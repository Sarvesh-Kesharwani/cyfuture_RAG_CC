from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from sqlalchemy.orm import sessionmaker
from backend.core.database import engine
from backend.core.models import Complaint
from uuid import uuid4
import re
import os
from dotenv import load_dotenv

load_dotenv()

# Set OpenAI API key (from environment variable)
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key
else:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

# Load knowledge base PDF
current_dir = os.path.dirname(os.path.abspath(__file__))
pdf_path = os.path.join(
    current_dir, "..", "knowledge_base", "customer_service_policies.pdf"
)
loader = PyPDFLoader(pdf_path)
documents = loader.load()

# Split text
text_splitter = CharacterTextSplitter(chunk_size=800, chunk_overlap=100)
docs = text_splitter.split_documents(documents)

# Embeddings and vector store
embeddings = OpenAIEmbeddings()
faiss_path = os.path.join(current_dir, "..", "embeddings", "faiss_index")

if not os.path.exists(faiss_path):
    os.makedirs(os.path.dirname(faiss_path), exist_ok=True)
    db = FAISS.from_documents(docs, embeddings)
    db.save_local(faiss_path)
else:
    db = FAISS.load_local(faiss_path, embeddings, allow_dangerous_deserialization=True)

# Memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# LLM
llm = ChatOpenAI(temperature=0)

# RAG chain
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm, retriever=db.as_retriever(), memory=memory
)

# DB session
SessionLocal = sessionmaker(bind=engine)

# Session dict to track complaint conversation state
session_data = {}


# Function to get chatbot response
def get_rag_response(user_input):
    response = ""

    # If user says 'file a complaint' — start complaint collection
    if "file a complaint" in user_input.lower():
        session_data["current_step"] = "name"
        response = "I'm sorry to hear that. Could you please provide your name?"
        return response

    # Sequential complaint details collection
    if "current_step" in session_data:
        step = session_data["current_step"]

        if step == "name":
            session_data["name"] = user_input
            session_data["current_step"] = "phone_number"
            return f"Thank you, {user_input}. May I have your phone number?"

        elif step == "phone_number":
            if re.match(r"^\d{10}$", user_input):
                session_data["phone_number"] = user_input
                session_data["current_step"] = "email"
                return "Got it. Please provide your email address."
            else:
                return "Please enter a valid 10-digit phone number."

        elif step == "email":
            if "@" in user_input and "." in user_input:
                session_data["email"] = user_input
                session_data["current_step"] = "complaint_details"
                return "Thanks. Could you describe your complaint?"
            else:
                return "Please enter a valid email address."

        elif step == "complaint_details":
            session_data["complaint_details"] = user_input
            complaint_id = str(uuid4())

            # Store to DB
            db_session = SessionLocal()
            new_complaint = Complaint(
                complaint_id=complaint_id,
                name=session_data["name"],
                phone_number=session_data["phone_number"],
                email=session_data["email"],
                complaint_details=session_data["complaint_details"],
            )
            db_session.add(new_complaint)
            db_session.commit()
            db_session.close()

            response = f"Your complaint has been registered with ID: {complaint_id}. You'll hear back soon."

            # Reset session state
            session_data.clear()
            return response

    # --- Enhanced complaint retrieval logic using LLM extraction ---
    db_session = SessionLocal()
    extracted = extract_complaint_query(user_input)
    complaint_id = extracted.get("complaint_id")
    email = extracted.get("email")
    name = extracted.get("name")

    if complaint_id:
        complaint = (
            db_session.query(Complaint)
            .filter(Complaint.complaint_id == complaint_id)
            .first()
        )
        db_session.close()
        if complaint:
            return (
                f"Complaint ID: {complaint.complaint_id}\n"
                f"Name: {complaint.name}\n"
                f"Phone: {complaint.phone_number}\n"
                f"Email: {complaint.email}\n"
                f"Details: {complaint.complaint_details}\n"
                f"Created At: {complaint.created_at}"
            )
        else:
            return f"No complaint found for ID: {complaint_id}."

    if email:
        complaints = db_session.query(Complaint).filter(Complaint.email == email).all()
        db_session.close()
        if complaints:
            return "\n\n".join(
                f"Complaint ID: {c.complaint_id}\n"
                f"Name: {c.name}\n"
                f"Phone: {c.phone_number}\n"
                f"Email: {c.email}\n"
                f"Details: {c.complaint_details}\n"
                f"Created At: {c.created_at}"
                for c in complaints
            )
        else:
            return f"No complaints found for email: {email}."

    if name:
        complaints = (
            db_session.query(Complaint).filter(Complaint.name.ilike(f"%{name}%")).all()
        )
        db_session.close()
        if complaints:
            return "\n\n".join(
                f"Complaint ID: {c.complaint_id}\n"
                f"Name: {c.name}\n"
                f"Phone: {c.phone_number}\n"
                f"Email: {c.email}\n"
                f"Details: {c.complaint_details}\n"
                f"Created At: {c.created_at}"
                for c in complaints
            )
        else:
            return f"No complaints found for name: {name}."

    db_session.close()
    # Fallback to KB RAG chain for general queries
    return qa_chain.run(user_input)


def extract_complaint_query(user_input):
    """
    Use the LLM to extract complaint_id, email, or name from the user's query.
    Returns a dict with possible keys: complaint_id, email, name.
    """
    extraction_prompt = (
        "Extract the complaint_id, email, or name from the following user query. "
        "Return ONLY a JSON object with keys 'complaint_id', 'email', and 'name'. "
        "If a value is not present, set it to null.\n"
        "Example:\n"
        "User query: Show me complaint details with id e7e0570c-2f9c-44de-a0b7-acaf1e682207\n"
        'JSON: {"complaint_id": "e7e0570c-2f9c-44de-a0b7-acaf1e682207", "email": null, "name": null}\n'
        "User query: Show complaints for john@example.com\n"
        'JSON: {"complaint_id": null, "email": "john@example.com", "name": null}\n'
        "User query: Show complaints for John Doe\n"
        'JSON: {"complaint_id": null, "email": null, "name": "John Doe"}\n'
        f"User query: {user_input}\n"
        "JSON:"
    )
    extraction_response = llm.invoke(extraction_prompt)
    import json

    # Log the LLM output for debugging
    print("LLM extraction response:", extraction_response)

    try:
        result = json.loads(extraction_response)
        return result
    except Exception:
        # Fallback: try to extract with regex if LLM fails
        complaint_id = None
        email = None
        name = None

        id_match = re.search(r"\b([a-f0-9\-]{36})\b", user_input)
        if id_match:
            complaint_id = id_match.group(1)
        email_match = re.search(
            r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", user_input
        )
        if email_match:
            email = email_match.group(1)
        # Try to extract name after "for" if present
        name_match = re.search(r"for\s+([A-Za-z ]+)$", user_input)
        if name_match:
            name = name_match.group(1).strip()
        return {"complaint_id": complaint_id, "email": email, "name": name}

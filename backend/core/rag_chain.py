from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
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
db = FAISS.from_documents(docs, embeddings)

# Memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# LLM
llm = ChatOpenAI(temperature=0)

# RAG chain
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm, retriever=db.as_retriever(), memory=memory
)


# Function to get chatbot response
def get_rag_response(user_input):
    result = qa_chain.run(user_input)
    return result

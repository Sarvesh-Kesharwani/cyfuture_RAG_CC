from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os

# Set your OpenAI API key (or environment variable)
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# 1️⃣ Load documents
loader = PyPDFLoader("knowledge_base/customer_service_policies.pdf")
documents = loader.load()

# 2️⃣ Split documents into chunks
text_splitter = CharacterTextSplitter(chunk_size=800, chunk_overlap=100)
docs = text_splitter.split_documents(documents)

# 3️⃣ Convert chunks into vector embeddings
embeddings = OpenAIEmbeddings()

# 4️⃣ Store embeddings in FAISS index
db = FAISS.from_documents(docs, embeddings)

# 5️⃣ Set up conversation memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# 6️⃣ Initialize Chat Model
llm = ChatOpenAI(temperature=0)

# 7️⃣ Build Conversational RAG Chain
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm, retriever=db.as_retriever(), memory=memory
)

# 8️⃣ Run interactive chatbot loop
print("📞 Customer Service Chatbot (type 'exit' to quit) 📞")
while True:
    query = input("\nUser: ")
    if query.lower() in ["exit", "quit"]:
        break
    result = qa_chain.run(query)
    print(f"Bot: {result}")

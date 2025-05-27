from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import complaints, chatbot  # import your route modules

app = FastAPI(
    title="RAG Customer Complaint Chatbot API",
    description="Backend API for complaint management and RAG-based chatbot.",
    version="1.0.0",
)

# Enable CORS so frontend (Streamlit) can talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for local dev; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route files
app.include_router(complaints.router)
app.include_router(chatbot.router)


# Health check route (optional)
@app.get("/")
def read_root():
    return {"message": "Backend API is running successfully."}

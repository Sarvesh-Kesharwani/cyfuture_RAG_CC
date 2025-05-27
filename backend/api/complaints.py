from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from backend.core import models, schemas, database
from uuid import uuid4

router = APIRouter()


# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/complaints", response_model=schemas.ComplaintIDResponse)
def create_complaint(complaint: schemas.ComplaintCreate):
    db = next(get_db())
    complaint_id = str(uuid4())

    new_complaint = models.Complaint(
        complaint_id=complaint_id,
        name=complaint.name,
        phone_number=complaint.phone_number,
        email=complaint.email,
        complaint_details=complaint.complaint_details,
    )

    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)
    db.close()

    return {"complaint_id": complaint_id, "message": "Complaint created successfully."}


@router.get("/complaints/{complaint_id}", response_model=schemas.ComplaintResponse)
def get_complaint(complaint_id: str):
    db = next(get_db())
    complaint = (
        db.query(models.Complaint)
        .filter(models.Complaint.complaint_id == complaint_id)
        .first()
    )
    db.close()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found.")

    return complaint

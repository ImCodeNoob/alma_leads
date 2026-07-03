import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.email_service import send_email
from app.models import Lead, LeadStatus, User
from app.schemas import LeadOut, LeadStatusUpdate
from app.security import get_current_user
from app.storage import save_resume

router = APIRouter(prefix="/api/leads", tags=["leads"])
logger = logging.getLogger("leads")


@router.post("", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
def create_lead(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Lead:
    resume_filename, resume_path = save_resume(resume)

    lead = Lead(
        first_name=first_name,
        last_name=last_name,
        email=email,
        resume_filename=resume_filename,
        resume_path=resume_path,
        status=LeadStatus.PENDING,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    try:
        send_email(
            to=lead.email,
            subject="We received your application",
            body=(
                f"Hi {lead.first_name},\n\n"
                "Thanks for submitting your information. An attorney will review "
                "your application and reach out shortly.\n\nBest,\nThe Team"
            ),
        )
    except Exception:
        logger.exception("Failed to send prospect confirmation email for lead %s", lead.id)

    attorney_emails = [row[0] for row in db.query(User.email).all()]
    for attorney_email in attorney_emails:
        try:
            send_email(
                to=attorney_email,
                subject="New lead submitted",
                body=(
                    f"A new lead was submitted:\n\n"
                    f"Name: {lead.first_name} {lead.last_name}\n"
                    f"Email: {lead.email}\n"
                    f"Lead ID: {lead.id}\n"
                ),
            )
        except Exception:
            logger.exception(
                "Failed to send lead notification to %s for lead %s", attorney_email, lead.id
            )

    return lead


@router.get("", response_model=list[LeadOut])
def list_leads(
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[Lead]:
    return db.query(Lead).order_by(Lead.created_at.desc()).all()


@router.patch("/{lead_id}/status", response_model=LeadOut)
def update_lead_status(
    lead_id: str,
    payload: LeadStatusUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> Lead:
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    if lead.status != LeadStatus.PENDING or payload.status != LeadStatus.REACHED_OUT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot transition lead from {lead.status.value} to {payload.status.value}",
        )

    lead.status = payload.status
    db.commit()
    db.refresh(lead)
    return lead


@router.get("/{lead_id}/resume")
def download_resume(
    lead_id: str,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> FileResponse:
    lead = db.get(Lead, lead_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return FileResponse(lead.resume_path, filename=lead.resume_filename)

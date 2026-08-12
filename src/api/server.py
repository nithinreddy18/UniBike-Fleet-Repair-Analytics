from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.database.session import SessionLocal
from src.database.models import Bike, WorkOrder, Inventory
from src.api.rag_chain import query_assistant
from src.core.config import settings
import pandas as pd
from typing import Optional

app = FastAPI(title="UniBike API")

# CORS setup for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Ticketing API ---
class TicketPayload(BaseModel):
    bike_id: int
    issue_type: str
    description: Optional[str] = ""


class LoginPayload(BaseModel):
    username: str
    password: str


@app.post("/api/login")
def login(payload: LoginPayload):
    if (
        payload.username == settings.gradio_admin_username
        and payload.password == settings.gradio_admin_password.get_secret_value()
    ):
        return {"token": "unibike-admin-token-valid"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.post("/api/tickets")
def submit_ticket(payload: TicketPayload, db: Session = Depends(get_db)):
    bike = db.query(Bike).filter(Bike.id == payload.bike_id).first()
    if not bike:
        # Auto-create the bike if it doesn't exist for a smoother UX
        bike = Bike(id=payload.bike_id, status="Available")
        db.add(bike)
        db.flush()  # Ensure bike has an ID for the work order

    existing_ticket = (
        db.query(WorkOrder)
        .filter(
            WorkOrder.bike_id == payload.bike_id,
            WorkOrder.issue_type == payload.issue_type,
            WorkOrder.status.in_(["Open", "In Progress"]),
        )
        .first()
    )

    if existing_ticket:
        raise HTTPException(
            status_code=400,
            detail=f"There is already an active ticket for '{payload.issue_type}' on Bike {payload.bike_id}.",
        )

    new_ticket = WorkOrder(
        bike_id=payload.bike_id,
        issue_type=payload.issue_type,
        description=payload.description,
        status="Open",
    )
    db.add(new_ticket)

    bike.status = "Out of Order"

    db.commit()
    return {
        "message": "Success! Ticket submitted.",
        "bike_id": payload.bike_id,
        "status": "Out of Order",
    }


class TicketUpdatePayload(BaseModel):
    status: str


@app.get("/api/tickets")
def get_tickets(db: Session = Depends(get_db)):
    tickets = db.query(WorkOrder).order_by(WorkOrder.created_at.desc()).all()
    return [
        {
            "id": t.id,
            "bike_id": t.bike_id,
            "issue_type": t.issue_type,
            "description": t.description,
            "status": t.status,
            "created_at": t.created_at,
        }
        for t in tickets
    ]


@app.patch("/api/tickets/{ticket_id}")
def update_ticket(
    ticket_id: int, payload: TicketUpdatePayload, db: Session = Depends(get_db)
):
    ticket = db.query(WorkOrder).filter(WorkOrder.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.status = payload.status
    if payload.status == "Resolved":
        ticket.resolved_at = pd.Timestamp.now(tz="UTC")

    db.commit()
    return {"message": "Status updated successfully", "status": ticket.status}


# --- RAG Assistant API ---
class ChatMessage(BaseModel):
    message: str


@app.post("/api/chat")
def chat(payload: ChatMessage):
    try:
        answer, docs = query_assistant(payload.message)
        sources = [doc.page_content for doc in docs]
        return {"answer": answer, "sources": sources}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e))


# --- KPI API ---
@app.get("/api/kpi")
def get_kpi_data(db: Session = Depends(get_db)):
    # Calculate MTTR
    resolved_wos = db.query(WorkOrder).filter(WorkOrder.status == "Resolved").all()
    mttr = 0
    if resolved_wos:
        resolved_df = pd.DataFrame([wo.__dict__ for wo in resolved_wos])
        if "created_at" in resolved_df.columns and "resolved_at" in resolved_df.columns:
            resolved_df["created_at"] = pd.to_datetime(
                resolved_df["created_at"], utc=True
            )
            resolved_df["resolved_at"] = pd.to_datetime(
                resolved_df["resolved_at"], utc=True
            )
            resolved_df["repair_time"] = (
                resolved_df["resolved_at"] - resolved_df["created_at"]
            ).dt.total_seconds() / 86400
            mttr = round(resolved_df["repair_time"].mean(), 1)

    # Open Tickets
    open_tickets = db.query(WorkOrder).filter(WorkOrder.status == "Open").count()

    # Missed SLAs (> 2 days)
    open_wos = db.query(WorkOrder).filter(WorkOrder.status == "Open").all()
    missed_slas = 0
    if open_wos:
        open_df = pd.DataFrame([wo.__dict__ for wo in open_wos])
        if "created_at" in open_df.columns:
            open_df["created_at"] = pd.to_datetime(open_df["created_at"], utc=True)
            now = pd.Timestamp.now(tz="UTC")
            missed_slas = len(
                open_df[(now - open_df["created_at"]).dt.total_seconds() / 86400 > 2]
            )

    # Status Distribution
    all_wos = db.query(WorkOrder).all()
    status_distribution = []
    if all_wos:
        df = pd.DataFrame([wo.__dict__ for wo in all_wos])
        status_counts = df["status"].value_counts().to_dict()
        for status, count in status_counts.items():
            status_distribution.append({"status": status, "count": count})

    # Inventory
    inventory = db.query(Inventory).all()
    inventory_data = [
        {
            "part_name": item.part_name,
            "quantity": item.quantity,
            "reorder_level": item.threshold,
        }
        for item in inventory
    ]

    return {
        "metrics": {
            "mttr": mttr,
            "open_tickets": open_tickets,
            "missed_slas": missed_slas,
        },
        "status_distribution": status_distribution,
        "inventory": inventory_data,
    }

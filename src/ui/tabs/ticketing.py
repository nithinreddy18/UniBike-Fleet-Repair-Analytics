import gradio as gr
from pydantic import BaseModel, ValidationError
from src.database.session import SessionLocal
from src.database.models import Bike, WorkOrder
from src.core.logger import logger


# Pydantic model for validation
class TicketPayload(BaseModel):
    bike_id: int
    issue_type: str
    description: str


def submit_ticket(bike_id_str, issue_type, description):
    try:
        # Pydantic Validation
        payload = TicketPayload(
            bike_id=int(bike_id_str) if bike_id_str else 0,
            issue_type=issue_type,
            description=description,
        )
    except ValidationError:
        gr.Warning("Validation Error: Please ensure all fields are correctly filled.")
        return
    except ValueError:
        gr.Warning("Invalid Bike ID.")
        return

    if not payload.issue_type:
        gr.Warning("Please select an issue type.")
        return

    db = SessionLocal()
    try:
        # Check if bike exists
        bike = db.query(Bike).filter(Bike.id == payload.bike_id).first()
        if not bike:
            gr.Error(f"Bike ID {payload.bike_id} not found in system.")
            return

        # Prevent duplicate active tickets
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
            gr.Info(
                f"There is already an active ticket for '{payload.issue_type}' on Bike {payload.bike_id}."
            )
            return

        # Create new ticket
        new_ticket = WorkOrder(
            bike_id=payload.bike_id,
            issue_type=payload.issue_type,
            description=payload.description,
            status="Open",
        )
        db.add(new_ticket)

        # Update bike status
        bike.status = "Out of Order"

        db.commit()
        logger.info(f"Created ticket for Bike {payload.bike_id} - {payload.issue_type}")
        gr.Info(
            f"Success! Ticket submitted for Bike {payload.bike_id}. Status updated to 'Out of Order'."
        )
        return

    except Exception as e:  # noqa: BLE001
        db.rollback()
        logger.error(f"Error submitting ticket: {e}")
        gr.Error("An error occurred while submitting the ticket.")
        return
    finally:
        db.close()


def create_ticketing_tab():
    with gr.Blocks() as tab:
        gr.Markdown("## 🚲 Report a Bike Issue")
        gr.Markdown(
            "Scan the QR code on your bike or manually enter the Bike ID below."
        )

        with gr.Row():
            bike_id_input = gr.Textbox(
                label="Bike ID", placeholder="e.g., 1", elem_id="bike-id-input"
            )

        with gr.Row():
            issue_dropdown = gr.Dropdown(
                choices=[
                    "Flat Tire",
                    "Broken Chain",
                    "Brakes Loose",
                    "Gears Skipping",
                    "Saddle Stolen",
                    "Other",
                ],
                label="Issue Type",
                elem_id="issue-type-input",
            )

        with gr.Row():
            desc_input = gr.Textbox(
                label="Description (Optional)", lines=3, elem_id="desc-input"
            )

        submit_btn = gr.Button(
            "Submit Ticket", variant="primary", elem_id="submit-ticket-btn"
        )

        submit_btn.click(
            fn=submit_ticket,
            inputs=[bike_id_input, issue_dropdown, desc_input],
            outputs=[],
        )

    return tab, bike_id_input

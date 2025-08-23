from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from datetime import datetime

def generate_gate_pass_pdf(workorder, file_path):
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    y = height - 30 * mm
    c.setFont("Helvetica-Bold", 18)
    c.drawString(30 * mm, y, "Gate Pass")
    y -= 15 * mm
    c.setFont("Helvetica", 12)
    c.drawString(30 * mm, y, f"Work Order ID: {workorder.id}")
    y -= 8 * mm
    c.drawString(30 * mm, y, f"Title: {workorder.title}")
    y -= 8 * mm
    c.drawString(30 * mm, y, f"Product: {workorder.product_name}")
    y -= 8 * mm
    c.drawString(30 * mm, y, f"Owner: {workorder.owner_name}")
    y -= 8 * mm
    c.drawString(30 * mm, y, f"Address: {workorder.address}")
    y -= 8 * mm
    c.drawString(30 * mm, y, f"Category: {workorder.category.name if workorder.category else ''}")
    y -= 8 * mm
    c.drawString(30 * mm, y, f"Priority: {workorder.priority.name if workorder.priority else ''}")
    y -= 8 * mm
    c.drawString(30 * mm, y, f"Assigned To: {workorder.assignee.full_name if workorder.assignee else ''}")
    y -= 8 * mm
    c.drawString(30 * mm, y, f"Estimated Hours: {workorder.estimated_hours}")
    y -= 8 * mm
    c.drawString(30 * mm, y, f"Cost Estimate: {workorder.cost_estimate}")
    y -= 8 * mm
    c.drawString(30 * mm, y, f"Due Date: {workorder.due_date.strftime('%Y-%m-%d') if workorder.due_date else ''}")
    y -= 8 * mm
    c.drawString(30 * mm, y, f"Created By: {workorder.creator.full_name if workorder.creator else ''}")
    y -= 8 * mm
    c.drawString(30 * mm, y, f"Created At: {workorder.created_at.strftime('%Y-%m-%d %H:%M') if workorder.created_at else ''}")
    y -= 12 * mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30 * mm, y, "Description:")
    y -= 8 * mm
    c.setFont("Helvetica", 11)
    text = c.beginText(30 * mm, y)
    for line in (workorder.description or '').splitlines():
        text.textLine(line)
    c.drawText(text)
    c.showPage()
    c.save()

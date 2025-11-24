import csv
import io
from typing import List
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from backend.db.models import Assessment, AssessmentResult


def generate_csv_report(assessment: Assessment, results: List[AssessmentResult]) -> str:
    """Generate CSV report for an assessment"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["AI Governance Assessment Report"])
    writer.writerow(["Assessment Title", assessment.title])
    writer.writerow(["Created", assessment.created_at.strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow(["Status", assessment.status])
    writer.writerow([])
    
    # Results
    writer.writerow(["Category", "Score", "Maturity Level", "Recommendations"])
    for result in results:
        writer.writerow([
            result.category,
            result.score,
            result.maturity_level,
            result.recommendations
        ])
    
    # Overall
    if results:
        overall_score = sum(r.score for r in results) // len(results)
        writer.writerow([])
        writer.writerow(["Overall Score", overall_score])
    
    return output.getvalue()


def generate_pdf_report(assessment: Assessment, results: List[AssessmentResult]) -> bytes:
    """Generate PDF report for an assessment"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
    )
    story.append(Paragraph("AI Governance Assessment Report", title_style))
    story.append(Spacer(1, 0.2 * inch))
    
    # Assessment Info
    info_data = [
        ["Assessment Title:", assessment.title],
        ["Created:", assessment.created_at.strftime("%Y-%m-%d %H:%M:%S")],
        ["Status:", assessment.status.upper()],
    ]
    if assessment.description:
        info_data.append(["Description:", assessment.description])
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # Results
    story.append(Paragraph("Assessment Results", styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))
    
    if results:
        # Results table
        results_data = [["Category", "Score", "Maturity Level"]]
        for result in results:
            results_data.append([
                result.category.replace("_", " ").title(),
                str(result.score),
                result.maturity_level.title()
            ])
        
        # Overall score
        overall_score = sum(r.score for r in results) // len(results)
        results_data.append(["OVERALL", str(overall_score), ""])
        
        results_table = Table(results_data, colWidths=[2.5*inch, 1*inch, 1.5*inch])
        results_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(results_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Recommendations
        story.append(Paragraph("Recommendations by Category", styles['Heading2']))
        story.append(Spacer(1, 0.2 * inch))
        
        for result in results:
            category_title = result.category.replace("_", " ").title()
            story.append(Paragraph(f"<b>{category_title}</b>", styles['Heading3']))
            story.append(Paragraph(result.recommendations or "No recommendations", styles['Normal']))
            story.append(Spacer(1, 0.15 * inch))
    else:
        story.append(Paragraph("No assessment results available.", styles['Normal']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

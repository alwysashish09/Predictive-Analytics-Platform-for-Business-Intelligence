"""Executive PDF Report Generator using ReportLab."""

import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ReportGenerator:
    def __init__(self, dataset: dict, model_run: dict, ai_insights: str = None):
        self.dataset = dataset
        self.model_run = model_run
        self.ai_insights = ai_insights
        self.styles = getSampleStyleSheet()
        self._add_custom_styles()

    def _add_custom_styles(self):
        """Add custom styles for the report."""
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor("#1e293b")
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor("#334155"),
            borderPadding=5,
        ))
        self.styles.add(ParagraphStyle(
            name='BodyTextCustom',
            parent=self.styles['BodyText'],
            fontSize=11,
            leading=14,
            spaceAfter=8,
            textColor=colors.HexColor("#475569")
        ))

    def _build_dataset_section(self) -> list:
        """Build the dataset overview section."""
        elements = []
        elements.append(Paragraph("Dataset Overview", self.styles['SectionHeader']))
        
        data = [
            ["Metric", "Value"],
            ["Dataset Name", self.dataset.get('name', 'N/A')],
            ["File Name", self.dataset.get('file_name', 'N/A')],
            ["Total Rows", f"{self.dataset.get('row_count', 0):,}"],
            ["Total Columns", str(self.dataset.get('column_count', 0))],
            ["Target Variable", self.dataset.get('target_column', 'N/A')],
        ]
        
        t = Table(data, colWidths=[200, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor("#334155")),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(t)
        elements.append(Spacer(1, 20))
        return elements

    def _build_model_section(self) -> list:
        """Build the model performance section."""
        elements = []
        elements.append(Paragraph("Model Performance", self.styles['SectionHeader']))
        
        metrics = self.model_run.get('metrics', {})
        
        data = [
            ["Metric", "Value"],
            ["Algorithm", self.model_run.get('model_type', 'N/A').replace('_', ' ').title()],
            ["Accuracy", f"{metrics.get('accuracy', 0) * 100:.2f}%"],
            ["F1 Score", f"{metrics.get('f1_score', 0) * 100:.2f}%"],
            ["Precision", f"{metrics.get('precision', 0) * 100:.2f}%"],
            ["Recall", f"{metrics.get('recall', 0) * 100:.2f}%"],
        ]
        
        t = Table(data, colWidths=[200, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor("#334155")),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(t)
        elements.append(Spacer(1, 20))
        return elements

    def _build_feature_importance(self) -> list:
        """Build the feature importance table."""
        elements = []
        fi = self.model_run.get('feature_importance', [])
        
        if not fi:
            return elements

        elements.append(Paragraph("Top Drivers (Feature Importance)", self.styles['SectionHeader']))
        
        data = [["Rank", "Feature", "Importance"]]
        for item in fi[:10]: # Top 10
            data.append([
                str(item.get('rank')),
                item.get('feature'),
                f"{item.get('importance', 0) * 100:.1f}%"
            ])
            
        t = Table(data, colWidths=[50, 250, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor("#334155")),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(t)
        elements.append(Spacer(1, 20))
        return elements

    def _build_ai_insights(self) -> list:
        """Add AI generated insights to the report."""
        elements = []
        if not self.ai_insights:
            return elements

        elements.append(PageBreak())
        elements.append(Paragraph("AI Executive Summary", self.styles['SectionHeader']))
        
        # Clean up markdown simple formatting for reportlab (e.g., replace ** with <b>)
        text = self.ai_insights.replace("**", "")
        text = text.replace("* ", "• ")
        
        # Split by newlines
        paragraphs = text.split("\n")
        for p in paragraphs:
            if p.strip():
                elements.append(Paragraph(p.strip(), self.styles['BodyTextCustom']))
                
        return elements

    def generate(self) -> io.BytesIO:
        """Generate the PDF and return it as an in-memory byte stream."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            rightMargin=72, 
            leftMargin=72, 
            topMargin=72, 
            bottomMargin=72
        )
        
        elements = []
        
        # Title
        elements.append(Paragraph("Predictive Analytics Executive Report", self.styles['ReportTitle']))
        elements.append(Spacer(1, 10))
        
        # Sections
        elements.extend(self._build_dataset_section())
        elements.extend(self._build_model_section())
        elements.extend(self._build_feature_importance())
        elements.extend(self._build_ai_insights())
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer

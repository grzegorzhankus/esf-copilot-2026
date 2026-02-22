from __future__ import annotations

from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from core.contracts import AnalysisResult


def export_to_pdf(result: AnalysisResult) -> bytes:
    """
    Export analysis result to PDF report with Polish character support.
    """
    # Register DejaVu fonts for Polish characters
    try:
        pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
        default_font = 'DejaVuSans'
        bold_font = 'DejaVuSans-Bold'
    except:
        # Fallback to Helvetica if DejaVu not available
        default_font = 'Helvetica'
        bold_font = 'Helvetica-Bold'

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=18,
    )

    # Container for the 'Flowable' objects
    elements = []

    # Define styles with Unicode font
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#4472C4'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName=bold_font,
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#4472C4'),
        spaceAfter=12,
        spaceBefore=12,
        fontName=bold_font,
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=default_font,
        fontSize=10,
    )
    small_style = ParagraphStyle(
        'CustomSmall',
        parent=styles['Normal'],
        fontName=default_font,
        fontSize=8,
    )

    # Title
    title = Paragraph("e-SF Copilot<br/>Financial Analysis Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2 * inch))

    # Metadata Section
    elements.append(Paragraph("File Information", heading_style))

    # Use Paragraphs for long text fields (Schema ID)
    metadata_data = [
        ["Filename:", Paragraph(result.metadata.filename, small_style)],
        ["Schema ID:", Paragraph(result.metadata.schema_id, small_style)],
        ["Schema Slug:", Paragraph(result.metadata.schema_id_slug, small_style)],
        ["File Size:", f"{result.metadata.file_size_bytes:,} bytes"],
        ["Analyzed At:", result.metadata.analyzed_at_utc],
    ]

    metadata_table = Table(metadata_data, colWidths=[1.5*inch, 4.5*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E7E6E6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), bold_font),
        ('FONTNAME', (0, 0), (-1, -1), default_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(metadata_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Coverage Section
    elements.append(Paragraph("Coverage", heading_style))
    coverage_data = [
        ["Metrics Covered:", f"{result.coverage.percent}%"],
        ["Present:", str(len(result.coverage.present))],
        ["Missing:", str(len(result.coverage.missing))],
    ]
    coverage_table = Table(coverage_data, colWidths=[1.5*inch, 4.5*inch])
    coverage_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E7E6E6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), bold_font),
        ('FONTNAME', (0, 0), (-1, -1), default_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(coverage_table)
    elements.append(Spacer(1, 0.3 * inch))

    # Base Metrics Section
    if result.metrics_base:
        elements.append(Paragraph("Base Metrics", heading_style))

        metrics_data = [["Key", "Value", "Unit"]]
        for m in result.metrics_base:
            value_str = f"{m.value:,.2f}" if m.value is not None else "N/A"
            metrics_data.append([m.key, value_str, m.unit])

        metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), bold_font),
            ('FONTNAME', (0, 1), (-1, -1), default_font),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F2F2')]),
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 0.3 * inch))

    # KPIs Section
    if result.kpis:
        elements.append(PageBreak())
        elements.append(Paragraph("Financial KPIs", heading_style))

        # Group by category
        categories = {}
        for kpi in result.kpis:
            if kpi.category not in categories:
                categories[kpi.category] = []
            categories[kpi.category].append(kpi)

        for category, kpis in sorted(categories.items()):
            elements.append(Paragraph(f"<b>{category}</b>", normal_style))
            elements.append(Spacer(1, 0.1 * inch))

            kpi_data = [["KPI", "Value", "Interpretation"]]
            for kpi in kpis:
                # Add space between value and unit
                if kpi.value is not None:
                    # Format value with proper spacing
                    value_str = f"{kpi.value:.2f} {kpi.unit}" if kpi.unit else f"{kpi.value:.2f}"
                else:
                    value_str = "N/A"

                # Use Paragraph for interpretation to allow word wrap
                interp_para = Paragraph(kpi.interpretation, small_style)
                kpi_data.append([kpi.name, value_str, interp_para])

            kpi_table = Table(kpi_data, colWidths=[1.8*inch, 1.2*inch, 3*inch])
            kpi_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#70AD47')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), bold_font),
                ('FONTNAME', (0, 1), (1, -1), default_font),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F2F2F2')]),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(kpi_table)
            elements.append(Spacer(1, 0.2 * inch))

    # Red Flags Section
    if result.red_flags:
        elements.append(PageBreak())
        elements.append(Paragraph("Red Flags Analysis", heading_style))

        detected_flags = [f for f in result.red_flags if f.detected]

        if detected_flags:
            summary_text = f"<b>Warning:</b> {len(detected_flags)} of {len(result.red_flags)} red flags detected!"
            elements.append(Paragraph(summary_text, normal_style))
            elements.append(Spacer(1, 0.2 * inch))

            # Count by severity
            high_count = len([f for f in detected_flags if f.severity == "high"])
            medium_count = len([f for f in detected_flags if f.severity == "medium"])
            low_count = len([f for f in detected_flags if f.severity == "low"])

            severity_data = [
                ["Severity", "Count"],
                ["High", str(high_count)],
                ["Medium", str(medium_count)],
                ["Low", str(low_count)],
            ]

            severity_table = Table(severity_data, colWidths=[2*inch, 1*inch])
            severity_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), bold_font),
                ('FONTNAME', (0, 1), (-1, -1), default_font),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            elements.append(severity_table)
            elements.append(Spacer(1, 0.3 * inch))

            # Display detected flags
            for severity in ["high", "medium", "low"]:
                severity_flags = [f for f in detected_flags if f.severity == severity]
                if severity_flags:
                    elements.append(Paragraph(f"<b>{severity.upper()} Severity Flags</b>", normal_style))
                    elements.append(Spacer(1, 0.1 * inch))

                    for flag in severity_flags:
                        # Use Paragraphs for text wrapping
                        flag_data = [
                            ["Title:", Paragraph(flag.title, small_style)],
                            ["Description:", Paragraph(flag.description, small_style)],
                            ["Details:", Paragraph(flag.details, small_style)],
                        ]

                        flag_table = Table(flag_data, colWidths=[1.5*inch, 4.5*inch])

                        # Color based on severity
                        bg_color = colors.HexColor('#FFC7CE') if severity == "high" else \
                                   colors.HexColor('#FFEB9C') if severity == "medium" else \
                                   colors.HexColor('#FFF2CC')

                        flag_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (0, -1), bold_font),
                            ('FONTNAME', (1, 0), (1, -1), default_font),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                            ('TOPPADDING', (0, 0), (-1, -1), 8),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ]))
                        elements.append(flag_table)
                        elements.append(Spacer(1, 0.15 * inch))
        else:
            elements.append(Paragraph(f"<b>Good News:</b> No red flags detected! All {len(result.red_flags)} checks passed.", normal_style))

    # Footer
    elements.append(Spacer(1, 0.5 * inch))
    footer_text = f"<i>Generated by e-SF Copilot on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
    elements.append(Paragraph(footer_text, normal_style))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

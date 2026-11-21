"""
Feature 3: Fraud Investigation Assistant - PDF Report Generator.
Generates an investigation dossier PDF using ReportLab
summarizing case evidence, AI explanations, and regulatory sign-offs.
"""

from typing import Dict, Any, Optional
import io
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class InvestigationReportGenerator:
    """Generates official multi-bank fraud investigation dossiers in PDF format."""

    def generate_case_pdf(self, case: Dict[str, Any]) -> bytes:
        """
        Builds a multi-page PDF document for a specific investigation case.
        Returns the raw PDF bytes.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
        )

        styles = getSampleStyleSheet()

        # Custom typography styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=20,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=colors.HexColor("#2563EB"),
            spaceAfter=14,
        )
        h2_style = ParagraphStyle(
            "SectionH2",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=colors.HexColor("#1E293B"),
            spaceBefore=12,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "BodyDark",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            textColor=colors.HexColor("#334155"),
            leading=13,
            spaceAfter=6,
        )
        callout_style = ParagraphStyle(
            "Callout",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            textColor=colors.HexColor("#1E3A8A"),
            leading=12,
        )

        elements = []

        # 1. Header Banner
        elements.append(Paragraph("RINGTRACE AI 🛡️", title_style))
        elements.append(Paragraph("Cross-Bank Mule Ring Investigation Dossier", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#CBD5E1"), spaceAfter=12))

        # 2. Case Overview Table
        vol = case.get("total_volume", 0.0)
        vol_str = f"Rs. {vol:,.2f}" if isinstance(vol, (int, float)) else str(vol)
        banks = ", ".join(case.get("banks_involved", ["Bank A", "Bank B", "Bank C"]))

        case_info_data = [
            [
                Paragraph(f"<b>Case ID:</b> {case.get('case_id')}", body_style),
                Paragraph(f"<b>Risk Score:</b> {case.get('risk_score', 92)}/100", body_style),
            ],
            [
                Paragraph(f"<b>Investigation Status:</b> {case.get('status', 'Pending')}", body_style),
                Paragraph(f"<b>Risk Tier:</b> {case.get('risk_tier', 'HIGH')}", body_style),
            ],
            [
                Paragraph(f"<b>Associated Banks:</b> {banks}", body_style),
                Paragraph(f"<b>Connected Accounts:</b> {case.get('connected_accounts_count', 5)}", body_style),
            ],
            [
                Paragraph(f"<b>Total Volume:</b> {vol_str}", body_style),
                Paragraph(f"<b>Transactions Count:</b> {case.get('transactions_count', 18)}", body_style),
            ],
        ]

        t_info = Table(case_info_data, colWidths=[260, 260])
        t_info.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(t_info)
        elements.append(Spacer(1, 10))

        # 3. AI-Generated Case Summary
        elements.append(Paragraph("AI-Generated Case Summary", h2_style))
        ai_summary = case.get(
            "ai_summary",
            "Multiple accounts across participating institutions exhibit coordinated rapid pass-through and circular transfer patterns consistent with money mule activity.",
        )
        elements.append(Paragraph(ai_summary, body_style))
        elements.append(Spacer(1, 8))

        # 4. Detected Transaction Patterns & Member Accounts
        elements.append(Paragraph("Mule Ring Account Topology", h2_style))
        members = case.get("member_accounts", [])
        patterns = case.get("detected_patterns", ["RAPID_PASS_THROUGH", "CIRCULAR_LAYERING"])

        members_str = ", ".join(members[:10]) if members else "None recorded"
        patterns_str = ", ".join(patterns) if patterns else "Standard mule ring"

        ring_data = [
            [Paragraph("<b>Suspect Accounts:</b>", body_style), Paragraph(members_str, body_style)],
            [Paragraph("<b>Detected Patterns:</b>", body_style), Paragraph(patterns_str, body_style)],
        ]
        t_ring = Table(ring_data, colWidths=[130, 390])
        t_ring.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_ring)
        elements.append(Spacer(1, 10))

        # 5. Ethical Safeguards & Compliance Sign-off Block
        elements.append(Paragraph("Regulatory Compliance & Decision Sign-Off", h2_style))
        elements.append(Paragraph(
            "<b>Safeguard Notice:</b> Automated account freezes are disabled. Final disposition "
            "requires compliance officer review, dual-institution sign-off, and SAR filing documentation.",
            callout_style,
        ))
        elements.append(Spacer(1, 12))

        signoff_data = [
            [
                Paragraph("<b>Investigator Signature:</b> ___________________________", body_style),
                Paragraph("<b>Date:</b> ______________", body_style),
            ],
            [
                Paragraph("<b>Supervisor Approval:</b> ___________________________", body_style),
                Paragraph("<b>Disposition:</b> [  ] Confirmed  [  ] Cleared", body_style),
            ],
        ]
        t_sign = Table(signoff_data, colWidths=[360, 160])
        t_sign.setStyle(TableStyle([
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(t_sign)

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from datetime import datetime
import io

TMH_DARK = colors.HexColor("#1a1a1a")
TMH_GREY = colors.HexColor("#555555")
TMH_RULE = colors.HexColor("#cccccc")
TMH_TABLE_HEADER_BG = colors.HexColor("#f2f2f2")

PAGE_W, PAGE_H = A4
MARGIN = 20 * mm


def _styles():
    base = getSampleStyleSheet()

    def s(name, **kw):
        return ParagraphStyle(name, **kw)

    return {
        "header_brand": s("HeaderBrand", fontSize=8, textColor=TMH_DARK,
                          fontName="Helvetica-Bold", leading=10),
        "header_doc":   s("HeaderDoc",   fontSize=8, textColor=TMH_GREY,
                          fontName="Helvetica", leading=10),
        "title":        s("Title",       fontSize=18, textColor=TMH_DARK,
                          fontName="Helvetica-Bold", leading=22, spaceAfter=2),
        "subtitle":     s("Subtitle",    fontSize=9,  textColor=TMH_GREY,
                          fontName="Helvetica", leading=12, spaceAfter=8),
        "section":      s("Section",     fontSize=11, textColor=TMH_DARK,
                          fontName="Helvetica-Bold", leading=14,
                          spaceBefore=14, spaceAfter=4),
        "body":         s("Body",        fontSize=9,  textColor=TMH_DARK,
                          fontName="Helvetica", leading=13, spaceAfter=6),
        "bullet":       s("Bullet",      fontSize=9,  textColor=TMH_DARK,
                          fontName="Helvetica", leading=13, spaceAfter=4,
                          leftIndent=12, bulletIndent=0),
        "table_label":  s("TLabel",      fontSize=9,  textColor=TMH_DARK,
                          fontName="Helvetica-Bold", leading=12),
        "table_value":  s("TValue",      fontSize=9,  textColor=TMH_DARK,
                          fontName="Helvetica", leading=12),
        "footer_left":  s("FooterL",     fontSize=7.5, textColor=TMH_GREY,
                          fontName="Helvetica", leading=10),
        "footer_bold":  s("FooterB",     fontSize=7.5, textColor=TMH_DARK,
                          fontName="Helvetica-Bold", leading=10),
    }


def _header_footer(canvas, doc, client_name, address):
    canvas.saveState()
    st = _styles()
    w = PAGE_W - 2 * MARGIN

    # ── Header ──────────────────────────────────────────────
    y_top = PAGE_H - 12 * mm
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(TMH_DARK)
    canvas.drawString(MARGIN, y_top, "TAS MANUFACTURED HOUSING")
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(TMH_GREY)
    canvas.drawString(MARGIN + 120, y_top, "|  Designer Briefing Document")
    canvas.setStrokeColor(TMH_RULE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, y_top - 3 * mm, MARGIN + w, y_top - 3 * mm)

    # ── Footer ───────────────────────────────────────────────
    y_foot = 12 * mm
    canvas.line(MARGIN, y_foot + 4 * mm, MARGIN + w, y_foot + 4 * mm)

    is_last = doc.page == doc._pageCount if hasattr(doc, "_pageCount") else False

    if doc.page == getattr(doc, "_total_pages", 99):
        canvas.setFont("Helvetica-Bold", 7.5)
        canvas.setFillColor(TMH_DARK)
        canvas.drawString(MARGIN, y_foot + 1 * mm,
                          "INTERNAL DOCUMENT - NOT FOR CLIENT DISTRIBUTION")
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(TMH_GREY)
        canvas.drawString(MARGIN, y_foot - 3 * mm,
                          "TAS Manufactured Housing  |  admin@tasmanufacturedhousing.com.au")
    else:
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(TMH_GREY)
        page_str = f"Page {doc.page} of 3      Confidential - Internal Use Only"
        canvas.drawString(MARGIN, y_foot + 1 * mm, page_str)

    canvas.restoreState()


def _two_col_table(data, st):
    col_w = [(PAGE_W - 2 * MARGIN) * 0.32,
             (PAGE_W - 2 * MARGIN) * 0.68]
    rows = [[Paragraph(label, st["table_label"]),
             Paragraph(value, st["table_value"])]
            for label, value in data]
    t = Table(rows, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX",        (0, 0), (-1, -1), 0.5, TMH_RULE),
        ("INNERGRID",  (0, 0), (-1, -1), 0.5, TMH_RULE),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def _actions_table(actions, st):
    col_w = [(PAGE_W - 2 * MARGIN) * 0.55,
             (PAGE_W - 2 * MARGIN) * 0.22,
             (PAGE_W - 2 * MARGIN) * 0.23]
    header = [Paragraph("Item", st["table_label"]),
              Paragraph("Owner", st["table_label"]),
              Paragraph("Status", st["table_label"])]
    rows = [header] + [
        [Paragraph(a.get("item", ""), st["table_value"]),
         Paragraph(a.get("owner", ""), st["table_value"]),
         Paragraph(a.get("status", ""), st["table_value"])]
        for a in actions
    ]
    t = Table(rows, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TMH_TABLE_HEADER_BG),
        ("BOX",        (0, 0), (-1, -1), 0.5, TMH_RULE),
        ("INNERGRID",  (0, 0), (-1, -1), 0.5, TMH_RULE),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def generate_brief_pdf(brief: dict) -> bytes:
    """
    brief dict keys:
      client_names, client_contact, site_address, project_stage,
      invoice_status, document_date,
      project_description (str),
      design_summary (list of [label, value]),
      intended_use_notes (list of str bullets),
      actions (list of {item, owner, status}),
      notes (str),
    """
    buf = io.BytesIO()
    st = _styles()

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=20 * mm, bottomMargin=20 * mm,
    )

    client_name = brief.get("client_names", "")
    address = brief.get("site_address", "")
    date_str = brief.get("document_date", datetime.today().strftime("%-d %B %Y"))

    def on_page(canvas, doc):
        _header_footer(canvas, doc, client_name, address)

    story = []

    # ── Title block ─────────────────────────────────────────
    surname = client_name.split()[-1] if client_name else "Client"
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Designer Briefing Document", st["title"]))
    story.append(Paragraph(
        f"{surname} Residence  |  {address}  |  Prepared for Matthew Purves",
        st["subtitle"]
    ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=TMH_RULE))
    story.append(Spacer(1, 4 * mm))

    # ── 1. Project Overview ──────────────────────────────────
    story.append(Paragraph("1. Project Overview", st["section"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=TMH_RULE))
    story.append(Spacer(1, 2 * mm))
    overview_data = [
        ("Client Names",    brief.get("client_names", "")),
        ("Client Contact",  brief.get("client_contact", "")),
        ("Site Address",    address),
        ("TMH Contact",     "Pearce  |  admin@tasmanufacturedhousing.com.au"),
        ("Designer",        "Matthew Purves"),
        ("Document Date",   date_str),
        ("Project Stage",   brief.get("project_stage", "")),
        ("Invoice Status",  brief.get("invoice_status", "")),
    ]
    story.append(_two_col_table(overview_data, st))
    story.append(Spacer(1, 4 * mm))

    # ── 2. Project Description ───────────────────────────────
    story.append(Paragraph("2. Project Description", st["section"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=TMH_RULE))
    story.append(Spacer(1, 2 * mm))
    for para in brief.get("project_description", "").split("\n\n"):
        if para.strip():
            story.append(Paragraph(para.strip(), st["body"]))

    # ── 3. Design & Product Summary ──────────────────────────
    story.append(Paragraph("3. Design &amp; Product Summary", st["section"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=TMH_RULE))
    story.append(Spacer(1, 2 * mm))
    story.append(_two_col_table(brief.get("design_summary", []), st))
    story.append(Spacer(1, 4 * mm))

    # ── 4. Intended Use Notes ────────────────────────────────
    story.append(Paragraph("4. Intended Use Notes", st["section"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=TMH_RULE))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        "The following points should be considered in the design process:", st["body"]
    ))
    for bullet in brief.get("intended_use_notes", []):
        story.append(Paragraph(f"• {bullet}", st["bullet"]))

    story.append(PageBreak())

    # ── 5. Outstanding Items & Actions ──────────────────────
    story.append(Paragraph("5. Outstanding Items &amp; Actions", st["section"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=TMH_RULE))
    story.append(Spacer(1, 2 * mm))
    story.append(_actions_table(brief.get("actions", []), st))
    story.append(Spacer(1, 4 * mm))

    # ── 6. Notes ─────────────────────────────────────────────
    story.append(Paragraph("6. Notes", st["section"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=TMH_RULE))
    story.append(Spacer(1, 2 * mm))
    for para in brief.get("notes", "").split("\n\n"):
        if para.strip():
            story.append(Paragraph(para.strip(), st["body"]))

    story.append(PageBreak())

    # ── 7. Site Photos ───────────────────────────────────────
    story.append(Paragraph("7. Site Photos", st["section"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=TMH_RULE))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        f"Photos taken on-site at {address}, {date_str}.", st["body"]
    ))
    story.append(Spacer(1, 4 * mm))

    # 2x2 placeholder grid
    cell_w = (PAGE_W - 2 * MARGIN - 4 * mm) / 2
    cell_h = 55 * mm
    placeholder_style = ParagraphStyle(
        "ph", fontSize=8, textColor=TMH_GREY,
        fontName="Helvetica", alignment=TA_CENTER
    )
    photo_cell = Paragraph("Photo to be added", placeholder_style)
    photo_data = [[photo_cell, photo_cell], [photo_cell, photo_cell]]
    photo_table = Table(photo_data, colWidths=[cell_w, cell_w],
                        rowHeights=[cell_h, cell_h])
    photo_table.setStyle(TableStyle([
        ("BOX",       (0, 0), (-1, -1), 0.5, TMH_RULE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, TMH_RULE),
        ("VALIGN",    (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND",(0, 0), (-1, -1), colors.HexColor("#f7f7f7")),
    ]))
    story.append(photo_table)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    return buf.getvalue()

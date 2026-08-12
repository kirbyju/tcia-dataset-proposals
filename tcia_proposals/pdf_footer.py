import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


FOOTER_BASELINE_Y = 35
FOOTER_LINE_Y = 46.4
FOOTER_CENTER_X = letter[0] / 2
FOOTER_VERSION = "TCIA Data Submission Agreement (v. 20220914)"


def draw_dsa_footer(pdf_canvas, page_number, total_pages, *, include_base=True):
    """Draw a DSA footer using the geometry of the agreement template."""
    pdf_canvas.saveState()
    pdf_canvas.setFillColor(colors.black)
    pdf_canvas.setStrokeColor(colors.black)
    pdf_canvas.setFont("Helvetica", 8)

    if include_base:
        pdf_canvas.setLineWidth(0.48)
        pdf_canvas.line(70.5, FOOTER_LINE_Y, 541.5, FOOTER_LINE_Y)
        pdf_canvas.drawString(72, FOOTER_BASELINE_Y, FOOTER_VERSION)

    pdf_canvas.drawCentredString(
        FOOTER_CENTER_X,
        FOOTER_BASELINE_Y,
        f"Page {page_number} of {total_pages}",
    )
    pdf_canvas.restoreState()


def replace_dsa_page_number(page, page_number, total_pages):
    """Cover a template page's fixed page count and overlay the final count."""
    overlay_buffer = io.BytesIO()
    overlay = canvas.Canvas(overlay_buffer, pagesize=letter)
    overlay.setFillColor(colors.white)
    overlay.rect(270, 28, 72, 15, fill=1, stroke=0)
    draw_dsa_footer(
        overlay,
        page_number,
        total_pages,
        include_base=False,
    )
    overlay.showPage()
    overlay.save()
    overlay_buffer.seek(0)

    # Imported here to keep the footer drawing helper usable by ReportLab alone.
    import PyPDF2

    overlay_page = PyPDF2.PdfReader(overlay_buffer).pages[0]
    page.merge_page(overlay_page)
    return page

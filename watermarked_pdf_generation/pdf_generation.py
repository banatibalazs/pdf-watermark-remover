from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from datetime import datetime
import os
from io import BytesIO
from PIL import Image, ImageDraw
import random

def create_gradient_background(canvas_obj, width, height, start_color, end_color):
    """Create a gradient background transition between two colors."""
    canvas_obj.saveState()

    # Number of steps for smooth gradient
    steps = 100

    # Calculate color increments
    r1, g1, b1 = start_color.red, start_color.green, start_color.blue
    r2, g2, b2 = end_color.red, end_color.green, end_color.blue

    r_step = (r2 - r1) / steps
    g_step = (g2 - g1) / steps
    b_step = (b2 - b1) / steps

    # Draw gradient rectangles
    rect_height = height / steps

    for i in range(steps):
        # Calculate current color
        current_r = r1 + (r_step * i)
        current_g = g1 + (g_step * i)
        current_b = b1 + (b_step * i)

        # Set color and draw rectangle
        canvas_obj.setFillColorRGB(current_r, current_g, current_b)
        canvas_obj.rect(0, height - (i + 1) * rect_height, width, rect_height, fill=1, stroke=0)

    canvas_obj.restoreState()


def create_sample_image(width=200, height=150, color="blue", text="Sample"):
    """Create a simple sample image with background using PIL."""
    # Create image with gradient or pattern background
    img = Image.new('RGB', (width, height), color=color)
    draw = ImageDraw.Draw(img)

    # Add some pattern/texture
    for i in range(0, width, 20):
        for j in range(0, height, 20):
            draw.rectangle([i, j, i + 10, j + 10], fill=(255, 255, 255, 50))

    # Add border
    draw.rectangle([0, 0, width - 1, height - 1], outline="darkblue", width=3)

    # Add text with background
    text_bbox = draw.textbbox((0, 0), text)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2

    # Text background rectangle
    draw.rectangle([text_x - 5, text_y - 5, text_x + text_width + 5, text_y + text_height + 5], fill="white")
    draw.text((text_x, text_y), text, fill="black")

    # Save to BytesIO for reportlab
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    return ImageReader(img_buffer)


def draw_text_with_background(canvas_obj, x, y, text, font_size=11, bg_color=colors.lightyellow,
                              text_color=colors.black, width=None):
    """Draw text with a colored background rectangle."""
    canvas_obj.saveState()

    # Set font to measure text
    canvas_obj.setFont("Helvetica", font_size)

    if width:
        # For multi-line text blocks
        text_height = font_size + 8
        # Draw background rectangle
        canvas_obj.setFillColor(bg_color)
        canvas_obj.rect(x - 5, y - 5, width + 10, text_height, fill=1, stroke=0)

        # Draw text - fix the slice index
        canvas_obj.setFillColor(text_color)
        char_limit = int(width // 8)  # Convert to integer
        canvas_obj.drawString(x, y, text[:char_limit])
    else:
        text_width = canvas_obj.stringWidth(text, "Helvetica", font_size)
        text_height = font_size + 4

        # Draw background rectangle
        canvas_obj.setFillColor(bg_color)
        canvas_obj.rect(x - 2, y - 2, text_width + 4, text_height, fill=1, stroke=0)

        # Draw text
        canvas_obj.setFillColor(text_color)
        canvas_obj.drawString(x, y, text)

    canvas_obj.restoreState()
    return text_height


def create_watermarked_pdf(filename="watermarked_document.pdf", num_pages=30):
    """
    Generate a PDF with structured layout, organized text and gradient backgrounds.

    Args:
        filename (str): Output PDF filename
        num_pages (int): Number of pages to generate
    """
    # Create canvas object
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Sample text content (keep existing lorem_text array)
    lorem_text = [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
        "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
        "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
        "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium totam rem.",
        "Totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt.",
        "Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni.",
        "At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti.",
        "Et harum quidem rerum facilis est et expedita distinctio nam libero tempore cum soluta nobis est eligendi.",
        "Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates."
    ]

    # Gradient color pairs for backgrounds
    gradient_colors = [
        (colors.lightblue, colors.white),
        (colors.lightgreen, colors.lightyellow),
        (colors.lightpink, colors.lightcyan),
        (colors.lavender, colors.lightgrey),
        (colors.mistyrose, colors.honeydew),
        (colors.lightcyan, colors.lightblue),
        (colors.lightyellow, colors.lightgreen),
        (colors.lightgrey, colors.lightpink),
        (colors.honeydew, colors.lavender),
        (colors.white, colors.lightcyan)
    ]

    image_colors = ["lightblue", "lightgreen", "lightcoral", "lightyellow", "lightpink", "lightgray"]

    for page_num in range(1, num_pages + 1):
        # Set random seed for consistent variety per page
        random.seed(page_num)

        # Add gradient background - replace the simple background
        start_color, end_color = gradient_colors[page_num % len(gradient_colors)]
        create_gradient_background(c, width, height, start_color, end_color)

        # Rest of your existing code remains the same...
        # Define layout margins
        left_margin = 60
        right_margin = width - 60
        top_margin = height - 60
        bottom_margin = 80

        # Add header section with background
        header_height = 40
        c.setFillColor(colors.darkblue)
        c.rect(0, top_margin, width, header_height, fill=1, stroke=0)

        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(left_margin, top_margin + 15, f"Structured Document - Page {page_num}")
        c.setFont("Helvetica", 10)
        c.drawString(right_margin - 150, top_margin + 15, f"Generated: {datetime.now().strftime('%Y-%m-%d')}")

        # Current Y position for content
        current_y = top_margin - 20

        # Section 1: Introduction with ordered layout
        current_y -= 30
        c.setFillColor(colors.darkgreen)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(left_margin, current_y, "1. Introduction")

        current_y -= 25
        # Text block with background
        text_content = lorem_text[page_num % len(lorem_text)]
        for line_num in range(3):
            line_text = text_content[line_num * 60:(line_num + 1) * 60] + "..."
            draw_text_with_background(c, left_margin, current_y, line_text,
                                      font_size=11, bg_color=colors.lightyellow, width=400)
            current_y -= 20

        # Add image in structured position (right side)
        img_width, img_height = 140, 100
        img_x = right_margin - img_width - 20
        img_y = current_y - img_height - 10

        try:
            img_color = random.choice(image_colors)
            sample_img = create_sample_image(img_width, img_height, img_color, f"Figure {page_num}.1")
            c.drawImage(sample_img, img_x, img_y, width=img_width, height=img_height)
        except:
            c.setFillColor(colors.lightblue)
            c.rect(img_x, img_y, img_width, img_height, fill=1, stroke=1)
            c.setFillColor(colors.black)
            c.drawString(img_x + 10, img_y + img_height // 2, f"Figure {page_num}.1")

        current_y = img_y - 30

        # Section 2: Analysis with structured layout
        c.setFillColor(colors.darkgreen)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(left_margin, current_y, "2. Analysis")

        current_y -= 25
        # Two column layout for text
        col_width = (right_margin - left_margin - 20) // 2

        # Left column
        for i in range(8):
            line_text = lorem_text[(page_num + i + 2) % len(lorem_text)][:50] + "..."
            draw_text_with_background(c, left_margin, current_y, line_text,
                                      font_size=10, bg_color=colors.lightcyan, width=col_width)
            current_y -= 18

        # Right column
        current_y += 82  # Reset for right column
        for i in range(8):
            line_text = lorem_text[(page_num + i + 5) % len(lorem_text)][:50] + "..."
            draw_text_with_background(c, left_margin + col_width + 20, current_y, line_text,
                                      font_size=10, bg_color=colors.lightpink, width=col_width)
            current_y -= 18

        current_y -= 20

        # Section 3: Data with chart
        c.setFillColor(colors.darkgreen)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(left_margin, current_y, "3. Data Visualization")

        current_y -= 35

        # Chart/image centered
        chart_width, chart_height = 200, 120
        chart_x = (width - chart_width) // 2

        try:
            chart_color = random.choice(image_colors)
            chart_img = create_sample_image(chart_width, chart_height, chart_color, f"Chart {page_num}")
            c.drawImage(chart_img, chart_x, current_y - chart_height, width=chart_width, height=chart_height)
        except:
            c.setFillColor(colors.lightgreen)
            c.rect(chart_x, current_y - chart_height, chart_width, chart_height, fill=1, stroke=1)
            c.setFillColor(colors.black)
            c.drawString(chart_x + 70, current_y - chart_height // 2, f"Chart {page_num}")

        current_y -= chart_height + 20

        # Summary section
        c.setFillColor(colors.darkgreen)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(left_margin, current_y, "4. Summary")

        current_y -= 25
        summary_text = lorem_text[(page_num + 7) % len(lorem_text)]
        draw_text_with_background(c, left_margin, current_y, summary_text[:80] + "...",
                                  font_size=11, bg_color=colors.lightgreen, width=400)

        # Add footer with structured layout
        footer_height = 30
        c.setFillColor(colors.lightgrey)
        c.rect(0, 0, width, footer_height, fill=1, stroke=0)

        c.setFillColor(colors.black)
        c.setFont("Helvetica", 9)
        c.drawString(left_margin, 15, "Confidential Document - Structured Layout")
        c.drawString(right_margin - 120, 15, f"Page {page_num} of {num_pages}")
        c.drawString((width - 100) // 2, 15, f"Doc-ID: STR{page_num:03d}")

        # Add watermark
        add_watermark(c, width, height)

        # Create new page (except for last page)
        if page_num < num_pages:
            c.showPage()

    # Save the PDF
    c.save()
    print(f"Generated {num_pages}-page PDF with structured layout and backgrounds: {filename}")


def add_watermark(canvas_obj, width, height):
    """
    Add multiple watermarks across the page with better visibility.

    Args:
        canvas_obj: ReportLab canvas object
        width: Page width
        height: Page height
    """
    # Save current state
    canvas_obj.saveState()

    # Set watermark properties - darker and more visible
    canvas_obj.setFillColor(colors.grey)
    canvas_obj.setFillAlpha(0.4)

    # Large diagonal watermarks
    canvas_obj.setFont("Helvetica-Bold", 56)
    canvas_obj.rotate(45)

    # Main watermark - center
    canvas_obj.drawCentredString(width * 0.7, height * 0.1, "CONFIDENTIAL")

    # Additional diagonal watermarks
    canvas_obj.drawCentredString(width * 0.3, height * 0.3, "CONFIDENTIAL")
    canvas_obj.drawCentredString(width * 1.0, height * -0.1, "CONFIDENTIAL")

    # Restore state and add more watermarks
    canvas_obj.restoreState()
    canvas_obj.saveState()

    # Horizontal watermarks (no rotation)
    canvas_obj.setFillColor(colors.darkgrey)
    canvas_obj.setFillAlpha(0.3)
    canvas_obj.setFont("Helvetica-Bold", 32)

    # Top watermark
    canvas_obj.drawCentredString(width / 2, height - 100, "WATERMARKED DOCUMENT")

    # Middle watermarks
    canvas_obj.drawCentredString(width / 2, height / 2 + 50, "CONFIDENTIAL")
    canvas_obj.drawCentredString(width / 2, height / 2 - 50, "INTERNAL USE ONLY")

    # Bottom watermark
    canvas_obj.drawCentredString(width / 2, 150, "DO NOT DISTRIBUTE")

    # Side watermarks
    canvas_obj.setFont("Helvetica-Bold", 24)
    canvas_obj.setFillAlpha(0.25)

    # Left side vertical text
    canvas_obj.saveState()
    canvas_obj.rotate(90)
    canvas_obj.drawCentredString(height / 2, -50, "CONFIDENTIAL")
    canvas_obj.restoreState()

    # Right side vertical text
    canvas_obj.saveState()
    canvas_obj.rotate(-90)
    canvas_obj.drawCentredString(-height / 2, width - 50, "CONFIDENTIAL")
    canvas_obj.restoreState()

    # Corner watermarks
    canvas_obj.setFont("Helvetica", 18)
    canvas_obj.setFillColor(colors.red)
    canvas_obj.setFillAlpha(0.5)

    # Corner stamps
    canvas_obj.drawString(20, height - 30, "CONFIDENTIAL")
    canvas_obj.drawString(width - 120, height - 30, "CONFIDENTIAL")
    canvas_obj.drawString(20, 20, "CONFIDENTIAL")
    canvas_obj.drawString(width - 120, 20, "CONFIDENTIAL")

    # Additional security stamps
    canvas_obj.setFont("Helvetica-Bold", 14)
    canvas_obj.setFillColor(colors.darkred)
    canvas_obj.setFillAlpha(0.6)

    # Security stamps in various positions
    canvas_obj.drawString(width / 4, height * 0.75, "RESTRICTED")
    canvas_obj.drawString(width * 0.75, height * 0.75, "PRIVATE")
    canvas_obj.drawString(width / 4, height * 0.25, "SECURE")
    canvas_obj.drawString(width * 0.75, height * 0.25, "CLASSIFIED")

    # Restore state
    canvas_obj.restoreState()


def main():
    """Main function to generate the watermarked PDF."""
    output_dir = "output"

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = os.path.join(output_dir, "input_new.pdf")

    try:
        create_watermarked_pdf(filename, 250)
    except Exception as e:
        print(f"Error generating PDF: {e}")


if __name__ == "__main__":
    main()
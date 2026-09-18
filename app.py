from flask import Flask, render_template, request, jsonify, send_file
from chatboat import ask_saarthi

import os
import uuid
import textwrap
from datetime import datetime
from urllib.parse import quote
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

app = Flask(__name__)


# =====================================================
# FOLDERS
# =====================================================

UPLOAD_FOLDER = "uploads"

GENERATED_FOLDER = os.path.join("static", "generated")
PDF_FOLDER = os.path.join(GENERATED_FOLDER, "pdf")
FLOWCHART_FOLDER = os.path.join(GENERATED_FOLDER, "flowcharts")
IMAGE_FOLDER = os.path.join(GENERATED_FOLDER, "images")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(FLOWCHART_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():
    return render_template("index.html")


# =====================================================
# CHAT + IMAGE ANALYSIS
# =====================================================

@app.route("/chat", methods=["POST"])
def chat():

    image_path = None

    try:
        user_message = request.form.get("message", "").strip()
        image = request.files.get("image")

        # ---------------------------------------------
        # IMAGE UPLOAD
        # ---------------------------------------------

        if image and image.filename:

            extension = os.path.splitext(
                image.filename
            )[1].lower()

            allowed_extensions = [
                ".jpg",
                ".jpeg",
                ".png",
                ".webp"
            ]

            if extension not in allowed_extensions:
                return jsonify({
                    "reply":
                    "Please upload JPG, JPEG, PNG or WEBP image."
                }), 400

            filename = str(uuid.uuid4()) + extension

            image_path = os.path.join(
                UPLOAD_FOLDER,
                filename
            )

            image.save(image_path)

        # ---------------------------------------------
        # EMPTY REQUEST
        # ---------------------------------------------

        if not user_message and not image_path:
            return jsonify({
                "reply":
                "Please enter a message or select an image."
            }), 400

        # ---------------------------------------------
        # GEMINI
        # ---------------------------------------------

        reply = ask_saarthi(
            user_message,
            image_path
        )

        return jsonify({
            "reply": reply
        })

    except Exception as e:

        print("Chat Error:", repr(e))

        return jsonify({
            "reply":
            "Sorry, something went wrong. Please try again."
        }), 500

    finally:

        if image_path and os.path.exists(image_path):

            try:
                os.remove(image_path)
            except Exception as e:
                print("Image cleanup error:", repr(e))


# =====================================================
# PDF GENERATION
# =====================================================

@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer
        )
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.enums import TA_CENTER
        import re

        data = request.get_json(silent=True) or {}

        # IMPORTANT:
        # PDF is generated from the topic entered in the
        # message box, not from old currentChat history.
        topic = data.get("topic", "").strip()

        # Optional fallback for old frontend versions.
        messages = data.get("messages", [])

        if topic:

            prompt = f"""
Create a professional educational PDF document about:

{topic}

Write clear, useful and student-friendly content.

Include these sections:

1. Introduction
2. Definition
3. How it works
4. Main concepts
5. Examples
6. Advantages
7. Applications
8. Conclusion

Use short paragraphs and clear headings.
Do not mention that you are an AI.
"""

            content = ask_saarthi(prompt)
            pdf_title = topic.title()

        elif messages:

            # Backward compatibility only.
            content_parts = []

            for message in messages:

                role = message.get("role", "")
                text = message.get("content", "")

                if not text:
                    continue

                label = (
                    "You"
                    if role == "user"
                    else "Saarthi AI"
                )

                content_parts.append(
                    f"{label}: {text}"
                )

            content = "\n\n".join(content_parts)
            pdf_title = "Saarthi AI Chat"

        else:

            return jsonify({
                "error":
                "Please enter a topic first."
            }), 400

        # ---------------------------------------------
        # PDF FILE
        # ---------------------------------------------

        filename = (
            "Saarthi_AI_"
            + datetime.now().strftime("%Y%m%d_%H%M%S")
            + ".pdf"
        )

        filepath = os.path.join(
            PDF_FOLDER,
            filename
        )

        document = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=45,
            leftMargin=45,
            topMargin=45,
            bottomMargin=45
        )

        styles = getSampleStyleSheet()
        styles["Title"].alignment = TA_CENTER

        story = []

        story.append(
            Paragraph(
                "SAARTHI AI",
                styles["Title"]
            )
        )

        story.append(
            Paragraph(
                pdf_title,
                styles["Heading1"]
            )
        )

        story.append(Spacer(1, 20))

        # ---------------------------------------------
        # CONTENT
        # ---------------------------------------------

        content = str(content)

        for line in content.splitlines():

            line = line.strip()

            if not line:
                story.append(Spacer(1, 8))
                continue

            clean_line = re.sub(
                r"^#{1,6}\s*",
                "",
                line
            )

            clean_line = re.sub(
                r"\*\*(.*?)\*\*",
                r"\1",
                clean_line
            )

            clean_line = (
                clean_line
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            if (
                line.startswith("#")
                or re.match(
                    r"^\d+\.\s+[A-Z]",
                    line
                )
            ):

                story.append(
                    Paragraph(
                        f"<b>{clean_line}</b>",
                        styles["Heading3"]
                    )
                )

            elif line.startswith("-"):

                clean_line = line[1:].strip()

                story.append(
                    Paragraph(
                        f"• {clean_line}",
                        styles["BodyText"]
                    )
                )

            else:

                story.append(
                    Paragraph(
                        clean_line,
                        styles["BodyText"]
                    )
                )

            story.append(Spacer(1, 7))

        document.build(story)

        # PDF is created on the server, but it is NOT downloaded automatically.
        # Frontend receives the URL and shows a Download PDF button.
        pdf_url = "/download-pdf/" + filename

        return jsonify({
            "reply": f"PDF successfully created for: {topic or pdf_title}",
            "pdf": pdf_url,
            "filename": filename
        })

    except Exception as e:

        print("PDF Error:", repr(e))

        return jsonify({
            "error":
            "Could not generate PDF."
        }), 500


# =====================================================
# DOWNLOAD PDF
# =====================================================

@app.route("/download-pdf/<filename>")
def download_pdf(filename):
    try:
        # Prevent path traversal. Only files inside PDF_FOLDER are served.
        safe_name = os.path.basename(filename)

        if safe_name != filename or not safe_name.lower().endswith(".pdf"):
            return jsonify({"error": "Invalid PDF file."}), 400

        filepath = os.path.join(PDF_FOLDER, safe_name)

        if not os.path.isfile(filepath):
            return jsonify({"error": "PDF file not found."}), 404

        return send_file(
            filepath,
            as_attachment=True,
            download_name=safe_name,
            mimetype="application/pdf"
        )

    except Exception as e:
        print("PDF Download Error:", repr(e))
        return jsonify({"error": "Could not download PDF."}), 500


# =====================================================
# GET FONT
# =====================================================

def get_font(size, bold=False):

    font_paths = []

    if os.name == "nt":

        if bold:
            font_paths.append(
                r"C:\Windows\Fonts\arialbd.ttf"
            )

        font_paths.append(
            r"C:\Windows\Fonts\arial.ttf"
        )

    font_paths.append(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    )

    font_paths.append(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    )

    for path in font_paths:

        if os.path.exists(path):

            try:
                return ImageFont.truetype(
                    path,
                    size
                )
            except Exception:
                pass

    return ImageFont.load_default()


# =====================================================
# FLOWCHART TEXT
# =====================================================

def get_flowchart_steps(topic):

    prompt = f"""
Create a simple educational flowchart for:

{topic}

Return exactly 6 short steps.

Use this format:

1. Short step
2. Short step
3. Short step
4. Short step
5. Short step
6. Short step

Keep every step short.
Do not add explanations.
"""

    result = ask_saarthi(prompt)

    steps = []

    for line in result.splitlines():

        line = line.strip()

        if not line:
            continue

        if "." in line:

            number, step_text = line.split(
                ".",
                1
            )

            if number.strip().isdigit():

                step_text = step_text.strip()

                if step_text:
                    steps.append(step_text)

    if not steps:

        steps = [
            "Understand the topic",
            "Learn the fundamentals",
            "Practice the concepts",
            "Apply the knowledge",
            "Test the result",
            "Complete the task"
        ]

    return steps[:6]


# =====================================================
# FLOWCHART GENERATION
# =====================================================

@app.route("/generate-flowchart", methods=["POST"])
def generate_flowchart():

    try:

        data = request.get_json(
            silent=True
        ) or {}

        topic = data.get(
            "topic",
            ""
        ).strip()

        if not topic:

            return jsonify({
                "reply":
                "Please enter a topic for the flowchart."
            }), 400

        steps = get_flowchart_steps(topic)

        # ---------------------------------------------
        # IMAGE SIZE
        # ---------------------------------------------

        width = 1000
        box_width = 760
        box_height = 100
        gap = 75
        top_margin = 120
        bottom_margin = 80

        height = (
            top_margin
            + len(steps) * (box_height + gap)
            + bottom_margin
        )

        # ---------------------------------------------
        # CREATE PNG
        # ---------------------------------------------

        image = Image.new(
            "RGB",
            (width, height),
            "white"
        )

        draw = ImageDraw.Draw(image)

        title_font = get_font(34, bold=True)
        step_font = get_font(22, bold=True)

        # ---------------------------------------------
        # TITLE
        # ---------------------------------------------

        title = f"Flowchart: {topic}"

        title_bbox = draw.textbbox(
            (0, 0),
            title,
            font=title_font
        )

        title_width = (
            title_bbox[2] - title_bbox[0]
        )

        draw.text(
            (
                (width - title_width) / 2,
                35
            ),
            title,
            fill="black",
            font=title_font
        )

        # ---------------------------------------------
        # BOXES
        # ---------------------------------------------

        for index, step in enumerate(steps):

            x = (width - box_width) // 2

            y = (
                top_margin
                + index * (box_height + gap)
            )

            # -----------------------------------------
            # ARROW
            # -----------------------------------------

            if index > 0:

                arrow_start = y - gap + 5
                arrow_end = y - 5
                center_x = width // 2

                draw.line(
                    (
                        center_x,
                        arrow_start,
                        center_x,
                        arrow_end
                    ),
                    fill="black",
                    width=4
                )

                draw.polygon(
                    [
                        (
                            center_x - 10,
                            arrow_end - 14
                        ),
                        (
                            center_x + 10,
                            arrow_end - 14
                        ),
                        (
                            center_x,
                            arrow_end
                        )
                    ],
                    fill="black"
                )

            # -----------------------------------------
            # BOX
            # -----------------------------------------

            draw.rounded_rectangle(
                (
                    x,
                    y,
                    x + box_width,
                    y + box_height
                ),
                radius=18,
                outline="black",
                width=3,
                fill="#f8fafc"
            )

            # -----------------------------------------
            # TEXT WRAP
            # -----------------------------------------

            wrapped = textwrap.wrap(
                step,
                width=48
            )

            lines = wrapped[:2]

            line_heights = []

            for line in lines:

                bbox = draw.textbbox(
                    (0, 0),
                    line,
                    font=step_font
                )

                line_heights.append(
                    bbox[3] - bbox[1]
                )

            total_height = (
                sum(line_heights)
                + max(0, len(lines) - 1) * 8
            )

            current_y = (
                y
                + (box_height - total_height) / 2
            )

            for line in lines:

                bbox = draw.textbbox(
                    (0, 0),
                    line,
                    font=step_font
                )

                text_width = (
                    bbox[2] - bbox[0]
                )

                draw.text(
                    (
                        (width - text_width) / 2,
                        current_y
                    ),
                    line,
                    fill="black",
                    font=step_font
                )

                current_y += (
                    bbox[3] - bbox[1] + 8
                )

        # ---------------------------------------------
        # SAVE PNG
        # ---------------------------------------------

        filename = (
            "flowchart_"
            + datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )
            + "_"
            + str(uuid.uuid4())[:6]
            + ".png"
        )

        filepath = os.path.join(
            FLOWCHART_FOLDER,
            filename
        )

        image.save(
            filepath,
            "PNG"
        )

        image_url = (
            "/static/generated/"
            "flowcharts/"
            + filename
        )

        return jsonify({
            "reply":
            f"Flowchart created for: {topic}",
            "image":
            image_url
        })

    except Exception as e:

        print(
            "Flowchart Error:",
            repr(e)
        )

        return jsonify({
            "reply":
            "Could not generate the flowchart. Please try again."
        }), 500


# =====================================================
# AI IMAGE GENERATION
# =====================================================

@app.route("/generate-image", methods=["POST"])
def generate_image():
    """
    Free text-to-image generation using Pollinations.
    This keeps normal Saarthi chat on Gemini and uses a separate
    image backend so Gemini paid image billing is not required.
    """

    try:
        data = request.get_json(silent=True) or {}
        prompt = data.get("prompt", "").strip()

        if not prompt:
            return jsonify({
                "reply": "Please enter an image description."
            }), 400

        # Encode the complete prompt safely for the URL.
        encoded_prompt = quote(prompt, safe="")

        # Pollinations' public image endpoint.
        image_url = (
            "https://image.pollinations.ai/prompt/"
            + encoded_prompt
            + "?model=flux"
            + "&width=1024"
            + "&height=1024"
            + "&nologo=true"
        )

        request_obj = Request(
            image_url,
            headers={
                "User-Agent": "Saarthi-AI/1.0"
            }
        )

        with urlopen(request_obj, timeout=120) as response:
            image_bytes = response.read()

        if not image_bytes:
            return jsonify({
                "reply": "Image service returned an empty image."
            }), 502

        filename = (
            "generated_"
            + datetime.now().strftime("%Y%m%d_%H%M%S")
            + "_"
            + str(uuid.uuid4())[:8]
            + ".png"
        )

        filepath = os.path.join(IMAGE_FOLDER, filename)

        with open(filepath, "wb") as image_file:
            image_file.write(image_bytes)

        generated_file = (
            "/static/generated/images/"
            + filename
        )

        return jsonify({
            "reply": "Your image has been generated successfully.",
            "image": generated_file
        })

    except Exception as e:
        print("IMAGE GENERATION ERROR:", repr(e))

        return jsonify({
            "reply":
            "Image generation failed. "
            "The free image service may be busy or rate-limited. "
            "Please try again."
        }), 500


# =====================================================
# RUN SERVER
# =====================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )

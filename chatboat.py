import os
from dotenv import load_dotenv
from google import genai
from PIL import Image

# ==========================================
# ENVIRONMENT LOAD
# ==========================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not configured in the .env file."
    )


# ==========================================
# GEMINI CLIENT
# ==========================================

client = genai.Client(api_key=API_KEY)

# Free-tier testing ke liye lightweight model
MODEL_NAME = "gemini-3.5-flash-lite"


# ==========================================
# SAARTHI AI FUNCTION
# ==========================================

def ask_saarthi(question, image_path=None):

    try:

        question = (question or "").strip()

        # --------------------------------------
        # EMPTY MESSAGE
        # --------------------------------------

        if not question and not image_path:
            return "Please enter a message."


        # --------------------------------------
        # IMAGE + TEXT
        # --------------------------------------

        if image_path:

            print("Image received:", image_path)

            try:
                image = Image.open(image_path)
                image.load()

            except Exception as image_error:

                print("IMAGE ERROR:", repr(image_error))

                return (
                    "⚠️ Image open nahi ho paayi.\n\n"
                    "Please image ko dobara upload karein."
                )


            if not question:

                question = (
                    "Analyze this image carefully and explain what "
                    "is visible in simple and clear language. "
                    "If it is a document, diagram, object, technical "
                    "problem, educational image, or agricultural image, "
                    "provide useful details."
                )


            print("Sending image request to Gemini...")

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[
                    question,
                    image
                ]
            )


        # --------------------------------------
        # TEXT ONLY
        # --------------------------------------

        else:

            print("User Question:", question)
            print("Sending text request to Gemini...")

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=question
            )


        # --------------------------------------
        # RESPONSE CHECK
        # --------------------------------------

        if response:

            print("Gemini response received.")

            if response.text:
                return response.text.strip()


        return "Saarthi AI ne koi response generate nahi kiya."


    # ==========================================
    # GEMINI ERROR
    # ==========================================

    except Exception as e:

        error_text = str(e)

        # Terminal me COMPLETE error dikhega
        print("\n========================================")
        print("        SAARTHI AI / GEMINI ERROR")
        print("========================================")
        print(repr(e))
        print("========================================\n")


        # --------------------------------------
        # 429 / QUOTA
        # --------------------------------------

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
            or "quota" in error_text.lower()
        ):

            return (
                "⚠️ Gemini Free Tier quota currently exhausted.\n\n"
                "Please try again after the quota resets."
            )


        # --------------------------------------
        # API KEY / AUTHENTICATION
        # --------------------------------------

        if (
            "API_KEY" in error_text
            or "api key" in error_text.lower()
            or "authentication" in error_text.lower()
            or "unauthenticated" in error_text.lower()
            or "401" in error_text
            or "403" in error_text
        ):

            return (
                "⚠️ Gemini API key authentication problem.\n\n"
                "Please check your GEMINI_API_KEY in the .env file."
            )


        # --------------------------------------
        # MODEL ERROR
        # --------------------------------------

        if (
            "model" in error_text.lower()
            and (
                "not found" in error_text.lower()
                or "not supported" in error_text.lower()
            )
        ):

            return (
                "⚠️ Gemini model problem.\n\n"
                "The selected model is not available for this API setup."
            )


        # --------------------------------------
        # CONNECTION ERROR
        # --------------------------------------

        if (
            "connection" in error_text.lower()
            or "timeout" in error_text.lower()
            or "network" in error_text.lower()
        ):

            return (
                "⚠️ Gemini server se connection nahi ho pa raha.\n\n"
                "Please check your internet connection and try again."
            )


        # --------------------------------------
        # GENERAL ERROR
        # --------------------------------------

        return (
            "⚠️ Saarthi AI me technical problem aa gayi.\n\n"
            f"Error: {error_text}"
        )

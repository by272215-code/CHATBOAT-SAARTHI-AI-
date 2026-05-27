import google.generativeai as genai
BOT_NAME = "Saarthi AI"
genai.configure(api_key="AIzaSyCjSnzSruj1CWmzeNgWnxF_C1oTg7Ms9R4")
model = genai.GenerativeModel("gemini-2.5-flash")
while True:
    question = input("You: ")
    if question.lower() == "exit":
        break
    response = model.generate_content(question)
    print(f"{BOT_NAME}: {response.text}")

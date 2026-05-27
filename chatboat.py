import google.generativeai as genai
BOT_NAME = "Saarthi AI"
genai.configure(api_key="HIDDEN API KEY ,  I Am Not Share API Key Because Its Privet")
model = genai.GenerativeModel("gemini-2.5-flash")
while True:
    question = input("You: ")
    if question.lower() == "exit":
        break
    response = model.generate_content(question)
    print(f"{BOT_NAME}: {response.text}")

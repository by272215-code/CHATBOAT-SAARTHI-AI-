import openai
openai.api_key = "YOUR_API_KEY"
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": user_input}
        ]
    )
    print("Bot:", response["choices"][0]["message"]["content"])
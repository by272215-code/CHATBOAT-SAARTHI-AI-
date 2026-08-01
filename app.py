from flask import Flask, render_template, request, jsonify
from chatboat import ask_saarthi

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]
    reply = ask_saarthi(user_message)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
// =====================================================
// SAARTHI AI - COMPLETE JAVASCRIPT
// =====================================================

let currentChat = [];

const HISTORY_KEY = "saarthi_ai_history";


// =====================================================
// PAGE LOAD
// =====================================================

document.addEventListener("DOMContentLoaded", function () {

    loadHistory();
    setupImagePreview();
    setupEnterKey();

});


// =====================================================
// SEND MESSAGE
// =====================================================

async function sendMessage() {

    const input = document.getElementById("message");
    const chat = document.getElementById("chat-box");
    const imageUpload = document.getElementById("imageUpload");

    if (!input || !chat) {
        console.error("Message input or chat box not found.");
        return;
    }

    const message = input.value.trim();

    const image =
        imageUpload && imageUpload.files.length > 0
            ? imageUpload.files[0]
            : null;


    if (message === "" && !image) {
        return;
    }


    // Show user message

    if (message !== "") {

        addUserMessage(message);

        currentChat.push({
            role: "user",
            type: "text",
            content: message
        });

    }


    // Show uploaded image

    if (image) {

        addUserImage(image);

        currentChat.push({
            role: "user",
            type: "image",
            content: image.name
        });

    }


    input.value = "";


    // Typing indicator

    const typing = document.createElement("div");

    typing.className =
        "message bot typing";

    typing.innerHTML = image
        ? "Saarthi AI is analyzing the image..."
        : "Saarthi AI is typing...";

    chat.appendChild(typing);

    chat.scrollTop = chat.scrollHeight;


    try {

        const formData = new FormData();

        formData.append(
            "message",
            message
        );


        if (image) {

            formData.append(
                "image",
                image
            );

        }


        const response = await fetch(
            "/chat",
            {
                method: "POST",
                body: formData
            }
        );


        const contentType =
            response.headers.get("content-type") || "";


        let data = {};


        if (contentType.includes("application/json")) {

            data = await response.json();

        }


        if (!response.ok) {

            throw new Error(
                data.error ||
                data.reply ||
                "Server Error: " + response.status
            );

        }


        typing.remove();


        const reply =
            data.reply ||
            "No response received.";


        addBotMessage(reply);


        currentChat.push({
            role: "assistant",
            type: "text",
            content: reply
        });


        saveCurrentChat();


        // Clear image

        if (imageUpload) {

            imageUpload.value = "";

        }


        const preview =
            document.getElementById(
                "image-preview"
            );


        if (preview) {

            preview.innerHTML = "";

            preview.style.display = "none";

        }


        chat.scrollTop =
            chat.scrollHeight;


    } catch (error) {

        console.error(
            "Chat Error:",
            error
        );


        typing.remove();


        addBotMessage(
            "Sorry, something went wrong. " +
            error.message
        );

    }

}


// =====================================================
// ADD USER MESSAGE
// =====================================================

function addUserMessage(message) {

    const chat =
        document.getElementById(
            "chat-box"
        );

    if (!chat) {
        return;
    }


    const div =
        document.createElement(
            "div"
        );


    div.className =
        "message user";


    div.innerHTML = `
        <b>You:</b>
        ${escapeHTML(message)}
    `;


    chat.appendChild(div);

    chat.scrollTop =
        chat.scrollHeight;

}


// =====================================================
// ADD USER IMAGE
// =====================================================

function addUserImage(image) {

    const chat =
        document.getElementById(
            "chat-box"
        );

    if (!chat) {
        return;
    }


    const div =
        document.createElement(
            "div"
        );


    div.className =
        "message user image-message";


    const imageURL =
        URL.createObjectURL(image);


    div.innerHTML = `
        <b>You:</b>
        <br>

        <img
            src="${imageURL}"
            class="chat-image"
            alt="Uploaded Image"
        >
    `;


    chat.appendChild(div);

}


// =====================================================
// ADD BOT MESSAGE
// =====================================================

function addBotMessage(reply) {

    const chat =
        document.getElementById(
            "chat-box"
        );

    if (!chat) {
        return;
    }


    const div =
        document.createElement(
            "div"
        );


    div.className =
        "message bot";


    div.innerHTML = `
        <div class="bot-content">

            <p class="bot-name">
                <strong>Saarthi AI</strong>
            </p>

            ${formatResponse(reply)}

        </div>
    `;


    chat.appendChild(div);

    chat.scrollTop =
        chat.scrollHeight;

}


// =====================================================
// FORMAT AI RESPONSE
// =====================================================

function formatResponse(text) {

    if (!text) {

        return `
            <p>
                No response received.
            </p>
        `;

    }


    text = String(text);

    text = escapeHTML(text);


    // Code blocks

    text = text.replace(
        /```([\s\S]*?)```/g,
        "<pre><code>$1</code></pre>"
    );


    // Headings

    text = text.replace(
        /^###\s+(.*)$/gm,
        "<h3>$1</h3>"
    );


    text = text.replace(
        /^##\s+(.*)$/gm,
        "<h2>$1</h2>"
    );


    text = text.replace(
        /^#\s+(.*)$/gm,
        "<h2>$1</h2>"
    );


    // Bold

    text = text.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );


    // Numbered list

    text = text.replace(
        /^\s*(\d+)\.\s+(.*)$/gm,
        "<br><strong>$1.</strong> $2"
    );


    // Bullet list

    text = text.replace(
        /^\s*[-*]\s+(.*)$/gm,
        "<br>• $1"
    );


    // Paragraphs

    const paragraphs =
        text.split(/\n\s*\n/);


    text = paragraphs
        .map(function (paragraph) {

            paragraph =
                paragraph.trim();


            if (!paragraph) {
                return "";
            }


            if (
                paragraph.startsWith("<h2>") ||
                paragraph.startsWith("<h3>") ||
                paragraph.startsWith("<pre>") ||
                paragraph.startsWith("<br>")
            ) {

                return paragraph;

            }


            paragraph =
                paragraph.replace(
                    /\n/g,
                    "<br>"
                );


            return `
                <p>
                    ${paragraph}
                </p>
            `;

        })
        .join("");


    return text;

}


// =====================================================
// ESCAPE HTML
// =====================================================

function escapeHTML(text) {

    const div =
        document.createElement(
            "div"
        );

    div.textContent =
        String(text ?? "");

    return div.innerHTML;

}


// =====================================================
// IMAGE PREVIEW
// =====================================================

function setupImagePreview() {

    const imageUpload =
        document.getElementById(
            "imageUpload"
        );

    const preview =
        document.getElementById(
            "image-preview"
        );


    if (!imageUpload || !preview) {
        return;
    }


    imageUpload.addEventListener(
        "change",
        function () {

            const file =
                this.files[0];


            if (!file) {

                preview.innerHTML =
                    "";

                preview.style.display =
                    "none";

                return;

            }


            if (!file.type.startsWith("image/")) {

                alert(
                    "Please select a valid image."
                );

                this.value = "";

                return;

            }


            const imageURL =
                URL.createObjectURL(file);


            preview.innerHTML = `

                <img
                    src="${imageURL}"
                    alt="Selected Image"
                >

                <div class="image-name">
                    📷 ${escapeHTML(file.name)}
                </div>

            `;


            preview.style.display =
                "block";

        }
    );

}


// =====================================================
// ENTER KEY
// =====================================================

function setupEnterKey() {

    const input =
        document.getElementById(
            "message"
        );


    if (!input) {
        return;
    }


    input.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendMessage();

            }

        }
    );

}


// =====================================================
// NEW CHAT
// =====================================================

function newChat() {

    const chat =
        document.getElementById(
            "chat-box"
        );


    if (!chat) {
        return;
    }


    if (currentChat.length > 0) {

        saveCurrentChat();

    }


    currentChat = [];


    chat.innerHTML = `

        <div class="message bot">

            <div class="bot-content">

                <p class="welcome">
                    👋 Welcome to
                    <strong>Saarthi AI</strong>
                </p>

                <p>
                    How can I help you today?
                </p>

            </div>

        </div>

    `;


    const input =
        document.getElementById(
            "message"
        );


    if (input) {
        input.value = "";
    }


    const imageUpload =
        document.getElementById(
            "imageUpload"
        );


    if (imageUpload) {
        imageUpload.value = "";
    }


    const preview =
        document.getElementById(
            "image-preview"
        );


    if (preview) {

        preview.innerHTML =
            "";

        preview.style.display =
            "none";

    }

}


// =====================================================
// SAVE CHAT HISTORY
// =====================================================

function saveCurrentChat() {

    if (currentChat.length === 0) {
        return;
    }


    let history =
        JSON.parse(
            localStorage.getItem(
                HISTORY_KEY
            )
        ) || [];


    const firstUserMessage =
        currentChat.find(
            item =>
                item.role === "user" &&
                item.type === "text"
        );


    let title =
        firstUserMessage
            ? firstUserMessage.content
            : "New Chat";


    title =
        title.substring(
            0,
            40
        );


    const chatData = {

        id: Date.now(),

        title: title,

        messages: currentChat,

        date:
            new Date()
                .toLocaleString()

    };


    history.unshift(
        chatData
    );


    history =
        history.slice(
            0,
            30
        );


    localStorage.setItem(
        HISTORY_KEY,
        JSON.stringify(history)
    );


    loadHistory();

}


// =====================================================
// LOAD HISTORY
// =====================================================

function loadHistory() {

    const historyList =
        document.getElementById(
            "history-list"
        );


    if (!historyList) {
        return;
    }


    const history =
        JSON.parse(
            localStorage.getItem(
                HISTORY_KEY
            )
        ) || [];


    historyList.innerHTML =
        "";


    if (history.length === 0) {

        historyList.innerHTML = `

            <div class="history-empty">
                No previous chats
            </div>

        `;

        return;

    }


    history.forEach(
        function (chat) {

            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "history-item";


            item.title =
                chat.title;


            item.innerHTML = `
                💬 ${escapeHTML(chat.title)}
            `;


            item.onclick =
                function () {

                    openHistoryChat(
                        chat.id
                    );

                };


            historyList.appendChild(
                item
            );

        }
    );

}


// =====================================================
// OPEN HISTORY CHAT
// =====================================================

function openHistoryChat(id) {

    const history =
        JSON.parse(
            localStorage.getItem(
                HISTORY_KEY
            )
        ) || [];


    const selected =
        history.find(
            chat =>
                chat.id === id
        );


    if (!selected) {
        return;
    }


    const chat =
        document.getElementById(
            "chat-box"
        );


    if (!chat) {
        return;
    }


    chat.innerHTML =
        "";


    currentChat =
        selected.messages || [];


    currentChat.forEach(
        function (message) {

            if (
                message.role === "user"
            ) {

                if (
                    message.type === "image"
                ) {

                    const div =
                        document.createElement(
                            "div"
                        );


                    div.className =
                        "message user";


                    div.innerHTML = `

                        <b>You:</b>
                        <br>

                        📷
                        ${escapeHTML(
                            message.content
                        )}

                    `;


                    chat.appendChild(
                        div
                    );

                } else {

                    addUserMessage(
                        message.content
                    );

                }

            }


            if (
                message.role ===
                "assistant"
            ) {

                addBotMessage(
                    message.content
                );

            }

        }
    );


    chat.scrollTop =
        chat.scrollHeight;

}


// =====================================================
// CLEAR HISTORY
// =====================================================

function clearHistory() {

    const confirmDelete =
        confirm(
            "Are you sure you want to delete all chat history?"
        );


    if (!confirmDelete) {
        return;
    }


    localStorage.removeItem(
        HISTORY_KEY
    );


    currentChat = [];


    loadHistory();


    newChat();

}


// =====================================================
// GENERATE PDF
// =====================================================

async function generatePDF() {

    const input =
        document.getElementById(
            "message"
        );


    if (!input) {
        return;
    }


    const topic =
        input.value.trim();


    if (!topic) {

        alert(
            "PDF banane ke liye pehle topic enter karo."
        );

        input.focus();

        return;

    }


    const chat =
        document.getElementById(
            "chat-box"
        );


    addUserMessage(
        "Create PDF: " + topic
    );


    input.value =
        "";


    const typing =
        document.createElement(
            "div"
        );


    typing.className =
        "message bot typing";


    typing.innerHTML =
        "Saarthi AI is creating your PDF...";


    chat.appendChild(
        typing
    );


    chat.scrollTop =
        chat.scrollHeight;


    try {

        const response =
            await fetch(
                "/generate-pdf",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            topic: topic
                        })
                }
            );


        const data =
            await response.json();


        typing.remove();


        if (!response.ok) {

            throw new Error(
                data.error ||
                data.reply ||
                "PDF generation failed."
            );

        }


        if (data.pdf) {

            addPDFDownload(
                data.pdf,
                data.filename ||
                    "Saarthi_AI.pdf",
                data.reply ||
                    "PDF successfully created."
            );

        } else {

            addBotMessage(
                data.reply ||
                "PDF created successfully."
            );

        }


    } catch (error) {

        typing.remove();


        console.error(
            "PDF Error:",
            error
        );


        addBotMessage(
            "PDF generate nahi ho saka: " +
            error.message
        );

    }

}


// =====================================================
// PDF DOWNLOAD
// =====================================================

function addPDFDownload(
    pdfURL,
    filename,
    message
) {

    const chat =
        document.getElementById(
            "chat-box"
        );


    const div =
        document.createElement(
            "div"
        );


    div.className =
        "message bot";


    div.innerHTML = `

        <div class="bot-content">

            <p class="bot-name">
                <strong>Saarthi AI</strong>
            </p>

            <p>
                ${escapeHTML(message)}
            </p>

            <div class="generated-actions pdf-actions">

                <a
                    href="${pdfURL}"
                    download="${escapeHTML(filename)}"
                    class="download-btn"
                >
                    ⬇ Download PDF
                </a>

            </div>

        </div>

    `;


    chat.appendChild(div);


    chat.scrollTop =
        chat.scrollHeight;

}


// =====================================================
// GENERATE FLOWCHART
// =====================================================

async function generateFlowchart() {

    const input =
        document.getElementById(
            "message"
        );


    if (!input) {
        return;
    }


    const topic =
        input.value.trim();


    if (!topic) {

        alert(
            "Enter a topic for the flowchart first."
        );

        input.focus();

        return;

    }


    addUserMessage(
        "Create a flowchart for: " +
        topic
    );


    input.value =
        "";


    const chat =
        document.getElementById(
            "chat-box"
        );


    const typing =
        document.createElement(
            "div"
        );


    typing.className =
        "message bot typing";


    typing.innerHTML =
        "Saarthi AI is creating your flowchart...";


    chat.appendChild(
        typing
    );


    try {

        const response =
            await fetch(
                "/generate-flowchart",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            topic: topic
                        })
                }
            );


        const data =
            await response.json();


        typing.remove();


        if (!response.ok) {

            throw new Error(
                data.error ||
                data.reply ||
                "Flowchart generation failed."
            );

        }


        if (data.reply) {

            addBotMessage(
                data.reply
            );

        }


        if (data.image) {

            addGeneratedImage(
                data.image,
                "Generated Flowchart"
            );

        }


    } catch (error) {

        typing.remove();


        console.error(
            "Flowchart Error:",
            error
        );


        addBotMessage(
            "Unable to generate the flowchart: " +
            error.message
        );

    }

}


// =====================================================
// GENERATE IMAGE
// =====================================================

async function generateImage() {

    const input =
        document.getElementById(
            "message"
        );


    if (!input) {
        return;
    }


    const prompt =
        input.value.trim();


    if (!prompt) {

        alert(
            "Image generate karne ke liye pehle description enter karo."
        );

        input.focus();

        return;

    }


    const chat =
        document.getElementById(
            "chat-box"
        );


    addUserMessage(
        "Generate image: " +
        prompt
    );


    input.value =
        "";


    const typing =
        document.createElement(
            "div"
        );


    typing.className =
        "message bot typing";


    typing.innerHTML =
        "🎨 Saarthi AI is generating your image...";


    chat.appendChild(
        typing
    );


    chat.scrollTop =
        chat.scrollHeight;


    try {

        const response =
            await fetch(
                "/generate-image",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            prompt: prompt
                        })
                }
            );


        const data =
            await response.json();


        typing.remove();


        if (!response.ok) {

            throw new Error(
                data.error ||
                data.reply ||
                "Image generation failed."
            );

        }


        if (data.image) {

            addBotMessage(
                data.reply ||
                "Your image has been generated successfully."
            );


            addGeneratedImage(
                data.image,
                "Generated Image"
            );

        } else {

            addBotMessage(
                data.reply ||
                "Image was not generated."
            );

        }


    } catch (error) {

        typing.remove();


        console.error(
            "Image Generation Error:",
            error
        );


        addBotMessage(
            "Image generation failed: " +
            error.message
        );

    }

}


// =====================================================
// SHOW GENERATED IMAGE
// =====================================================

function addGeneratedImage(
    imageURL,
    title
) {

    const chat =
        document.getElementById(
            "chat-box"
        );


    const div =
        document.createElement(
            "div"
        );


    div.className =
        "message bot";


    div.innerHTML = `

        <div class="bot-content">

            <p>
                <strong>
                    ${escapeHTML(title)}
                </strong>
            </p>

            <div class="generated-image-container">

                <img
                    src="${imageURL}"
                    class="generated-image"
                    alt="${escapeHTML(title)}"
                    loading="lazy"
                    onerror="this.parentElement.innerHTML='<p>Unable to display the generated image.</p>'"
                >

            </div>

            <div class="generated-actions">

                <a
                    href="${imageURL}"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="download-btn"
                >
                    🔍 Open
                </a>

                <a
                    href="${imageURL}"
                    download
                    class="download-btn"
                >
                    ⬇ Download
                </a>

            </div>

        </div>

    `;


    chat.appendChild(div);


    chat.scrollTop =
        chat.scrollHeight;

}


// =====================================================
// VOICE INPUT
// =====================================================

function startVoice() {

    const input =
        document.getElementById(
            "message"
        );


    if (!input) {
        return;
    }


    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;


    if (!SpeechRecognition) {

        alert(
            "Voice input is not supported in this browser."
        );

        return;

    }


    const recognition =
        new SpeechRecognition();


    recognition.lang =
        "en-IN";


    recognition.continuous =
        false;


    recognition.interimResults =
        false;


    recognition.start();


    recognition.onresult =
        function (event) {

            input.value =
                event.results[0][0]
                    .transcript;

        };


    recognition.onerror =
        function (event) {

            console.error(
                "Voice error:",
                event.error
            );

        };

}


// =====================================================
// EXPORT FUNCTIONS
// =====================================================

window.sendMessage =
    sendMessage;

window.startVoice =
    startVoice;

window.newChat =
    newChat;

window.clearHistory =
    clearHistory;

window.generatePDF =
    generatePDF;

window.generateFlowchart =
    generateFlowchart;

window.generateImage =
    generateImage;

window.addPDFDownload =
    addPDFDownload;

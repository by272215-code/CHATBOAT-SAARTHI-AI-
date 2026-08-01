async function sendMessage(){

    const input=document.getElementById("message");

    const message=input.value;

    if(message=="") return;

    const chat=document.getElementById("chat-box");

    chat.innerHTML += "<p class='user'><b>You:</b> "+message+"</p>";

    input.value="";

    const response=await fetch("/chat",{
  

        method:"POST",

        headers:{
            "Content-Type":"application/json"
        },

        body:JSON.stringify({
            message:message
        })

    });

    const data=await response.json();

    chat.innerHTML += "<p class='bot'><b>Saarthi AI:</b> "+data.reply+"</p>";

    chat.scrollTop=chat.scrollHeight;

}
function startVoice(){

const recognition = new webkitSpeechRecognition();

recognition.lang = "en-IN";

recognition.start();

recognition.onresult = function(event){

document.getElementById("message").value =
event.results[0][0].transcript;

sendMessage();

}

}
const socketio = io();

const messages = document.getElementById("messages");

convertHTMLString = (msg) => {
    for (char=0; char<msg.length; char++) {
        if (msg[char] == "<") {
            msg = msg.slice(0, char) + "&lt;" + msg.slice(char+1);
        } else if (msg[char] == ">") {
            msg = msg.slice(0, char) + "&gt;" + msg.slice(char+1);
        }
    }
    return msg;
}

const createMessage = (msg) => {
    console.log(msg)
    
    const content = `
    <div class="text">
        <span style="font-size: 0.7rem;">
            ${msg}
        </span>
    </div>
    <lbr>
    `;
    messages.innerHTML += content;
};

createStructuredMessage = (msg) => {
    const content = `
    <div class="text">
        <pre style="font-size: 0.7rem;">
            ${convertHTMLString(msg)}
        </pre>
    </div>
    <lbr>`;
    messages.innerHTML += content;
    
};

const output = document.getElementById("output_structured")

createCorrectStructuredMessage = (msg) => {
    output.innerHTML += `<div>${convertHTMLString(msg)}</div>`;
    output.innerHTML += "<br>";
    // Prism.highlightAll();    
};

socketio.on("message", (msg) => {
    createMessage(msg);
});

socketio.on("message_structured", (msg) => {
    createStructuredMessage(msg);
});

const tab = document.getElementById("defaultOpen");

socketio.on("correct_structured", (msg) => {
    createCorrectStructuredMessage(msg);
    tab.click();
    if (button.value != "Translate") {
        button.value = "Translate";
        button.disabled = false;
    }
});
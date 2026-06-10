document.addEventListener("DOMContentLoaded", function () {
    const messageData = document.getElementById("django_messages");
    if (!messageData) return;

    const messages = JSON.parse(messageData.textContent);
    if (!messages.length) return;

    const messageItems = messages
        .map(m => `<p class="pop_content ${m.tags}">${m.text}</p>`)
        .join("");

    const modalHTML = `
        <div id="messages_modal" class="model_pop">
            <div class="model-content">
                <span class="close_button">&times;</span>
                <h3>Notice</h3>
                <hr>
                ${messageItems}
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML("beforeend", modalHTML);
    const style = document.createElement("style");
    style.textContent = `
        .model_pop {
            display: none; 
            position: fixed; 
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%; 
            overflow: auto;
            font-size: 1.125em;
            background-color: rgba(0, 0, 0, 0.3);
            line-height: 1.5;
        }
        .model-content {
            background-color: #fff;
            margin: 10em auto;
            padding: 1.5em;
            border-radius: 12px;
            box-shadow: 0px 4px 20px rgba(0,0,0,0.15);
            width: min(75vw, 450px);
            color: #000000ff;
            font-family: system-ui, sans-serif;
        }
        .pop_content:first-of-type {
            margin-top: 1em;
        }
        .pop_content{
            margin-bottom: 0.25em;
            text-align: left;
        }
        .close_button {
            float: right;
            position: relative;
            top: -0.1em;
            font-size: 1.3em;
            font-weight: bold;
            cursor: pointer;
            color: #656565ff;
        }
        .close_button:hover {
            color: black;
        }
        h3 {
            margin-bottom: 0.5em;
            font-weight: 600;
        }
    `;
    document.head.appendChild(style);

    const modal = document.getElementById("messages_modal");
    const closeBtn = modal.querySelector(".close_button");

    modal.style.display = "block";

    closeBtn.addEventListener("click", () => modal.style.display = "none");
    window.addEventListener("click", (e) => {
        if (e.target === modal) modal.style.display = "none";
    });
});
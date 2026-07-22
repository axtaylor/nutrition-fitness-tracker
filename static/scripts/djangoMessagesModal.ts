interface DjangoMessage {
    tags: string;
    text: string;
}

document.addEventListener("DOMContentLoaded", function () {

    const messageData = document.getElementById("django_messages");
    if (!messageData) return;

    const messages: DjangoMessage[] = JSON.parse(messageData.textContent);
    if (!messages.length) return;

    const messageItems = messages
        .map((m) => `<p class="pop_content ${m.tags}">${m.text}</p>`)
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
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);

    const activeModal = document.getElementById("messages_modal");
    if (!activeModal) return;

    const closeBtn = activeModal.querySelector(".close_button");
    if (!closeBtn) return;

    activeModal.style.display = "block";

    closeBtn.addEventListener("click", () => activeModal.style.display = "none");

    window.addEventListener("click", (e) => {
        if (e.target === activeModal) activeModal.style.display = "none";
    });
    
});
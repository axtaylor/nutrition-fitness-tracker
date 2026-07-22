document.addEventListener("DOMContentLoaded", function () {

    const guestElement = (document.getElementById('guest_check'));
    if (!guestElement) {
        return;
    }

    const isGuest : string = guestElement.textContent.toLowerCase();

    let modalHTML = ``;
    if (isGuest === "true") {
        modalHTML = `
        <div id="helpmodel" class="model_pop">
            <div class="model-content">
                <span class="close_button">&times;</span>
                <h3>Preview Mode</h3>
                <hr>
                <p class="pop_content">Select "Sign Out" from the left side menu to exit preview mode.</p>
            </div>
        </div>`;   
    }

    document.body.insertAdjacentHTML('beforeend', modalHTML);

    if (isGuest === "true") {

        const activeModal = document.getElementById("helpmodel");

        if (!activeModal) {
            return;
        }

        const closeButtonToggle = activeModal.querySelector(".close_button");

        if (!closeButtonToggle) {
            return;
        }

        activeModal.style.display = "block";

        closeButtonToggle.addEventListener("click", function () {
            activeModal.style.display = "none";
        });

        window.addEventListener("click", function (e) {
            if (e.target === activeModal) {
                activeModal.style.display = "none";
            }
        });
    }
    
});

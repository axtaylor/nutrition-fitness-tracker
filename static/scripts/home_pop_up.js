document.addEventListener("DOMContentLoaded", function () {
    const all_data = JSON.parse(document.getElementById('guest_check').textContent);
    let modelHTML = ``;

    if (all_data == true){

        modelHTML = `
        <div id="helpmodel" class="model_pop">
            <div class="model-content">
                <span class="close_button">&times;</span>
                <h3>Preview Mode</h3>
                <hr>
                <p class="pop_content">Select "Sign Out" from the left side menu to exit preview mode.</p>
            </div>
        </div>`;   
    }
    document.body.insertAdjacentHTML('beforeend', modelHTML);
    if (all_data === true){
        const model = document.getElementById("helpmodel");
        const close_button = model.querySelector(".close_button");
        model.style.display = "block";
        close_button.addEventListener("click", function () {
            model.style.display = "none";
        });
        window.addEventListener("click", function (e) {
            if (e.target === model) {
                model.style.display = "none";
            }
        });
    }
});

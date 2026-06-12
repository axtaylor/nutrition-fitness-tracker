document.addEventListener("DOMContentLoaded", function () {
    const id = JSON.parse(document.getElementById("log_info").textContent);
    let modelHTML = ``;

    if (id == "weightlog"){

        modelHTML = `
        <div id="helpmodel" class="model_pop">
            <div class="model-content">
                <span class="close_button">&times;</span>
                <h3>How To: Bodyweight</h3>
                <hr>
                <p class="pop_content">The bodyweight information entered will be used to calculate your rate of weight change
                over time.</p>
                <p class="pop_content">
                To optimize your caloric recommendations and fitness levels, it is recommended to track your bodyweight
                at minimum three times per week.</p>
            </div>
        </div>
    `;
        
    }
    else if (id == "nutritionlog") {

        modelHTML = `
        <div id="helpmodel" class="model_pop">
            <div class="model-content">
                <span class="close_button">&times;</span>
                <h3>How To: Nutrition</h3>
                <hr>                
                <p class="pop_content">Your caloric consumption will be used with your logged bodyweight changes
                to determine your maintenance, weight gain, and weight loss calorie amounts with high confidence. </p>

                <p class="pop_content">
                To optimize your recommendations, it is recommended to track your consumption
                on a daily basis.</p>

                <p class="pop_content">
                It is recommended to track consumption using nutrition labels and weighing portions.
                AI calorie photo scanners are inaccurate and will generate unreliable results.</p>
            </div>
        </div>
    `;

    }
    else if (id == "compositionlog") {

        modelHTML = `
        <div id="helpmodel" class="model_pop">
            <div class="model-content">
                <span class="close_button">&times;</span>
                <h3>How To: Composition</h3>
                <hr>
                <p class="pop_content">Methodology: US Navy</p>
                <p class="pop_content">For Men:</p>
                <p class="pop_content">Provide measurements of the waist, neck, and bodyweight to determine body composition metrics.</p>
                <p class="pop_content">For Women:</p>
                <p class="pop_content">Provide measurements of the waist, neck, hip, and bodyweight to determine body composition metrics.</p>
            </div>
        </div>
    `;
    }
    else {

        modelHTML = `
        <div id="helpmodel" class="model_pop">
            <div class="model-content">
                <span class="close_button">&times;</span>
                <h3>Error</h3>
                <p class="pop_content"></p>
            </div>
        </div>
    `;

    }
    document.body.insertAdjacentHTML('beforeend', modelHTML);
    const help_button = document.querySelector(".button.circle_button");
    const model = document.getElementById("helpmodel");
    const close_button = model.querySelector(".close_button");
    if (help_button) {
        help_button.addEventListener("click", function (e) {
            e.preventDefault(); 
            model.style.display = "block";
        });
    }
    close_button.addEventListener("click", function () {
        model.style.display = "none";
    });
    window.addEventListener("click", function (e) {
        if (e.target === model) {
            model.style.display = "none";
        }
    });
});

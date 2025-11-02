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



    document.body.insertAdjacentHTML("beforeend", modelHTML);
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

document.addEventListener('DOMContentLoaded', function () {

    // Inject "Or Manually Enter Daily Totals" label after the date field
    document.getElementById('id_date').insertAdjacentHTML('afterend', `
        <p class="manual-totals-label">Or Manually Enter Daily Totals</p>
    `);

    // Hide the response_html field from the user — it is managed programmatically
    document.getElementById('id_response_html').closest('p').classList.add('hidden-food');

    const modal = document.getElementById('foodModal');

    function showModalError(message) {
        const err = document.getElementById('foodModalError');
        err.textContent = message;
        err.classList.remove('hidden-food');
        clearTimeout(err._hideTimer);
        err._hideTimer = setTimeout(() => err.classList.add('hidden-food'), 3000);
    }

    // -------------------------------------------------------------------------
    // Modal open / close
    // -------------------------------------------------------------------------
    document.getElementById('openFoodModal').addEventListener('click', () => modal.style.display = 'block');
    document.getElementById('closeFoodModal').addEventListener('click', () => modal.style.display = 'none');
    // Close modal when clicking the backdrop
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.style.display = 'none'; });

    // -------------------------------------------------------------------------
    // Tab switching (Search / Custom Entry)
    // -------------------------------------------------------------------------
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(p => p.style.display = 'none');
            btn.classList.add('active');
            document.getElementById('tab-' + btn.dataset.tab).style.display = 'block';
        });
    });

    // -------------------------------------------------------------------------
    // Food search
    // -------------------------------------------------------------------------
    document.getElementById('foodSearchBtn').addEventListener('click', searchFoods);
    // Allow submitting search with Enter key
    document.getElementById('foodSearchInput').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') { e.preventDefault(); searchFoods(); }
    });

    function searchFoods() {
        const query = document.getElementById('foodSearchInput').value.trim();
        const resultsDiv = document.getElementById('searchResults');
        if (!query) return;

        resultsDiv.innerHTML = '<p style="color:#656565; font-size:0.9em;">Searching...</p>';
        fetch(`/api/food-search/?q=${encodeURIComponent(query)}`)
            .then(r => r.json())
            .then(data => {
                if (!data.length) {
                    resultsDiv.innerHTML = '<p style="color:#656565; font-size:0.9em;">No results found.</p>';
                    return;
                }
                // Cache results so selectFood() can reference them by index
                window._searchResults = data;
                resultsDiv.innerHTML = data.map((item, i) => `
                    <div class="search-result-item">
                        <div>
                            <div class="food-name">${item.name}</div>
                            <div class="food-macros">${item.calories} kcal &bull; P: ${item.protein}g &bull; F: ${item.fat}g &bull; C: ${item.carbs}g</div>
                        </div>
                        <button type="button" class="button" onclick="selectFood(${i})">Add</button>
                    </div>
                `).join('');
            })
            .catch(() => resultsDiv.innerHTML = '<p style="color:#c00; font-size:0.9em;">Search failed. Try again.</p>');
    }

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------

    function closeModal() {
        modal.style.display = 'none';
    }

    // Creates a food item element and appends it to the food list,
    // then syncs totals and saves the list HTML to the DB field
    function appendFoodItem(food) {
        const item = document.createElement('div');
        item.classList.add('food-list-item');
        // Store macro values as data attributes for use in updateTotals()
        Object.assign(item.dataset, { calories: food.calories, protein: food.protein, fat: food.fat, carbs: food.carbs });
        item.innerHTML = `
            <div class="food-list-name">${food.name}</div>
            <div class="food-list-macros">${food.calories} kcal &bull; P: ${food.protein}g &bull; F: ${food.fat}g &bull; C: ${food.carbs}g</div>
            <button type="button" class="food-list-remove" onclick="this.parentElement.remove(); updateTotals(); updateFoodHTML()">&times;</button>
        `;
        document.getElementById('foodList').appendChild(item);
        updateTotals();
        updateFoodHTML();
    }

    // Serializes the current food list HTML into id_response_html so it is
    // submitted with the form and persisted to the DB.
    // A space is stored when the list is empty to satisfy blank=False validation.
    window.updateFoodHTML = function () {
        const list = document.getElementById('foodList');
        document.getElementById('id_response_html').value = list.innerHTML.trim() || ' ';
    };

    // Shows or hides the manual macro input fields and their label.
    // Called by updateTotals() — hidden when food items are present,
    // visible again when the list is empty so the user can enter manually.
    function toggleManualFields(hide) {
        const fields = ['id_calories', 'id_protein', 'id_fat', 'id_carbs'];
        fields.forEach(id => document.getElementById(id).closest('p').style.display = hide ? 'none' : '');
        document.querySelector('.manual-totals-label').style.display = hide ? 'none' : '';
    }

    // -------------------------------------------------------------------------
    // Totals
    // Recalculates macro totals from all food-list-item data attributes,
    // updates the Django form fields, and syncs the totals display bar.
    // -------------------------------------------------------------------------
    window.updateTotals = function () {
        const items = document.querySelectorAll('.food-list-item');
        const totals = { calories: 0, protein: 0, fat: 0, carbs: 0 };

        items.forEach(item => {
            Object.keys(totals).forEach(key => totals[key] += parseFloat(item.dataset[key]) || 0);
        });

        // Always keep Django form fields in sync so POST data is accurate
        document.getElementById('id_calories').value = totals.calories.toFixed(1);
        document.getElementById('id_protein').value  = totals.protein.toFixed(1);
        document.getElementById('id_fat').value      = totals.fat.toFixed(1);
        document.getElementById('id_carbs').value    = totals.carbs.toFixed(1);

        const foodTotals = document.getElementById('foodTotals');

        // No items — hide totals bar and restore manual entry fields
        if (!items.length) {
            foodTotals.style.display = 'none';
            toggleManualFields(false);
            return;
        }

        // Items present — show totals bar and hide manual entry fields
        foodTotals.style.display = 'flex';
        toggleManualFields(true);
        document.getElementById('totalCalories').textContent = totals.calories.toFixed(1);
        document.getElementById('totalProtein').textContent  = totals.protein.toFixed(1)  + 'g';
        document.getElementById('totalFat').textContent      = totals.fat.toFixed(1)      + 'g';
        document.getElementById('totalCarbs').textContent    = totals.carbs.toFixed(1)    + 'g';
    };

    // -------------------------------------------------------------------------
    // Add food from search results (called via inline onclick)
    // -------------------------------------------------------------------------
    window.selectFood = function (index) {
        appendFoodItem(window._searchResults[index]);
        closeModal();
    };

    // -------------------------------------------------------------------------
    // Restore saved food items when editing an existing log entry
    // Saved HTML is injected back into the food list and remove buttons
    // have their handlers re-attached since onclick attributes are not
    // preserved when setting innerHTML from a stored value.
    // -------------------------------------------------------------------------
    const savedHTML = document.getElementById('id_response_html').value;
    if (savedHTML.trim()) {
        document.getElementById('foodList').innerHTML = savedHTML;
        document.querySelectorAll('.food-list-remove').forEach(btn => {
            btn.onclick = function () {
                this.parentElement.remove();
                updateTotals();
                updateFoodHTML();
            };
        });
        updateTotals();
    }

    // -------------------------------------------------------------------------
    // Custom food entry form submission
    // -------------------------------------------------------------------------
    document.getElementById('addCustomFood').addEventListener('click', () => {
        const name     = document.getElementById('customName').value.trim();
        const calories = document.getElementById('customCalories').value.trim();
        const protein  = document.getElementById('customProtein').value.trim();
        const fat      = document.getElementById('customFat').value.trim();
        const carbs    = document.getElementById('customCarbs').value.trim();

        if (!name) { showModalError('Please enter a food name.'); return; }
        const numericFields = [
            { value: calories, label: 'Calories' },
            { value: protein,  label: 'Protein'  },
            { value: fat,      label: 'Fat'      },
            { value: carbs,    label: 'Carbs'    },
        ];


        for (const field of numericFields) {
            if (field.value === '' || parseFloat(field.value) < 0) {
                showModalError(`${field.label} must be a valid number.`);
                return;
            }
        }

        const food = {
            name,
            calories: parseFloat(calories),
            protein:  parseFloat(protein),
            fat:      parseFloat(fat),
            carbs:    parseFloat(carbs),
        };

        appendFoodItem(food);
        closeModal();
    });
})
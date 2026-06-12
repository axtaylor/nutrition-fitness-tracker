document.addEventListener('DOMContentLoaded', function () {

    document.getElementById('id_date').insertAdjacentHTML('afterend', `
        <p class="manual-totals-label">Or Manually Enter Daily Totals</p>
    `);

    document.getElementById('id_response_html').closest('p').classList.add('hidden-food');

    const modal = document.getElementById('foodModal');

    // -------------------------------------------------------------------------
    // My Foods data
    // -------------------------------------------------------------------------
    const _savedFoods = [
        { name: 'Premier Protein Shake',             calories: 160,  protein: 30,    fat: 3,    carbs: 5   },
        { name: 'Fairlife Core Power 42g',               calories: 230,  protein: 42,    fat: 3.5,  carbs: 14  },
        { name: 'Fairlife Core Power 26g',               calories: 170,  protein: 26,    fat: 3,    carbs: 11  },
        { name: "McDonald's Double Big Mac",                    calories: 740,  protein: 38,    fat: 44,   carbs: 48  },
        { name: "McDonald's Spicy Bacon Deluxe McCrispy",     calories: 580,  protein: 34,    fat: 30,   carbs: 46  },
        { name: "Osmows Chicken Shawarma Poutine",      calories: 1165, protein: 37.87,  fat: 71.4, carbs: 81},
        { name: "Osmows Chicken on the Rocks",      calories: 857, protein: 40,  fat: 37.1, carbs: 81.33},
        { name: "Crave Buffalo Chicken Dinner",      calories: 570, protein: 24,  fat: 28, carbs: 56},
        { name: "Crave Bacon Macaroni Dinner",      calories: 530, protein: 25,  fat: 23, carbs: 55},
        { name: "Wendy's Spicy Asiago Ranch Chicken Club", calories: 590, protein: 33, fat: 30, carbs: 48},
        { name: "Wendy's Jr. Bacon Cheeseburger", calories: 390, protein: 19, fat: 24, carbs: 25},
        { name: "Wendy's Baconator Fries", calories: 410, protein: 12, fat: 23, carbs: 38},
        // Add here
        { name: 'Cheese Slice',                          calories: 50,   protein: 3,     fat: 4,    carbs: 1   },
        { name: 'Cheese Curds',                          calories: 110,   protein: 6,     fat: 8,    carbs: 1   },

    ];

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
    document.getElementById('openFoodModal').addEventListener('click', () => {
        clearEditState();
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(p => p.style.display = 'none');
        document.querySelector('.tab-btn[data-tab="myfood"]').classList.add('active');
        document.getElementById('tab-myfood').style.display = 'block';
        renderMyFoods(_savedFoods);
        modal.style.display = 'block';
    });

    document.getElementById('closeFoodModal').addEventListener('click', () => modal.style.display = 'none');
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.style.display = 'none'; });

    // -------------------------------------------------------------------------
    // Tab switching — single loop handles all tabs including My Food
    // -------------------------------------------------------------------------
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(p => p.style.display = 'none');
            btn.classList.add('active');
            document.getElementById('tab-' + btn.dataset.tab).style.display = 'block';
            if (btn.dataset.tab === 'myfood') renderMyFoods(_savedFoods);
        });
    });

    // -------------------------------------------------------------------------
    // Food search
    // -------------------------------------------------------------------------
    document.getElementById('foodSearchBtn').addEventListener('click', searchFoods);
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
        clearEditState();
    }

    let _editingItem = null;

    function openEditModal(item) {
        _editingItem = item;
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(p => p.style.display = 'none');
        document.querySelector('.tab-btn[data-tab="custom"]').classList.add('active');
        document.getElementById('tab-custom').style.display = 'block';
        document.getElementById('customName').value     = item.querySelector('.food-list-name').textContent;
        document.getElementById('customCalories').value = item.dataset.calories;
        document.getElementById('customProtein').value  = item.dataset.protein;
        document.getElementById('customFat').value      = item.dataset.fat;
        document.getElementById('customCarbs').value    = item.dataset.carbs;
        document.getElementById('addCustomFood').textContent = 'Save Changes';
        modal.style.display = 'block';
    }

    function clearEditState() {
        _editingItem = null;
        document.getElementById('addCustomFood').textContent = 'Add Food';
        document.getElementById('customName').value     = '';
        document.getElementById('customCalories').value = '';
        document.getElementById('customProtein').value  = '';
        document.getElementById('customFat').value      = '';
        document.getElementById('customCarbs').value    = '';
    }

    function appendFoodItem(food) {
        const item = document.createElement('div');
        item.classList.add('food-list-item');
        Object.assign(item.dataset, { calories: food.calories, protein: food.protein, fat: food.fat, carbs: food.carbs });
        item.innerHTML = `
            <div class="food-list-name">${food.name}</div>
            <div class="food-list-macros">${food.calories} kcal &bull; P: ${food.protein}g &bull; F: ${food.fat}g &bull; C: ${food.carbs}g</div>
            <button type="button" class="food-list-remove" onclick="this.parentElement.remove(); updateTotals(); updateFoodHTML()">&times;</button>
        `;
        item.querySelector('.food-list-name').addEventListener('click', () => openEditModal(item));
        item.querySelector('.food-list-macros').addEventListener('click', () => openEditModal(item));
        document.getElementById('foodList').appendChild(item);
        updateTotals();
        updateFoodHTML();
    }

    function attachEditListeners(item) {
        item.querySelector('.food-list-name').addEventListener('click', () => openEditModal(item));
        item.querySelector('.food-list-macros').addEventListener('click', () => openEditModal(item));
    }

    window.updateFoodHTML = function () {
        document.getElementById('id_response_html').value =
            document.getElementById('foodList').innerHTML.trim() || ' ';
    };

    function toggleManualFields(hide) {
        ['id_calories', 'id_protein', 'id_fat', 'id_carbs'].forEach(id =>
            document.getElementById(id).closest('p').style.display = hide ? 'none' : ''
        );
        document.querySelector('.manual-totals-label').style.display = hide ? 'none' : '';
    }

    // -------------------------------------------------------------------------
    // Totals
    // -------------------------------------------------------------------------
    window.updateTotals = function () {
        const items = document.querySelectorAll('.food-list-item');
        const totals = { calories: 0, protein: 0, fat: 0, carbs: 0 };
        items.forEach(item => {
            Object.keys(totals).forEach(key => totals[key] += parseFloat(item.dataset[key]) || 0);
        });

        document.getElementById('id_calories').value = totals.calories.toFixed(1);
        document.getElementById('id_protein').value  = totals.protein.toFixed(1);
        document.getElementById('id_fat').value      = totals.fat.toFixed(1);
        document.getElementById('id_carbs').value    = totals.carbs.toFixed(1);

        const foodTotals = document.getElementById('foodTotals');
        if (!items.length) {
            foodTotals.style.display = 'none';
            toggleManualFields(false);
            return;
        }

        foodTotals.style.display = 'flex';
        toggleManualFields(true);
        document.getElementById('totalCalories').textContent = totals.calories.toFixed(1);
        document.getElementById('totalProtein').textContent  = totals.protein.toFixed(1)  + 'g';
        document.getElementById('totalFat').textContent      = totals.fat.toFixed(1)      + 'g';
        document.getElementById('totalCarbs').textContent    = totals.carbs.toFixed(1)    + 'g';
    };

    // -------------------------------------------------------------------------
    // Add food from search results
    // -------------------------------------------------------------------------
    window.selectFood = function (index) {
        appendFoodItem(window._searchResults[index]);
        closeModal();
    };

    window.selectSavedFood = function (index) {
        appendFoodItem(_savedFoods[index]);
        closeModal();
    };

    // -------------------------------------------------------------------------
    // Restore saved food items on edit
    // -------------------------------------------------------------------------
    const savedHTML = document.getElementById('id_response_html').value;
    if (savedHTML.trim()) {
        document.getElementById('foodList').innerHTML = savedHTML;
        document.querySelectorAll('.food-list-item').forEach(item => {
            item.querySelector('.food-list-remove').onclick = function () {
                this.parentElement.remove();
                updateTotals();
                updateFoodHTML();
            };
            attachEditListeners(item);
        });
        updateTotals();
    }

    // -------------------------------------------------------------------------
    // My Foods render and filter
    // -------------------------------------------------------------------------
    function renderMyFoods(foods) {
        const container = document.getElementById('myFoodList');
        if (!foods.length) {
            container.innerHTML = '<p style="color:#656565; font-size:0.9em;">No matching foods.</p>';
            return;
        }
        container.innerHTML = foods.map((food, i) => `
            <div class="my-food-item">
                <div>
                    <div class="food-name">${food.name}</div>
                    <div class="food-macros">${food.calories} kcal &bull; P: ${food.protein}g &bull; F: ${food.fat}g &bull; C: ${food.carbs}g</div>
                </div>
                <button type="button" class="button" onclick="selectSavedFood(${i})">Add</button>
            </div>
        `).join('');
    }

    document.getElementById('myFoodSearch').addEventListener('input', (e) => {
        renderMyFoods(_savedFoods.filter(f => f.name.toLowerCase().includes(e.target.value.toLowerCase())));
    });

    // -------------------------------------------------------------------------
    // Custom food entry / edit form submission
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

        if (_editingItem) {
            Object.assign(_editingItem.dataset, food);
            _editingItem.querySelector('.food-list-name').textContent  = food.name;
            _editingItem.querySelector('.food-list-macros').textContent =
                `${food.calories} kcal • P: ${food.protein}g • F: ${food.fat}g • C: ${food.carbs}g`;
            updateTotals();
            updateFoodHTML();
        } else {
            appendFoodItem(food);
        }

        closeModal();
    });
});
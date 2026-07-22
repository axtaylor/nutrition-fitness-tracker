// Add Nutrition Log Menu
import { SavedFood, savedFoods } from "./globalNutritionData.js";

declare global {
    interface Window {
        _searchResults: SavedFood[];
        _renderedFoods: SavedFood[];
        selectFood: (index: number) => void;
        selectSavedFood: (index: number) => void;
        updateFoodHTML: () => void;
        updateTotals: () => void;
    }
}

interface Totals {
    calories: number;
    protein: number;
    fat: number;
    carbs: number;
}

document.addEventListener('DOMContentLoaded', function () {

    const afterDateElement = document.getElementById('id_date');
    if (!afterDateElement) return;

    afterDateElement
        .insertAdjacentHTML('afterend', `<p class="manual-totals-label">Manually Enter Daily Totals</p>`);

    // Hidden pre-populated django form item
    const responseHTMLFormElement = document.getElementById('id_response_html') as HTMLInputElement | null;
    if (!responseHTMLFormElement) return;

    const responseHTMLFormData = responseHTMLFormElement.closest('p');
    if (!responseHTMLFormData) return;
    responseHTMLFormData.classList.add('hidden-food');

    const modal = document.getElementById('foodModal');
    if (!modal) return;

    const _savedFoods: SavedFood[] = savedFoods;
    if (!_savedFoods) return;

    // -------------------------------------------------------------------------
    // Error view
    // -------------------------------------------------------------------------
    function showModalError(message: string): void {

        const err = document.getElementById('foodModalError');
        if (!err) return;

        err.textContent = message;
        err.classList.remove('hidden-food');

        clearTimeout((err as any)._hideTimer);
        (err as any)._hideTimer = setTimeout(() => err.classList.add('hidden-food'), 3000);
    }

    // -------------------------------------------------------------------------
    // Modal open / close
    // -------------------------------------------------------------------------
    let _editingItem: HTMLElement | null = null;

    function clearEditState(): void {
        _editingItem = null;

        const addBtn = document.getElementById('addCustomFood');
        if (addBtn) addBtn.textContent = 'Add';

        const nameInput = document.getElementById('customName') as HTMLInputElement | null;
        if (nameInput) nameInput.value = '';

        const caloriesInput = document.getElementById('customCalories') as HTMLInputElement | null;
        if (caloriesInput) caloriesInput.value = '';

        const proteinInput = document.getElementById('customProtein') as HTMLInputElement | null;
        if (proteinInput) proteinInput.value = '';

        const fatInput = document.getElementById('customFat') as HTMLInputElement | null;
        if (fatInput) fatInput.value = '';

        const carbsInput = document.getElementById('customCarbs') as HTMLInputElement | null;
        if (carbsInput) carbsInput.value = '';
    }

    const openButton = document.getElementById('openFoodModal');
    if (!openButton) return;

    openButton.addEventListener('click', () => {

        clearEditState();

        document.querySelectorAll<HTMLElement>('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll<HTMLElement>('.tab-panel').forEach(p => p.style.display = 'none');

        const myFoodTabBtn = document.querySelector('.tab-btn[data-tab="myfood"]');
        if (myFoodTabBtn) myFoodTabBtn.classList.add('active');

        const myFoodPanel = document.getElementById('tab-myfood');
        if (myFoodPanel) myFoodPanel.style.display = 'block';

        renderMyFoods(_savedFoods);
        modal.style.display = 'block';
    });

    function closeModal(): void {
        if (!modal) return;
        modal.style.display = 'none';
        clearEditState();
    }

    const closeButton = document.getElementById('closeFoodModal');
    if (!closeButton) return;

    closeButton.addEventListener('click', () => {
        closeModal();
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // -------------------------------------------------------------------------
    // Tab Switching
    // -------------------------------------------------------------------------
    document.querySelectorAll<HTMLElement>('.tab-btn').forEach(btn => {

        btn.addEventListener('click', () => {

            document.querySelectorAll<HTMLElement>('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll<HTMLElement>('.tab-panel').forEach(p => p.style.display = 'none');
            btn.classList.add('active');

            const tabName = btn.dataset.tab;
            if (!tabName) return;

            const panel = document.getElementById('tab-' + tabName);
            if (panel) panel.style.display = 'block';

            if (tabName === 'myfood') renderMyFoods(_savedFoods);
        });
    });

    // -------------------------------------------------------------------------
    // Helpers
    // -------------------------------------------------------------------------
    function openEditModal(item: HTMLElement): void {
        _editingItem = item;

        document.querySelectorAll<HTMLElement>('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll<HTMLElement>('.tab-panel').forEach(p => p.style.display = 'none');

        const customTabBtn = document.querySelector('.tab-btn[data-tab="custom"]');
        if (customTabBtn) customTabBtn.classList.add('active');

        const customPanel = document.getElementById('tab-custom');
        if (customPanel) customPanel.style.display = 'block';

        const nameEl = item.querySelector('.food-list-name');
        const nameInput = document.getElementById('customName') as HTMLInputElement | null;
        if (nameInput) nameInput.value = nameEl?.textContent ?? '';

        const caloriesInput = document.getElementById('customCalories') as HTMLInputElement | null;
        if (caloriesInput) caloriesInput.value = item.dataset.calories ?? '';

        const proteinInput = document.getElementById('customProtein') as HTMLInputElement | null;
        if (proteinInput) proteinInput.value = item.dataset.protein ?? '';

        const fatInput = document.getElementById('customFat') as HTMLInputElement | null;
        if (fatInput) fatInput.value = item.dataset.fat ?? '';

        const carbsInput = document.getElementById('customCarbs') as HTMLInputElement | null;
        if (carbsInput) carbsInput.value = item.dataset.carbs ?? '';

        const addBtn = document.getElementById('addCustomFood');
        if (addBtn) addBtn.textContent = 'Save Changes';

        if (modal) modal.style.display = 'block';
    }

    function appendFoodItem(food: SavedFood): void {

        const item = document.createElement('div');
        item.classList.add('food-list-item');

        Object.assign(item.dataset, {
            calories: String(food.calories),
            protein: String(food.protein),
            fat: String(food.fat),
            carbs: String(food.carbs),
        });

        item.innerHTML = `
            <div class="food-list-name">${food.name}</div>
            <div class="food-list-macros">${food.calories} kcal &bull; P: ${food.protein}g &bull; F: ${food.fat}g &bull; C: ${food.carbs}g</div>
            <button type="button" class="food-list-remove" onclick="this.parentElement.remove(); updateTotals(); updateFoodHTML()">&times;</button>
        `;

        const nameElement = item.querySelector('.food-list-name');
        const macrosElement = item.querySelector('.food-list-macros');

        if (nameElement) nameElement.addEventListener('click', () => openEditModal(item));
        if (macrosElement) macrosElement.addEventListener('click', () => openEditModal(item));

        const foodList = document.getElementById('foodList');
        if (foodList) foodList.appendChild(item);

        window.updateTotals();
        window.updateFoodHTML();
    }

    function attachEditListeners(item: HTMLElement): void {
        const nameElement = item.querySelector('.food-list-name');
        const macrosElement = item.querySelector('.food-list-macros');

        if (nameElement) nameElement.addEventListener('click', () => openEditModal(item));
        if (macrosElement) macrosElement.addEventListener('click', () => openEditModal(item));
    }

    window.updateFoodHTML = function (): void {
        const responseInput = document.getElementById('id_response_html') as HTMLInputElement | null;
        const foodList = document.getElementById('foodList');

        if (responseInput && foodList) {
            responseInput.value = foodList.innerHTML.trim() || ' ';
        }
    };

    function toggleManualFields(hide: boolean): void {
        ['id_calories', 'id_protein', 'id_fat', 'id_carbs'].forEach(id => {
            const el = document.getElementById(id);
            const wrapper = el?.closest('p');
            if (wrapper) (wrapper as HTMLElement).style.display = hide ? 'none' : '';
        });

        const label = document.querySelector('.manual-totals-label');
        if (label) (label as HTMLElement).style.display = hide ? 'none' : '';
    }

    // -------------------------------------------------------------------------
    // Totals
    // -------------------------------------------------------------------------
    window.updateTotals = function (): void {
        const items = document.querySelectorAll<HTMLElement>('.food-list-item');
        const totals: Totals = { calories: 0, protein: 0, fat: 0, carbs: 0 };

        items.forEach(item => {
            (Object.keys(totals) as (keyof Totals)[]).forEach(key => {
                totals[key] += parseFloat(item.dataset[key] ?? '') || 0;
            });
        });

        const caloriesInput = document.getElementById('id_calories') as HTMLInputElement | null;
        const proteinInput = document.getElementById('id_protein') as HTMLInputElement | null;
        const fatInput = document.getElementById('id_fat') as HTMLInputElement | null;
        const carbsInput = document.getElementById('id_carbs') as HTMLInputElement | null;

        if (caloriesInput) caloriesInput.value = totals.calories.toFixed(1);
        if (proteinInput) proteinInput.value = totals.protein.toFixed(1);
        if (fatInput) fatInput.value = totals.fat.toFixed(1);
        if (carbsInput) carbsInput.value = totals.carbs.toFixed(1);

        const foodTotals = document.getElementById('foodTotals');
        if (!foodTotals) return;

        if (!items.length) {
            foodTotals.style.display = 'none';
            toggleManualFields(false);
            return;
        }

        foodTotals.style.display = 'flex';
        toggleManualFields(true);

        const protein_pct = ((totals.protein * 4) / totals.calories) * 100;
        const fat_pct = ((totals.fat * 9) / totals.calories) * 100;
        const carb_pct = ((totals.carbs * 4) / totals.calories) * 100;
        //let extra = 100-(protein_pct+fat_pct+carb_pct);
        //fat_pct+=extra;

        const totalCalories = document.getElementById('totalCalories');
        const totalProtein = document.getElementById('totalProtein');
        const totalFat = document.getElementById('totalFat');
        const totalCarbs = document.getElementById('totalCarbs');

        if (totalCalories) totalCalories.textContent = totals.calories.toFixed(1);
        if (totalProtein) totalProtein.textContent = totals.protein.toFixed(1) + 'g';
        if (totalFat) totalFat.textContent = totals.fat.toFixed(1) + 'g';
        if (totalCarbs) totalCarbs.textContent = totals.carbs.toFixed(1) + 'g';

        const totalProteinPct = document.getElementById('totalProteinPct');
        const totalFatPct = document.getElementById('totalFatPct');
        const totalCarbsPct = document.getElementById('totalCarbsPct');

        if (totalProteinPct) totalProteinPct.textContent = '(' + protein_pct.toFixed(1) + '%)';
        if (totalFatPct) totalFatPct.textContent = '(' + fat_pct.toFixed(1) + '%)';
        if (totalCarbsPct) totalCarbsPct.textContent = '(' + carb_pct.toFixed(1) + '%)';
    };

    // -------------------------------------------------------------------------
    // Add food from search results
    // -------------------------------------------------------------------------
    window.selectFood = function (index: number): void {
        appendFoodItem(window._searchResults[index]);
        closeModal();
    };

    window.selectSavedFood = function (index: number): void {
        appendFoodItem(window._renderedFoods[index]);
        closeModal();
    };

    // -------------------------------------------------------------------------
    // Restore saved food items on edit
    // -------------------------------------------------------------------------
    const savedHTML = responseHTMLFormElement.value;
    if (savedHTML.trim()) {
        const foodList = document.getElementById('foodList');
        if (foodList) foodList.innerHTML = savedHTML;

        document.querySelectorAll<HTMLElement>('.food-list-item').forEach(item => {
            const removeBtn = item.querySelector('.food-list-remove') as HTMLElement | null;
            if (removeBtn) {
                removeBtn.onclick = function () {
                    item.remove();
                    window.updateTotals();
                    window.updateFoodHTML();
                };
            }
            attachEditListeners(item);
        });

        window.updateTotals();
    }

    // -------------------------------------------------------------------------
    // My Foods render and filter
    // -------------------------------------------------------------------------
    function renderMyFoods(foods: SavedFood[]): void {
        const container = document.getElementById('myFoodList');
        if (!container) return;

        if (!foods.length) {
            container.innerHTML = '<p style="color:#656565; font-size:0.9em;">No matching foods.</p>';
            return;
        }

        // Store the currently rendered list so selectSavedFood indexes into it correctly
        window._renderedFoods = foods;

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

    const myFoodSearch = document.getElementById('myFoodSearch') as HTMLInputElement | null;
    if (myFoodSearch) {
        myFoodSearch.addEventListener('input', (e) => {
            const value = (e.target as HTMLInputElement).value.toLowerCase();
            renderMyFoods(_savedFoods.filter(f => f.name.toLowerCase().includes(value)));
        });
    }

    // -------------------------------------------------------------------------
    // Custom food entry / edit form submission
    // -------------------------------------------------------------------------
    const addCustomFoodBtn = document.getElementById('addCustomFood');
    if (addCustomFoodBtn) {
        addCustomFoodBtn.addEventListener('click', () => {
            const nameInput = document.getElementById('customName') as HTMLInputElement | null;
            const caloriesInput = document.getElementById('customCalories') as HTMLInputElement | null;
            const proteinInput = document.getElementById('customProtein') as HTMLInputElement | null;
            const fatInput = document.getElementById('customFat') as HTMLInputElement | null;
            const carbsInput = document.getElementById('customCarbs') as HTMLInputElement | null;

            if (!nameInput || !caloriesInput || !proteinInput || !fatInput || !carbsInput) return;

            const name = nameInput.value.trim();
            const calories = caloriesInput.value.trim();
            const protein = proteinInput.value.trim();
            const fat = fatInput.value.trim();
            const carbs = carbsInput.value.trim();

            if (!name) { showModalError('Please enter a food name.'); return; }

            const numericFields = [
                { value: calories, label: 'Calories' },
                { value: protein, label: 'Protein' },
                { value: fat, label: 'Fat' },
                { value: carbs, label: 'Carbs' },
            ];

            for (const field of numericFields) {
                if (field.value === '' || parseFloat(field.value) < 0) {
                    showModalError(`${field.label} must be a valid number.`);
                    return;
                }
            }

            const food: SavedFood = {
                name,
                calories: parseFloat(calories),
                protein: parseFloat(protein),
                fat: parseFloat(fat),
                carbs: parseFloat(carbs),
            };

            if (_editingItem) {
                Object.assign(_editingItem.dataset, {
                    name: String(food.name),
                    calories: String(food.calories),
                    protein: String(food.protein),
                    fat: String(food.fat),
                    carbs: String(food.carbs),
                });

                const nameEl = _editingItem.querySelector('.food-list-name');
                const macrosEl = _editingItem.querySelector('.food-list-macros');

                if (nameEl) nameEl.textContent = food.name;
                if (macrosEl) {
                    macrosEl.textContent =
                        `${food.calories} kcal • P: ${food.protein}g • F: ${food.fat}g • C: ${food.carbs}g`;
                }

                window.updateTotals();
                window.updateFoodHTML();
            } else {
                appendFoodItem(food);
            }

            closeModal();
        });
    }
});
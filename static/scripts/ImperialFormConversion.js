"use strict";
document.addEventListener("DOMContentLoaded", () => {
    const unitsField = document.getElementById("id_units");
    if (!unitsField)
        return;
    const heightField = document.getElementById("id_height");
    if (!heightField)
        return;
    const imperialDiv = document.getElementById("imperialHeightFields");
    if (!imperialDiv)
        return;
    const feetInput = document.getElementById("heightFeet");
    if (!feetInput)
        return;
    const inchesInput = document.getElementById("heightInches");
    if (!inchesInput)
        return;
    function inchesToFeetInches(totalInches) {
        return {
            feet: Math.floor(totalInches / 12),
            inches: totalInches % 12,
        };
    }
    function updateHeightInches() {
        const feet = parseFloat(feetInput.value) || 0;
        const inches = parseFloat(inchesInput.value) || 0;
        heightField.value = String((feet * 12) + inches);
    }
    function toggleHeightFields() {
        const isImperial = unitsField.value === "Imperial";
        const heightContainer = heightField.closest("p");
        if (heightContainer) {
            heightContainer.style.display = isImperial ? "none" : "";
        }
        imperialDiv.style.display = isImperial ? "block" : "none";
        if (isImperial && heightField.value) {
            const { feet, inches } = inchesToFeetInches(parseFloat(heightField.value));
            feetInput.value = String(feet);
            inchesInput.value = String(inches);
        }
    }
    toggleHeightFields();
    unitsField.addEventListener("change", toggleHeightFields);
    feetInput.addEventListener("input", updateHeightInches);
    inchesInput.addEventListener("input", updateHeightInches);
});

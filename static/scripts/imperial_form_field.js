document.addEventListener('DOMContentLoaded', function () {
    const unitsField  = document.getElementById('id_units');
    const heightField = document.getElementById('id_height');
    const imperialDiv = document.getElementById('imperialHeightFields');
    const feetInput   = document.getElementById('heightFeet');
    const inchesInput = document.getElementById('heightInches');

    function inchesToFeetInches(totalInches) {
        return {
            feet:   Math.floor(totalInches / 12),
            inches: totalInches % 12,
        };
    }

    function updateHeightInches() {
        const feet   = parseFloat(feetInput.value)   || 0;
        const inches = parseFloat(inchesInput.value) || 0;
        heightField.value = (feet * 12) + inches;
    }

    function toggleHeightFields() {
        const isImperial = unitsField.value === 'Imperial';

        heightField.closest('p').style.display = isImperial ? 'none' : '';
        imperialDiv.style.display = isImperial ? 'block' : 'none';

        if (isImperial && heightField.value) {
            const { feet, inches } = inchesToFeetInches(parseFloat(heightField.value));
            feetInput.value   = feet;
            inchesInput.value = inches;
        }
    }

    toggleHeightFields();
    unitsField.addEventListener('change', toggleHeightFields);
    feetInput.addEventListener('input', updateHeightInches);
    inchesInput.addEventListener('input', updateHeightInches);
});
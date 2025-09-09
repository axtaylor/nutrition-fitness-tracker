let current_data_type = 'weight';
let current_period = '28';
let chart;

function get_label_for(type) {
    const labels = {
        'weight': 'Weight',
        'bodyfat': 'Body Fat %',
        'lean_mass': 'Lean Mass',
        'fat_mass': 'Fat Mass',
        'calories': 'Calories',
        'protein': 'Protein',
        'carbs': 'Carbs',
        'fat': 'Fat',
    };
    return labels[type] || type;
}

function get_axis_range(data) {
    const filtered_data = data.filter(v => v !== null);
    if (filtered_data.length === 0) {
        return { max: 5, min: 0 }; // Default range if no data
    }
    return {
        max: Math.max(...filtered_data),
        min: Math.min(...filtered_data),
    }
}
// Initialize the first chart element on the DOM
function display_chart() {
    // Grab the data from python 
    const all_data = JSON.parse(document.getElementById('chart_data').textContent);
    // New chart based on canvas HTML element
    const ctx = document.getElementById('weight_chart').getContext('2d');
    // Loads all the timeframe data for weight, bodyfat...
    const current_data = all_data[current_data_type];
    // all_data['weight']['labels_28'] = [2025-01-01, null, ...n=28]
    const labels = current_data[`labels_${current_period}`] || [];
    // all_data['weight']['data_28'] = [190, 180, null, ...n=28]
    const data = current_data[`data_${current_period}`] || [];
    const { min, max } = get_axis_range(data);
    //const variance = getVariance(current_period);
    // color toggle for light/dark view.
    const chartColor = getComputedStyle(document.documentElement).getPropertyValue('--chart-color').trim();
    const chart_border = getComputedStyle(document.documentElement).getPropertyValue('--chart-border').trim();
    // Empty h2 on the div use the label from the data to fill it
    const chart_header = document.getElementById('chart_header');
    if (chart_header) {
        chart_header.textContent = get_label_for(current_data_type);
    }

    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: get_label_for(current_data_type),
                data: data,
                spanGaps: true,
                fill: true,
                backgroundColor: 'rgba(79, 172, 254, 0.1)',
                borderColor: '#4facfe',
                borderWidth: 3,
                clip: false,
                tension: 0.15, 
                pointBackgroundColor: '#4facfe',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 0,
                pointRadius: 0,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: '#4facfe',
                pointHoverBorderColor: '#ffffff'
            }]
        },
        options: {
            color: chartColor,
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: 0,
            }, 
            interaction: {
                intersect: false,
                mode: 'index',
            },
            plugins: {
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#4facfe',
                    borderWidth: 1,
                },
                legend: {
                    display: false,
                    labels: {
                        color: chartColor,
                        font: {
                            size: 15,
                        },
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: chartColor,
                        maxRotation: 0,
                        autoSkip: false,
                        padding: 15,
                        font: {
                            size: 11,
                
                        },
                        callback: function(value, index, ticks) {
                            const label = this.getLabelForValue(value);
                            const date = new Date(label + "T00:00:00");
                            if (current_period === '365'){
                                if ([0, Math.floor(ticks.length/2), Math.floor(ticks.length/4),  Math.floor(3*ticks.length/4), ticks.length-1].includes(index)) {
                                    return date.toLocaleDateString('en-US', { 
                                        day: 'numeric',
                                        month: 'numeric',
                                        year: 'numeric' 
                                    });
                                }
                                return '';
                            }
                            else if (current_period === '28'){
                                if ([0, Math.floor(ticks.length/2),  Math.floor(ticks.length/4),  Math.floor(3*ticks.length/4), ticks.length-1].includes(index)) {
                                    return date.toLocaleDateString('en-US', { 
                                        month: 'short',
                                        day: 'numeric',
                                       
                                    });
                                }
                                return '';
                            }
                            else{
                                if (index === 0 || index) {
                                    return date.toLocaleDateString('en-US', { 
                                        month: 'short',
                                        day: 'numeric' 
                                    });
                                }
                                return "";
                            }
                        }
                    },
                    grid: {
                        display: false,
                        color: chart_border
                    },
                    border:{
                        color: chart_border,
                    }
                },
                y: {
                    min: Math.max(0, Math.floor(min / 5) * 5),
                    max: Math.ceil(max / 5) * 5,
                    ticks: {
                        color: chartColor,
                        stepSize: 2.5,
                        font: {
                            size: 14,
                        },
                    },
                    grid: {
                        display: true,
                        color: chart_border
                    },
                    border:{
                        color: chart_border 
                    }
                }
            }
        }
    });
}

function updateChart() {
    // Refreshing the data or time frame
    const all_data = JSON.parse(document.getElementById('chart_data').textContent);
    const current_data = all_data[current_data_type];
    const labels = current_data[`labels_${current_period}`] || [];
    const data = current_data[`data_${current_period}`] || [];
    const { min, max } = get_axis_range(data);

    chart.data.labels = labels;
    chart.data.datasets[0].data = data;
    chart.data.datasets[0].label = get_label_for(current_data_type);
    chart.options.scales.y.max = Math.floor(max + 2);
    chart.options.scales.y.min = Math.floor(Math.max(0, min - 2));
    chart.options.scales.y.ticks.stepSize = 2;

    if (current_data_type === "bodyfat"){
        chart.options.scales.y.ticks.stepSize = 1
    }
    if (current_data_type === "lean_mass"){
        chart.options.scales.y.ticks.stepSize = 5;
    }
    if (current_data_type === "fat_mass"){
        chart.options.scales.y.ticks.stepSize = 5;
    }
    if (current_data_type === "calories"){
        chart.options.scales.y.ticks.stepSize = 100;
        chart.options.scales.y.max = (Math.round(Math.floor(max + 100) / 100)*100);
        chart.options.scales.y.min = Math.round(Math.max(0, Math.floor(min - 100))/100)*100
    }
    if (current_data_type === "weight"){
        chart.options.scales.y.ticks.stepSize = 10;
        if (current_period === '365'){
            chart.options.scales.y.max = (Math.round(Math.floor(max + 10) / 10)*10);
            chart.options.scales.y.min = Math.round(Math.max(0, Math.floor(min - 10))/10)*10
        }
        else if (current_period === "28"){
            chart.options.scales.y.min = Math.max(0, Math.floor(min / 5) * 5);
            chart.options.scales.y.max = Math.ceil(max / 5) * 5;
            chart.options.scales.y.ticks.stepSize = 2.5;

        }
    }
    const chart_header = document.getElementById('chart_header');
    if (chart_header) {
        chart_header.textContent = get_label_for(current_data_type);
    }
    chart.update();
}

// Timeframe button activity sensor
function set_active_button(activeButton) {
    const buttons = document.querySelectorAll('.chartbuttons button');
    buttons.forEach((btn) => {
        btn.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
    });
    activeButton.style.backgroundColor = 'rgba(0, 170, 255, 0.39)';
}

// DOM event listener
document.addEventListener('DOMContentLoaded', function() {

    // Grab the select box and use it to apply local var current data type to the mapped value
    const data_selector = document.getElementById('data-selector');
        if (data_selector && data_selector.options.length > 0) {
        data_selector.selectedIndex = 0;
        current_data_type = data_selector.value;
    }
    display_chart();

    const buttons = document.querySelectorAll('.chartbuttons button');
    if (buttons.length >= 3) {
        buttons[2].addEventListener('click', () => {
            current_period = '7';
            updateChart();
            set_active_button(buttons[2]);
        });
        buttons[1].addEventListener('click', () => {
            current_period = '28';
            updateChart();
            set_active_button(buttons[1]);
        });
        buttons[0].addEventListener('click', () => {
            current_period = '365';
            updateChart();
            set_active_button(buttons[0]);
        });
        set_active_button(buttons[1]);
    }
    if (data_selector) {
        data_selector.addEventListener('change', (e) => {
            current_data_type = e.target.value;
            updateChart();
        });
    }
});
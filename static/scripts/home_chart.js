const dom_cache_dict = {};
const chart_instances = {};

// Cache these elements in the DOM since the other app features are seperate pages
function cache_data() {
    dom_cache_dict.chart_data_json = document.getElementById('chart_data');
    dom_cache_dict.weight_chart_obj = document.getElementById('weight_chart');
    dom_cache_dict.comp_chart_obj = document.getElementById('comp_chart');
    dom_cache_dict.cal_chart_obj = document.getElementById('cal_chart');

    dom_cache_dict.bfVal = document.querySelector('.macro-value.bf');
    dom_cache_dict.lmVal = document.querySelector('.macro-value.lm');
    dom_cache_dict.fmVal = document.querySelector('.macro-value.fm');
}
// Cleanup function for the cached data
function dom_cleanup() {
    Object.values(chart_instances).forEach(chart => {
        if (chart && typeof chart.destroy === 'function') {
            chart.destroy();
        }
    });
}

// For the weight chart
function get_axes_range(data) {
    if (!data || !Array.isArray(data)) return { max: 5, min: 0 };
    const filtered_data = data.filter(v => v !== null && v !== undefined && !isNaN(v));
    if (filtered_data.length === 0) return { max: 5, min: 0 };
    
    const min = Math.min(...filtered_data);
    const max = Math.max(...filtered_data);
    return { max, min };
}

function load_charts() {
    try {
        cache_data();
        if (!dom_cache_dict.chart_data_json) {
            console.error('Chart data element not found?');
            return;
        }
        const all_data = JSON.parse(dom_cache_dict.chart_data_json.textContent);
        
        const CURRENT_PERIOD_NUTRITION = '365';
        const CURRENT_PERIOD_COMP = '1';

        const protein = all_data.protein || {};
        const fat = all_data.fat || {};
        const carbs = all_data.carbs || {};
        const calories = all_data.calories || {};

        full_cal_labels = calories[`labels_${CURRENT_PERIOD_NUTRITION}`] || [];
        full_cal_data = calories[`data_${CURRENT_PERIOD_NUTRITION}`] || [];
        full_p_bar_data = protein[`data_${CURRENT_PERIOD_NUTRITION}`] || [];
        full_f_bar_data = fat[`data_${CURRENT_PERIOD_NUTRITION}`] || [];
        full_c_bar_data = carbs[`data_${CURRENT_PERIOD_NUTRITION}`] || [];
        
        max_weeks = Math.ceil(full_cal_labels.length / 7);
        current_week_index = max_weeks - 1; 

        const weight = all_data.weight || {};
        const weight_labels = weight[`labels_${CURRENT_PERIOD_WEIGHT}`] || [];
        const weight_data = weight[`data_${CURRENT_PERIOD_WEIGHT}`] || [];
        const { min, max } = get_axes_range(weight_data);

        const body_fat = all_data.bodyfat || {};
        const lean_mass = all_data.lean_mass || {};
        const fat_mass = all_data.fat_mass || {};
        const bf_data = body_fat[`data_${CURRENT_PERIOD_COMP}`] || 0;
        const lm_data = lean_mass[`data_${CURRENT_PERIOD_COMP}`] || 0;
        const fm_data = fat_mass[`data_${CURRENT_PERIOD_COMP}`] || 0;
        update_composition_cache(bf_data, lm_data, fm_data);

        if (dom_cache_dict.weight_chart_obj && dom_cache_dict.weight_chart_obj.getContext) {
            const weightCtx = dom_cache_dict.weight_chart_obj.getContext('2d');
            chart_instances.weight = new Chart(weightCtx, weight_chart_config(weight_labels, weight_data, min, max));
        }
        if (dom_cache_dict.comp_chart_obj && dom_cache_dict.comp_chart_obj.getContext) {
            const compCtx = dom_cache_dict.comp_chart_obj.getContext('2d');
            chart_instances.comp = new Chart(compCtx, composition_chart_config([lm_data, fm_data]));
        }

        if (dom_cache_dict.cal_chart_obj && dom_cache_dict.cal_chart_obj.getContext) {
            const calCtx = dom_cache_dict.cal_chart_obj.getContext('2d');
            current_week_index = 0;
            const initial_week_data = get_week_data_non_overlapping(current_week_index);
            chart_instances.cal = new Chart(calCtx, calories_chart_config(
                initial_week_data.labels,
                initial_week_data.cal_data,
                initial_week_data.p_data.map(p => p * 4),
                initial_week_data.f_data.map(f => f * 9), 
                initial_week_data.c_data.map(c => c * 4)  
            ));
            connect_navigation_buttons();
            update_navigation_buttons();
        }
    } catch (error) {
        console.error('Data log error', error);
    }
}

document.addEventListener('DOMContentLoaded', load_charts);
window.addEventListener('beforeunload', dom_cleanup);


/*

BODYWEIGHT CHART

*/
function weight_chart_config(labels, data, min, max) {
    return {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Weight',
                data: data,
                borderColor: '#4facfe',
                backgroundColor: 'rgba(79, 172, 254, 0.1)',
                borderWidth: 3,
                fill: true,
                spanGaps: true,
                tension: 0.4,
                pointBackgroundColor: '#4facfe',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 0,
                pointRadius: 0,
                pointHoverRadius: 0,
                pointHoverBackgroundColor: '#4facfe',
                pointHoverBorderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#4facfe',
                    borderWidth: 0,
                    callbacks: {
                        label: function(context) {
                            return `Weight: ${context.parsed.y} Lbs`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        maxRotation: 0,
                        autoSkip: false,
                        padding: 10,
                        font: { size: 11 },
                        callback: function(value, index, ticks) {
                            const label = this.getLabelForValue(value);
                            const date = new Date(label + "T00:00:00");
                            const custom_index = [0, Math.floor(ticks.length/4), Math.floor(ticks.length/2), Math.floor(3*ticks.length/4), ticks.length-1];
                            if (custom_index.includes(index)) {
                                return date.toLocaleDateString('en-US', { 
                                    month: 'short',
                                    day: 'numeric'
                                });
                            }
                            return '';
                        }
                    }
                },
                y: {
                    grid: { display: true },
                    ticks: {
                        font: { size: 11 },
                        stepSize: STEP_SIZE,
                        callback: function(value) {
                            return value/*value + ' Lbs'*/;
                        }
                    },
                    min: Math.max(0, Math.floor(min / 5) * 5),
                    max: Math.ceil(max / 5) * 5
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    };
}
// Timeframe button activity sensor
let CURRENT_PERIOD_WEIGHT = "365";
let STEP_SIZE = 5
function set_active_button(active_button) {
    const buttons = document.querySelectorAll('.chartbuttons button');
    buttons.forEach((btn) => {
        btn.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
    });
    active_button.style.backgroundColor = 'rgba(0, 170, 255, 0.39)';
}
document.addEventListener('DOMContentLoaded', function() { 
    const buttons = document.querySelectorAll('.chartbuttons button');
    if (buttons.length >= 2) {
        buttons[1].addEventListener('click', () => {
            CURRENT_PERIOD_WEIGHT = '365';
            dom_cleanup();
            STEP_SIZE = 5
            load_charts();
            set_active_button(buttons[1]);
        });
        buttons[0].addEventListener('click', () => {
            CURRENT_PERIOD_WEIGHT = '28';
            dom_cleanup();
            STEP_SIZE = 2.5
            load_charts();
            set_active_button(buttons[0]);
        });
        set_active_button(buttons[1]);
    }
});


/*

BODY COMPOSITION CHART

*/
function composition_chart_config(data) {
    return {
        type: 'doughnut',
        data: {
            labels: ['Lean Mass', 'Fat Mass'],
            datasets: [{
                data: data,
                backgroundColor: ['#ff974dff', '#69A1E2'],
                borderColor: ['#ff974dff', '#69A1E2'],
                borderWidth: 2,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const total = context.dataset.data
                                .filter(v => v != null)            // drop null/undefined
                                .reduce((a, b) => a + Number(b), 0); // force to number
                            const percentage = total > 0 
                                ? Math.round((value / total) * 100) 
                                : 0;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    },
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#4facfe',
                    borderWidth: 1
                }
            },
            cutout: '60%',
            animation: {
                animateRotate: true,
                duration: 1000
            }
        }
    };
}

function update_composition_cache(bf_data, lm_data, fm_data) {
    if (dom_cache_dict.bfVal) dom_cache_dict.bfVal.textContent = `${bf_data}%`;
    if (dom_cache_dict.lmVal) dom_cache_dict.lmVal.textContent = lm_data;
    if (dom_cache_dict.fmVal) dom_cache_dict.fmVal.textContent = fm_data;
}


/*

CALORIES CHART

*/
let current_week_index = 0; 
let max_weeks = 0; 
let full_cal_labels = [];
let full_cal_data = [];
let full_p_bar_data = [];
let full_f_bar_data = [];
let full_c_bar_data = [];

function calories_chart_config(labels, cal_data, prot, fat, carb) {
    return {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Calories',
                    data: cal_data,
                    backgroundColor: '#33EE96',
                    hoverBackgroundColor: '#33EE96',
                    hoverBorderColor: '#33EE96',
                    borderColor: '#33EE96',
                    borderWidth: 2,
                    hoverOffset: 4,
                    order: 0,
                    stack: 'stack1',
                },
                {
                    label: 'Protein',
                    data: prot,
                    backgroundColor: '#FFC052',
                    borderColor: '#FFC052',
                    hoverBackgroundColor: '#FFC052',
                    hoverBorderColor: '#FFC052',
                    borderWidth: 2,
                    hoverOffset: 4,
                    order: 1,
                    stack: 'macro',
                },
                {
                    label: 'Fat',
                    data: fat,
                    backgroundColor: '#f23e74ff',
                    hoverBackgroundColor: '#f23e74ff',
                    borderColor: '#f23e74ff',
                    hoverBorderColor: '#f23e74ff',
                    borderWidth: 2,
                    hoverOffset: 4,
                    order: 1,
                    stack: 'macro',
                },
                {
                    label: 'Carbs',
                    data: carb,
                    backgroundColor: '#5cb0f9ff',
                    hoverBackgroundColor: '#5cb0f9ff',
                    hoverBorderColor: '#5cb0f9ff',
                    borderColor: '#5cb0f9ff',
                    borderWidth: 2,
                    hoverOffset: 4,
                    order: 1,
                    stack: 'macro',
                },
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    stacked: true,
                    ticks: {
                        callback: function(value, index, ticks) {
                            const label = this.getLabelForValue(value);
                            const date = new Date(label + "T00:00:00");
                            return date.toLocaleDateString('en-US', { 
                                month: 'short',
                                day: 'numeric'
                            });
                        }
                    }
                },
                y: {
                    stacked: true,
                },
            },
            plugins: {
                legend: {
                    display: false,
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#4facfe',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y; 
                            
                            const totalCalories = context.chart.data.datasets
                                .reduce((total, dataset, index) => {
                                    if (index === 0) return total;
                                    const dataValue = dataset.data[context.dataIndex];
                                    return total + (dataValue || 0);
                                }, 0);
                            let grams, percentage;
                            if (label === 'Protein' || label === 'Carbs') {
                                grams = Math.round(value / 4);
                                percentage = totalCalories > 0 ? Math.round((value / totalCalories) * 100) : 0;
                                return `${label}: ${grams}g (${value} Calories, ${percentage}%)`;
                            } else if (label === 'Fat') {
                                grams = Math.round(value / 9);
                                percentage = totalCalories > 0 ? Math.round((value / totalCalories) * 100) : 0;
                                return `${label}: ${grams}g (${value} Calories, ${percentage}%)`;
                            } else {
                                return `${label}: ${value} Calories`;
                            }
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                duration: 1000
            }
        }
    };
}


function get_week_data_non_overlapping(week_index) {
    const total_days = full_cal_labels.length;
    
    if (week_index === 0) {
        const start_index = Math.max(0, total_days - 7);
        return {
            labels: full_cal_labels.slice(start_index, total_days),
            cal_data: full_cal_data.slice(start_index, total_days),
            p_data: full_p_bar_data.slice(start_index, total_days),
            f_data: full_f_bar_data.slice(start_index, total_days),
            c_data: full_c_bar_data.slice(start_index, total_days)
        };
    } 
    else {
        const days_already_shown = Math.min(7, total_days); 
        const additional_days_back = (week_index - 1) * 7;
        const end_index = total_days - days_already_shown - additional_days_back;
        const start_index = Math.max(0, end_index - 7);
        
        return {
            labels: full_cal_labels.slice(start_index, end_index),
            cal_data: full_cal_data.slice(start_index, end_index),
            p_data: full_p_bar_data.slice(start_index, end_index),
            f_data: full_f_bar_data.slice(start_index, end_index),
            c_data: full_c_bar_data.slice(start_index, end_index)
        };
    }
}
function update_calories_chart() {
    if (!chart_instances.cal) return;
    
    const week_data = get_week_data_non_overlapping(current_week_index);
    chart_instances.cal.data.labels = week_data.labels;
    chart_instances.cal.data.datasets[0].data = week_data.cal_data;
    chart_instances.cal.data.datasets[1].data = week_data.p_data.map(p => p * 4); 
    chart_instances.cal.data.datasets[2].data = week_data.f_data.map(f => f * 9);
    chart_instances.cal.data.datasets[3].data = week_data.c_data.map(c => c * 4);
    chart_instances.cal.update('active');
    update_navigation_buttons();
}
function update_navigation_buttons() {
    const back_button = document.getElementById('go_to_last_week');
    const forward_button = document.getElementById('go_to_next_week');
    const weekInfo = document.getElementById('week-info');
    
    if (back_button) back_button.disabled = current_week_index >= max_weeks - 1;
    if (forward_button) forward_button.disabled = current_week_index <= 0;
    
    if (weekInfo) {

        const week_data = get_week_data_non_overlapping(current_week_index);
        if (week_data.labels.length > 0) {
            const start_date = week_data.labels[0];
            const end_date = week_data.labels[week_data.labels.length - 1];
            weekInfo.textContent = `${start_date} - ${end_date}`;
        }
    }
}
function go_to_previous_week() {
    if (current_week_index < max_weeks - 1) {
        current_week_index++;
        update_calories_chart();
    }
}
function go_to_next_week() {
    if (current_week_index > 0) {
        current_week_index--;
        update_calories_chart();
    }
}
function connect_navigation_buttons() {
    const back_button = document.getElementById('go_to_last_week');
    const forward_button = document.getElementById('go_to_next_week');

    if (back_button) {
        back_button.onclick = go_to_previous_week;
    }
    if (forward_button) {
        forward_button.onclick = go_to_next_week;
    }
}
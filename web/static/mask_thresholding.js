function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

function updateThresholdSliderValue(id, value) {
    document.getElementById(id).textContent = value;
    sendThresholdSliderValues();
}

function updateColorSliderValue(id, value) {
    document.getElementById(id).textContent = value;
    sendColorSliderValues();
}

function sendThresholdSliderValues() {
    const thMinValue = document.getElementById('th_min_slider').value;
    const thMaxValue = document.getElementById('th_max_slider').value;

    fetch('/update_thresholds', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            th_min: thMinValue,
            th_max: thMaxValue
        })
    })
    .then(response => response.blob())
    .then(blob => {
        const img = document.getElementById('mask');
        img.src = URL.createObjectURL(blob);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}


function sendColorSliderValues() {
    const rMinValue = document.getElementById('r_min_slider').value;
    const rMaxValue = document.getElementById('r_max_slider').value;
    const gMinValue = document.getElementById('g_min_slider').value;
    const gMaxValue = document.getElementById('g_max_slider').value;
    const bMinValue = document.getElementById('b_min_slider').value;
    const bMaxValue = document.getElementById('b_max_slider').value;
    const sharpenValue = document.getElementById('sharpen_slider').value;
    const modeValue = document.getElementById('mode_select').value;

    fetch('/update_color_filters', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            r_min: rMinValue,
            r_max: rMaxValue,
            g_min: gMinValue,
            g_max: gMaxValue,
            b_min: bMinValue,
            b_max: bMaxValue,
            sharpen: sharpenValue,
            mode: modeValue
        })
    })
    .then(response => response.blob())
    .then(blob => {
        const img = document.getElementById('mask');
        img.src = URL.createObjectURL(blob);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

const debouncedSendThresholdSliderValues = debounce(updateThresholdSliderValue, 10);
const debouncedSendColorSliderValues = debounce(updateColorSliderValue, 75);

function color_filtering_done() {
    console.log('color_filtering_done');
    document.getElementById('color-filtering-sliders-div').style.display = 'none';
    document.getElementById('progress-bar').style.display = 'flex';
    document.getElementById('start_button').style.display = 'flex';
}

function erode_dilate_done() {
    console.log('erode_dilate_done');
    document.querySelector('h1').innerHTML = 'Color filtering';
    document.getElementById('color-filtering-sliders-div').style.display = 'flex';
    document.getElementById('color-filtering-sliders-div').style.flexDirection = 'column';
    const elements = document.querySelectorAll('.new-buttons');
    elements.forEach(element => {
        element.style.display = 'None';
    });
    document.getElementById('done_button').addEventListener('click', color_filtering_done);
    sendColorSliderValues();
}

function mask_selection_done() {
    document.querySelector('h1').innerHTML = 'Erode/Dilate mask';
    console.log('mask_selection_done');
    document.getElementById('threshold-sliders-div').style.display = 'None';
    const elements = document.querySelectorAll('.new-buttons');
    elements.forEach(element => {
        element.style.display = 'flex';
    });
    document.getElementById('done_button').addEventListener('click', erode_dilate_done);
}

function processMask(url) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        updateImageDilateErode();
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function erode_mask() {
    processMask('/erode_mask');
}

function dilate_mask() {
    processMask('/dilate_mask');
}

function reset_mask() {
    processMask('/reset_dilate_erode_mask');
}

function updateImage() {
    const img = document.getElementById('mask');
    img.src = '/get_threshold_mask/';
}

function updateImageDilateErode() {
    console.log('updateImageDilateErode');
    const img = document.getElementById('mask');
    img.src = '/get_dilate_erode_mask/';
}



window.onload = function() {
    const socket = io();
    socket.on('progress_update', function(data) {
        const progressBar = document.getElementById('progress-bar');
        progressBar.value = data.progress;
    });

    document.getElementById('start_button').addEventListener('click', function() {
        fetch('/start_long_task', { method: 'POST' });
    });
    updateThresholdSliderValue('th_min_value', document.getElementById('th_min_slider').value);
    updateThresholdSliderValue('th_max_value', document.getElementById('th_max_slider').value);

    document.getElementById('done_button').addEventListener('click', mask_selection_done);
    document.getElementById('erode_button').addEventListener('click', erode_mask);
    document.getElementById('dilate_button').addEventListener('click', dilate_mask);
    document.getElementById('reset_button').addEventListener('click', reset_mask);
    document.getElementById('mode_select').addEventListener('change', sendColorSliderValues);
};
// Configuration
const NUM_SEQUENCES = 10;
const NUM_FEATURES = 57;
const KNOWN_FEATURES = ['age', 'bp', 'sc', 'htn', 'dm', 'cad', 'hemo', 'al', 'sg'];
const RANGES = {
    age: { min: 18, max: 100, step: 1 },
    bp: { min: 50, max: 180, step: 1 },
    sc: { min: 0.5, max: 24.0, step: 0.1 },
    htn: { min: 0, max: 1, step: 1 },
    dm: { min: 0, max: 1, step: 1 },
    cad: { min: 0, max: 1, step: 1 },
    hemo: { min: 9.0, max: 17.0, step: 0.1 },
    al: { min: 0, max: 5, step: 1 },
    sg: { min: 0, max: 4, step: 1 }
};
const STATS = {
    age: { mean: 51.5, std: 15.0 },
    bp: { mean: 76.0, std: 13.0 },
    sc: { mean: 3.0, std: 2.5 },
    hemo: { mean: 11.0, std: 2.0 }
};
const DEFAULT_VALUES = {
    age: 60,
    bp: 80,
    sc: 1.2,
    htn: 1,
    dm: 1,
    cad: 0,
    hemo: 12.0,
    al: 2,
    sg: 3
};
const ALL_FEATURES = [
    'id', 'age', 'bp', 'bgr', 'bu', 'sc', 'sod', 'pot', 'hemo', 'pcv', 'wc', 'rc',
    'sg_1.005', 'sg_1.01', 'sg_1.015', 'sg_1.02', 'sg_1.025',
    'al_0', 'al_1', 'al_2', 'al_3', 'al_4', 'al_5',
    'su_0', 'su_1', 'su_2', 'su_3', 'su_4', 'su_5',
    'rbc_normal', 'rbc_abnormal',
    'pc_normal', 'pc_abnormal',
    'pcc_present', 'pcc_notpresent',
    'ba_present', 'ba_notpresent',
    'htn_yes', 'htn_no',
    'dm_yes', 'dm_no',
    'cad_yes', 'cad_no',
    'appet_good', 'appet_poor',
    'pe_yes', 'pe_no',
    'ane_yes', 'ane_no',
    // Adding missing features to reach 57 total features
    'class_ckd', 'class_notckd',
    'pcv_high', 'pcv_normal', 'pcv_low',
    'wc_high', 'wc_normal', 'wc_low'
];
const SG_MAPPING = { 0: '1.005', 1: '1.01', 2: '1.015', 3: '1.02', 4: '1.025' };
const FEATURE_MAPPING = {
    'age': 'age',
    'bp': 'bp',
    'sc': 'sc',
    'htn': 'htn_yes',
    'dm': 'dm_yes',
    'cad': 'cad_yes',
    'hemo': 'hemo',
    'al': 'al_{}',
    'sg': 'sg_{}'
};

// Generate input fields
const inputFields = document.getElementById('input-fields');
const sequenceDiv = document.createElement('div');
sequenceDiv.innerHTML = `<h3 class="text-lg font-semibold mb-2">Patient Health Snapshot</h3>`;
const grid = document.createElement('div');
grid.className = 'grid grid-cols-2 gap-2';
KNOWN_FEATURES.forEach((key) => {
    const label = key.toUpperCase() === 'BP' ? 'Blood Pressure' :
                  key.toUpperCase() === 'SC' ? 'Serum Creatinine' :
                  key.toUpperCase() === 'HTN' ? 'Hypertension' :
                  key.toUpperCase() === 'DM' ? 'Diabetes' :
                  key.toUpperCase() === 'CAD' ? 'Coronary Artery Disease' :
                  key.toUpperCase() === 'HEMO' ? 'Hemoglobin' :
                  key.toUpperCase() === 'AL' ? 'Albumin' :
                  key.toUpperCase() === 'SG' ? 'Specific Gravity' :
                  key.charAt(0).toUpperCase() + key.slice(1);
    if (key === 'htn' || key === 'dm' || key === 'cad') {
        grid.innerHTML += `
            <div>
                <label class="block text-sm font-medium text-gray-700">${label} (1=Yes, 0=No)</label>
                <select name="${key}" class="border p-2 rounded w-full" required>
                    <option value="1" ${DEFAULT_VALUES[key] === 1 ? 'selected' : ''}>1</option>
                    <option value="0" ${DEFAULT_VALUES[key] === 0 ? 'selected' : ''}>0</option>
                </select>
            </div>
        `;
    } else if (key === 'sg') {
        grid.innerHTML += `
            <div>
                <label class="block text-sm font-medium text-gray-700">${label} (0=1.005, 1=1.01, 2=1.015, 3=1.02, 4=1.025)</label>
                <select name="${key}" class="border p-2 rounded w-full" required>
                    <option value="0" ${DEFAULT_VALUES[key] === 0 ? 'selected' : ''}>0</option>
                    <option value="1" ${DEFAULT_VALUES[key] === 1 ? 'selected' : ''}>1</option>
                    <option value="2" ${DEFAULT_VALUES[key] === 2 ? 'selected' : ''}>2</option>
                    <option value="3" ${DEFAULT_VALUES[key] === 3 ? 'selected' : ''}>3</option>
                    <option value="4" ${DEFAULT_VALUES[key] === 4 ? 'selected' : ''}>4</option>
                </select>
            </div>
        `;
    } else {
        grid.innerHTML += `
            <div>
                <label class="block text-sm font-medium text-gray-700">${label}</label>
                <input
                    type="number"
                    step="${RANGES[key].step}"
                    min="${RANGES[key].min}"
                    max="${RANGES[key].max}"
                    class="border p-2 rounded w-full"
                    name="${key}"
                    value="${DEFAULT_VALUES[key]}"
                    required
                >
            </div>
        `;
    }
});
sequenceDiv.appendChild(grid);
inputFields.appendChild(sequenceDiv);

// Generate random inputs
document.getElementById('generate-random').addEventListener('click', () => {
    KNOWN_FEATURES.forEach(key => {
        const inputField = document.querySelector(`[name="${key}"]`);
        if (key === 'htn' || key === 'dm' || key === 'cad') {
            inputField.value = Math.random() > 0.5 ? "1" : "0";
        } else if (key === 'sg') {
            inputField.value = Math.floor(Math.random() * 5);
        } else {
            const { min, max, step } = RANGES[key];
            const value = min + Math.random() * (max - min);
            inputField.value = step >= 1 ? Math.round(value) : value.toFixed(1);
        }
    });
});

// Handle form submission
document.getElementById('predict-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const resultDiv = document.getElementById('result');
    const progress = document.getElementById('progress');
    const progressBar = document.getElementById('progress-bar');
    const downloadBtn = document.getElementById('download-result');
    resultDiv.className = 'mt-6 p-4 rounded-lg hidden';
    resultDiv.innerHTML = '';
    downloadBtn.classList.add('hidden');

    // Show progress bar
    progress.classList.remove('hidden');
    progressBar.style.width = '30%';

    // Collect raw form data
    const rawFormData = {};
    KNOWN_FEATURES.forEach(key => {
        const inputField = document.querySelector(`[name="${key}"]`);
        rawFormData[key] = inputField.value;
    });
    console.log("Raw form data:", rawFormData);

    // Validate inputs
    const values = {};
    let isValid = true;
    KNOWN_FEATURES.forEach(key => {
        const inputField = document.querySelector(`[name="${key}"]`);
        let value = inputField.value;

        if (key === 'htn' || key === 'dm' || key === 'cad') {
            if (value !== "0" && value !== "1") {
                console.warn(`Invalid ${key} value: ${value}, defaulting to ${DEFAULT_VALUES[key]}`);
                value = DEFAULT_VALUES[key].toString();
                inputField.value = value;
                inputField.selectedIndex = value === "1" ? 0 : 1;
            }
        } else if (key === 'sg') {
            if (!['0', '1', '2', '3', '4'].includes(value)) {
                console.warn(`Invalid sg value: ${value}, defaulting to 3`);
                value = "3";
                inputField.value = value;
                inputField.selectedIndex = 3;
            }
        }

        if (value === "" || value == null) {
            isValid = false;
            inputField.classList.add('error-border');
            console.error(`Validation failed for ${key}: value is empty or null`);
        } else {
            const parsedValue = parseFloat(value);
            if (isNaN(parsedValue)) {
                isValid = false;
                inputField.classList.add('error-border');
                console.error(`Validation failed for ${key}: value '${value}' is not a number`);
            } else {
                values[key] = parsedValue;
                inputField.classList.remove('error-border');
            }
        }
    });

    if (!isValid) {
        progress.classList.add('hidden');
        resultDiv.className = 'mt-6 p-4 rounded-lg bg-red-100 text-red-800';
        resultDiv.innerHTML = `<h3>Error</h3><p>Please fill all fields with valid numbers.</p>`;
        resultDiv.classList.remove('hidden');
        return;
    }

    // Log validated values
    console.log("Validated form values:", values);

    // Standardize values
    const standardizedValues = {};
    KNOWN_FEATURES.forEach(key => {
        const value = values[key];
        if (key in STATS) {
            standardizedValues[key] = (value - STATS[key].mean) / STATS[key].std;
        } else {
            standardizedValues[key] = value;
        }
    });

    // Generate 10 sequences with 57 features
    const sequences = Array(NUM_SEQUENCES).fill().map(() => {
        const sequence = Array(NUM_FEATURES).fill(0);
        KNOWN_FEATURES.forEach(key => {
            const value = standardizedValues[key];
            const variation = (Math.random() * 0.2 - 0.1);
            const variedValue = value + variation;
            
            if (['age', 'bp', 'sc', 'hemo'].includes(key)) {
                const idx = ALL_FEATURES.indexOf(FEATURE_MAPPING[key]);
                if (idx !== -1) {
                    sequence[idx] = variedValue;
                }
            } else if (['htn', 'dm', 'cad'].includes(key)) {
                const idxYes = ALL_FEATURES.indexOf(FEATURE_MAPPING[key]);
                const idxNo = ALL_FEATURES.indexOf(FEATURE_MAPPING[key].replace('_yes', '_no'));
                if (idxYes !== -1 && idxNo !== -1) {
                    sequence[idxYes] = variedValue > 0.5 ? 1.0 : 0.0;
                    sequence[idxNo] = 1.0 - sequence[idxYes];
                }
            } else if (key === 'al') {
                const alValue = Math.round(values['al']);
                const idx = ALL_FEATURES.indexOf(FEATURE_MAPPING[key].replace('{}', alValue));
                if (idx !== -1) {
                    sequence[idx] = 1.0;
                }
            } else if (key === 'sg') {
                const sgIdx = Math.round(values['sg']);
                const sgValue = SG_MAPPING[sgIdx];
                const idx = ALL_FEATURES.indexOf(FEATURE_MAPPING[key].replace('{}', sgValue));
                if (idx !== -1) {
                    sequence[idx] = 1.0;
                }
            }
        });
        return sequence;
    });

    // Log input
    console.log("Input sent to API (first sequence shown):", JSON.stringify(sequences[0], null, 2));
    console.log(`Input shape: (${sequences.length}, ${sequences[0].length})`);

    try {
        progressBar.style.width = '60%';
        const response = await fetch('http://127.0.0.1:5000/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input: sequences })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `Server error: ${response.status}`);
        }
        
        const data = await response.json();
        progressBar.style.width = '100%';
        setTimeout(() => progress.classList.add('hidden'), 500);

        resultDiv.className = 'mt-6 p-4 rounded-lg bg-green-100 text-green-800';
        resultDiv.innerHTML = `
            <h3 class="text-lg font-semibold">Prediction Result</h3>
            <p><strong>Risk Level:</strong> ${data.prediction}</p>
            <p><strong>Probability:</strong> ${(data.probability * 100).toFixed(2)}%</p>
        `;
        downloadBtn.classList.remove('hidden');
        downloadBtn.onclick = () => {
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'prediction_result.pdf';
            a.click();
            URL.revokeObjectURL(url);
        };
    } catch (error) {
        console.error("Prediction error:", error);
        progressBar.style.width = '100%';
        setTimeout(() => progress.classList.add('hidden'), 500);
        resultDiv.className = 'mt-6 p-4 rounded-lg bg-red-100 text-red-800';
        resultDiv.innerHTML = `<h3>Error</h3><p>${error.message}</p>`;
    }
    resultDiv.classList.remove('hidden');
});

// Reset form
document.getElementById('reset-form').addEventListener('click', () => {
    document.getElementById('predict-form').reset();
    const resultDiv = document.getElementById('result');
    const progress = document.getElementById('progress');
    const downloadBtn = document.getElementById('download-result');
    resultDiv.className = 'mt-6 p-4 rounded-lg hidden';
    resultDiv.innerHTML = '';
    progress.classList.add('hidden');
    downloadBtn.classList.add('hidden');
    KNOWN_FEATURES.forEach(key => {
        const inputField = document.querySelector(`[name="${key}"]`);
        inputField.value = DEFAULT_VALUES[key];
        inputField.classList.remove('error-border');
        if (key === 'htn' || key === 'dm' || key === 'cad') {
            inputField.selectedIndex = DEFAULT_VALUES[key] === 1 ? 0 : 1;
        } else if (key === 'sg') {
            inputField.selectedIndex = DEFAULT_VALUES[key];
        }
    });
});
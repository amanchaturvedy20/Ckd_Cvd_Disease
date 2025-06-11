import requests
import json
import random
import numpy as np

def generate_input():
    """Generate input for 10 sequences with 57 features based on kidney_disease.csv."""
    # Define known feature keys and practical ranges from CSV
    feature_keys = ['age', 'bp', 'sc', 'htn', 'dm', 'cad', 'hemo', 'al', 'sg']
    ranges = {
        'age': (18, 100),  # years, integer
        'bp': (50, 180),  # mmHg, integer
        'sc': (0.5, 24.0),  # mg/dL, one decimal
        'htn': (0, 1),  # yes=1, no=0
        'dm': (0, 1),  # yes=1, no=0
        'cad': (0, 1),  # yes=1, no=0
        'hemo': (9.0, 17.0),  # g/dL, one decimal
        'al': (0, 5),  # integer
        'sg': (0, 4)  # mapped: 1.005=0, 1.01=1, 1.015=2, 1.02=3, 1.025=4
    }
    # Mean and std from dataset (approximated from CSV sample)
    stats = {
        'age': {'mean': 51.5, 'std': 15.0},
        'bp': {'mean': 76.0, 'std': 13.0},
        'sc': {'mean': 3.0, 'std': 2.5},
        'hemo': {'mean': 11.0, 'std': 2.0}
    }
    base_values = {
        'age': 60,
        'bp': 80,
        'sc': 1.2,
        'htn': 1,
        'dm': 1,
        'cad': 0,
        'hemo': 12.0,
        'al': 2,
        'sg': 3
    }

    # Standardize known values
    standardized_values = {}
    for key in feature_keys:
        value = base_values[key]
        if key in stats:
            standardized_values[key] = (value - stats[key]['mean']) / stats[key]['std']
        else:
            standardized_values[key] = value  # Binary or categorical

    # Full feature list (57 features) - FIXED to match the expected 57 features
    all_features = [
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
        # Adding missing features to reach 57 total features
        'class_ckd', 'class_notckd',
        'pcv_high', 'pcv_normal', 'pcv_low',
        'wc_high', 'wc_normal', 'wc_low'
    ]
    print(f"Number of features: {len(all_features)}")
    print("Features:", all_features)  # Debug: list all features
    assert len(all_features) == 57, f"Expected 57 features, got {len(all_features)}"

    # Map input features
    feature_mapping = {
        'age': 'age',
        'bp': 'bp',
        'sc': 'sc',
        'htn': 'htn_yes',
        'dm': 'dm_yes',
        'cad': 'cad_yes',
        'hemo': 'hemo',
        'al': 'al_{}',
        'sg': 'sg_{}'
    }
    sg_mapping = {0: '1.005', 1: '1.01', 2: '1.015', 3: '1.02', 4: '1.025'}

    # Create 10 sequences
    input_data = []
    for i in range(10):
        sequence = [0.0] * 57
        for key in feature_keys:
            value = standardized_values[key]
            variation = random.uniform(-0.1, 0.1)
            varied_value = value + variation
            if key in ['age', 'bp', 'sc', 'hemo']:
                idx = all_features.index(feature_mapping[key])
                sequence[idx] = varied_value
            elif key in ['htn', 'dm', 'cad']:
                idx_yes = all_features.index(feature_mapping[key])
                idx_no = all_features.index(feature_mapping[key].replace('_yes', '_no'))
                sequence[idx_yes] = 1 if varied_value > 0.5 else 0
                sequence[idx_no] = 1 - sequence[idx_yes]
            elif key == 'al':
                al_value = round(base_values['al'] + variation * 5)
                al_value = max(0, min(5, al_value))
                idx = all_features.index(feature_mapping[key].format(al_value))
                sequence[idx] = 1.0
            elif key == 'sg':
                sg_idx = round(base_values['sg'] + variation * 4)
                sg_idx = max(0, min(4, sg_idx))
                idx = all_features.index(feature_mapping[key].format(sg_mapping[sg_idx]))
                sequence[idx] = 1.0
        input_data.append(sequence)

    # Display input (denormalized)
    print("\nInput Data for Prediction (Sequence 1 shown, others similar):")
    for key in feature_keys:
        idx = all_features.index(feature_mapping[key]) if key in ['age', 'bp', 'sc', 'hemo'] else None
        if idx is not None:
            value = input_data[0][idx]
            if key in stats:
                denormalized_value = value * stats[key]['std'] + stats[key]['mean']
                denormalized_value = round(denormalized_value) if key in ['age', 'bp'] else round(denormalized_value, 1)
            else:
                denormalized_value = value
            print(f"{key}: {denormalized_value}")
        else:
            # For categorical variables, find the corresponding one-hot encoded column
            if key in ['htn', 'dm', 'cad']:
                idx = all_features.index(feature_mapping[key])
                value = input_data[0][idx]
                print(f"{key}: {int(value)}")
            elif key == 'al':
                for i in range(6):
                    idx = all_features.index(f'al_{i}')
                    if input_data[0][idx] == 1.0:
                        print(f"{key}: {i}")
                        break
            elif key == 'sg':
                for i, sg_val in sg_mapping.items():
                    idx = all_features.index(f'sg_{sg_val}')
                    if input_data[0][idx] == 1.0:
                        print(f"{key}: {i}")
                        break
    print(f"... plus {57 - len(feature_keys)} other features")
    print(f"Generated input shape: ({len(input_data)}, {len(input_data[0])})")

    return {"input": input_data}

def make_prediction(test_input):
    """Send prediction request to the API."""
    try:
        response = requests.post("http://127.0.0.1:5000/predict", json=test_input, timeout=10)
        print("\nResponse from API:")
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to API: {e}")

def main():
    try:
        test_input = generate_input()
        make_prediction(test_input)
    except Exception as e:
        print(f"Script failed: {e}")

if __name__ == "__main__":
    main()
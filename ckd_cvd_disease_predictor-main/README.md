Running the Application

    Start the Flask Server:
    bash

    python3 app.py

        The server runs on http://127.0.0.1:5000.

        Ensure gru_model.h5 is in the root directory, or the server will fail to start.

    Access the Application:

        Open a browser and navigate to http://127.0.0.1:5000.

        The web interface loads with a form for patient data.

    Test the API (Optional):

        Run the provided test_api.py to verify the /predict endpoint:
        bash

        python3 test_api.py

        Expected output: JSON response like {"prediction": "Low Risk", "probability": 0.3958}.

Usage

    Enter Patient Data:

        Fill the form with values for:

            Age (18–100)

            Blood Pressure (50–180)

            Serum Creatinine (0.5–24.0)

            Hypertension (1=Yes, 0=No)

            Diabetes (1=Yes, 0=No)

            Coronary Artery Disease (1=Yes, 0=No)

            Hemoglobin (9.0–17.0)

            Albumin (0–5)

            Specific Gravity (0=1.005, 1=1.01, 2=1.015, 3=1.02, 4=1.025)

        Example:

            Age: 25

            Blood Pressure: 54

            Serum Creatinine: 4.1

            Hypertension: 1

            Diabetes: 0

            Coronary Artery Disease: 0

            Hemoglobin: 16.8

            Albumin: 1

            Specific Gravity: 4

    Generate Random Inputs:

        Click "Generate Random Inputs" to auto-fill the form with valid random values.

    Predict:

        Click "Predict" to submit the form.

        A progress bar animates during processing.

        The result appears in a div:

            Red background for "High Risk".

            Green background for "Low Risk".

            Example: "Risk Level: Low Risk, Probability: 39.58%"

    Download Result:

        Click "Download Result" to save a PDF (prediction_result.pdf).

        The PDF includes:

            Patient Health Snapshot (e.g., Age: 25, Blood Pressure: 54).

            Prediction Result (e.g., Risk Level: Low Risk, Probability: 39.58%).

    Reset:

        Click "Reset" to clear the form and restore default values.

Working Mechanism
Frontend (index.html)

    Technologies:

        HTML5, Tailwind CSS (via CDN), JavaScript, jsPDF (via CDN).

    Components:

        Form: Collects 9 patient features (age, bp, sc, htn, dm, cad, hemo, al, sg).

        Animations: Slide-in for inputs, fade-in for results, scale-up for button clicks.

        Validation: Ensures all inputs are valid numbers within specified ranges.

        Data Processing:

            Standardizes numerical inputs (age, bp, sc, hemo) using mean/std.

            Generates 10 sequences of 57 features, padding with zeros and adding ±0.1 variation.

        API Call: Sends POST request to /predict with input sequences.

        Result Display: Shows prediction with red/green background based on risk level.

        PDF Generation: Uses jsPDF to create a PDF with patient data and prediction.

    Flow:

        User fills form or generates random inputs.

        Validates inputs; shows error if invalid.

        Standardizes data and generates sequences.

        Sends API request and animates progress bar.

        Displays result with animations.

        Generates PDF on download request.

Backend (app.py)

    Technologies:

        Flask, TensorFlow, NumPy.

    Components:

        Flask Server: Hosts the app at http://127.0.0.1:5000.

        Model Loading: Loads gru_model.h5 (GRU model) at startup.

        Prediction Endpoint: /predict (POST) accepts 10x57 input sequences.

        Prediction Logic:

            Validates input shape (10, 57).

            Runs GRU model to predict probability.

            Returns High Risk (probability > 0.5) or Low Risk with probability.

    Flow:

        Starts Flask server and loads model.

        Serves index.html at root (/).

        Processes /predict requests, validates input, and returns JSON response.

Data Flow

    Input: 9 user-provided features (e.g., age: 25, htn: 1).

    Processing:

        Standardized: Numerical features normalized (e.g., (age - 51.5) / 15).

        Sequenced: 10 sequences generated, each with 57 features (9 user inputs mapped, 48 padded).

        Example: htn: 1 maps to htn_yes: 1, htn_no: 0.

    Prediction: GRU model processes sequences, outputs probability.

    Output: JSON with prediction (High/Low Risk) and probability.

    PDF: Combines user inputs and prediction in a formatted document.
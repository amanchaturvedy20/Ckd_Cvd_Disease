from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.layers import GRU, Dense, Masking
from sklearn.utils import class_weight
from sklearn.model_selection import train_test_split
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import numpy as np
import os

app = Flask(__name__, template_folder='templates')
app.secret_key = 'supersecretkey'
CORS(app)

# ---------- MongoDB Connection ----------
password = "252607"
uri = f"mongodb+srv://pragatipandey325:{password}@pragati.vkjinph.mongodb.net/?retryWrites=true&w=majority&appName=pragati"

try:
    client = MongoClient(uri, server_api=ServerApi('1'))
    client.admin.command('ping')
    print("Pinged your deployment. Successfully connected to MongoDB!")
except Exception as e:
    print("MongoDB Connection Error:", e)
    exit(1)

mongo_db = client['majorproject']
mongo_users = mongo_db['users']

# ---------- Load or Train GRU Model ----------
os.environ["CUDA_VISIBLE_DEVICES"] = ""
model_path = "gru_model.h5"

if not os.path.exists(model_path):
    try:
        print("Training new GRU model...")
        X = np.load("X_data.npy")  # shape (num_samples, 10, 57)
        y = np.load("y_labels.npy")  # shape (num_samples,)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y)
        class_weights = class_weight.compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
        class_weights = dict(enumerate(class_weights))

        model = Sequential([
            Masking(mask_value=0.0, input_shape=(10, 57)),
            GRU(64, return_sequences=False),
            Dense(1, activation='sigmoid')
        ])

        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        model.fit(X_train, y_train, epochs=20, batch_size=32, validation_split=0.1, class_weight=class_weights)
        model.save(model_path)
        print("Model trained and saved.")
    except Exception as e:
        print(f"Error training model: {e}")
        exit(1)
else:
    try:
        model = load_model(model_path, compile=False)
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        exit(1)

# ---------- Routes ----------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        gender = request.form['gender']

        if mongo_users.find_one({"$or": [{"email": email}, {"username": username}]}):
            return render_template('register.html', error='Email or Username already exists.')

        mongo_users.insert_one({
            "name": name,
            "username": username,
            "email": email,
            "password": password,
            "gender": gender
        })
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        password = request.form.get('password')
        if not identifier or not password:
            return render_template('login.html', error='Please fill out all fields.')

        user = mongo_users.find_one({"$or": [{"username": identifier}, {"email": identifier}]})
        if user and check_password_hash(user['password'], password):
            session['user'] = user['username']
            return redirect(url_for('index'))

        return render_template('login.html', error='Invalid credentials.')

    return render_template('login.html')

@app.route('/index')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')

# ---------- Prediction ----------
@app.route('/predict', methods=['POST'])
def predict():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()
        input_seq = data['input']

        FEATURE_RANGES = {i: (0, 1) for i in range(57)}
        FEATURE_RANGES.update({
            0: (18, 100),     # age
            1: (50, 180),     # bp
            2: (0.4, 15),     # sc
            3: (0, 1),        # htn
            4: (0, 1),        # dm
            5: (0, 1),        # cad
            6: (3.1, 18),     # hemo
            7: (0, 5),        # al
            8: (1.005, 1.025) # sg
        })

        def normalize(seq):
            normalized = []
            for i, val in enumerate(seq):
                min_val, max_val = FEATURE_RANGES.get(i, (0, 1))
                try:
                    val = float(val)
                except:
                    val = 0.0
                norm_val = (val - min_val) / (max_val - min_val) if max_val != min_val else 0
                norm_val = min(max(norm_val, 0.0), 1.0)
                normalized.append(norm_val)
            return normalized

        converted_seq = [normalize(seq) for seq in input_seq]
        input_seq = np.array(converted_seq, dtype=np.float32)

        if input_seq.shape != (10, 57):
            return jsonify({"error": f"Invalid shape {input_seq.shape}, expected (10, 57)"}), 400

        input_seq = np.expand_dims(input_seq, axis=0)
        prediction = model.predict(input_seq)[0][0]
        result = "High Risk" if prediction > 0.5 else "Low Risk"

        return jsonify({"prediction": result, "probability": float(prediction)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- Contact ----------
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        username = request.form['username']
        topic = request.form['topic']
        query = request.form['query']

        with open('queries.txt', 'a') as f:
            f.write(f"Username: {username}\nTopic: {topic}\nQuery: {query}\n---\n")

        return render_template('contact.html', message="Your query has been submitted!")

    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)

# train_model.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, GRU, Dense, Dropout, BatchNormalization
from sklearn.metrics import accuracy_score, roc_auc_score
from tensorflow.keras.models import save_model
#from google.colab import files  # Remove this line if not using Google Colab

# Load Dataset
df = pd.read_csv("kidney_disease.csv")

# Preprocessing
numerical_cols = df.select_dtypes(include=np.number).columns
categorical_cols = df.select_dtypes(exclude=np.number).columns

num_imputer = SimpleImputer(strategy='mean')
df[numerical_cols] = num_imputer.fit_transform(df[numerical_cols])

cat_imputer = SimpleImputer(strategy='most_frequent')
df[categorical_cols] = cat_imputer.fit_transform(df[categorical_cols])

scaler = StandardScaler()
df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
categorical_features = encoder.fit_transform(df[['sg', 'al', 'su', 'rbc', 'pc', 'pcc', 'ba', 'htn', 'dm', 'cad', 'appet', 'pe', 'ane']])
encoded_feature_names = encoder.get_feature_names_out(['sg', 'al', 'su', 'rbc', 'pc', 'pcc', 'ba', 'htn', 'dm', 'cad', 'appet', 'pe', 'ane'])
encoded_features_df = pd.DataFrame(categorical_features, columns=encoded_feature_names, index=df.index)

df = df.drop(columns=['sg', 'al', 'su', 'rbc', 'pc', 'pcc', 'ba', 'htn', 'dm', 'cad', 'appet', 'pe', 'ane'])
df = pd.concat([df, encoded_features_df], axis=1)

# Ensure all numeric
df = df.apply(pd.to_numeric, errors='coerce')
df = df.fillna(0)
df = df.values

# Create sequences
sequence_length = 10
def create_sequences(data, seq_length):
    return np.array([data[i:i+seq_length] for i in range(len(data) - seq_length)])

data_sequences = create_sequences(df, sequence_length)
labels = df[sequence_length:, -1]

X_train, X_test, y_train, y_test = train_test_split(data_sequences, labels, test_size=0.2, random_state=42)

# Build Models
def build_lstm(input_shape):
    model = Sequential([
        LSTM(128, return_sequences=True, input_shape=input_shape),
        BatchNormalization(),
        LSTM(64, return_sequences=True),
        Dropout(0.3),
        LSTM(32, return_sequences=False),
        Dropout(0.3),
        Dense(16, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def build_gru(input_shape):
    model = Sequential([
        GRU(128, return_sequences=True, input_shape=input_shape),
        BatchNormalization(),
        GRU(64, return_sequences=True),
        Dropout(0.3),
        GRU(32, return_sequences=False),
        Dropout(0.3),
        Dense(16, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

lstm_model = build_lstm((sequence_length, X_train.shape[2]))
gru_model = build_gru((sequence_length, X_train.shape[2]))
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)

# Train Models
lstm_model.fit(X_train, y_train, epochs=5, batch_size=32, validation_data=(X_test, y_test))
gru_model.fit(X_train, y_train, epochs=5, batch_size=32, validation_data=(X_test, y_test))
rf_model.fit(X_train[:, -1, :], y_train)

# Evaluate Models
def evaluate(model, X, y, type_):
    if type_ == 'rf':
        y_pred = model.predict(X[:, -1, :])
    else:
        y_pred = (model.predict(X) > 0.5).astype(int)
    acc = accuracy_score(y, y_pred)
    auc = roc_auc_score(y, y_pred)
    print(f"{type_.upper()} Model - Accuracy: {acc:.2f}, AUC-ROC: {auc:.2f}")
    return auc

auc_lstm = evaluate(lstm_model, X_test, y_test, 'lstm')
auc_gru = evaluate(gru_model, X_test, y_test, 'gru')
evaluate(rf_model, X_test, y_test, 'rf')

# Save best model
best_model = gru_model if auc_gru >= auc_lstm else lstm_model
filename = "gru_model.h5" if auc_gru >= auc_lstm else "lstm_model.h5"
best_model.save(filename)
print(f"✅ Best model saved as {filename}")

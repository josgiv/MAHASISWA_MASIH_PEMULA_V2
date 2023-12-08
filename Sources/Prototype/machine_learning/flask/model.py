# model.py

import pandas as pd
import joblib
from flask import Flask, request, jsonify

app = Flask(__name__)   

class TrafficClassifier:
    def __init__(self, model_path='../model/test2.pkl'):
        self.model = joblib.load(model_path)

    def preprocess(self, df):
        categorical_cols = ['switch', 'src', 'dst', 'pairflow', 'protocol']
        df_processed = pd.get_dummies(df, columns=categorical_cols)
        df_processed = df_processed.where(pd.notna(df_processed), None)

        return df_processed

    def classify(self, df):
        df_processed = self.preprocess(df)
        try:
            df_processed = df_processed.astype(float)
            predictions = self.model.predict(df_processed)
            df['classification'] = predictions
            df['classification'] = df['classification'].map({0: 'Normal', 1: 'Malicious'})
        except Exception as e:
            df['classification'] = 'Error: ' + str(e)
        return df

def predict_traffic(data):
    classifier = TrafficClassifier()
    try:
        # Ensure the input data is a DataFrame
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)
        classified_data = classifier.classify(data)

        classified_data['classification'] = classified_data['classification'].str[:255]

        classified_data['classification'] = classified_data['classification'].astype(str)

        data['classification'] = classified_data['classification']
    except Exception as e:
        data['classification'] = 'Error: ' + str(e)

    if 'classification' in data.columns:
        important_features = [
            'src', 'pktcount', 'dst', 'byteperflow', 'pktperflow', 'pktrate',
            'tot_kbps', 'rx_kbps', 'flows', 'bytecount', 'dt', 'protocol',
            'dur', 'tot_dur', 'classification',
        ]
        return data[important_features]
    else:
        return data

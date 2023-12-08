# app.py

from flask import Flask, jsonify, request
from supabase import create_client
import pandas as pd
import os
from model import predict_traffic
from dotenv import load_dotenv
from model import TrafficClassifier
import argparse

load_dotenv()

app = Flask(__name__)

parser = argparse.ArgumentParser(description="Run the Flask app with customizable port.")
parser.add_argument("-p", "--port", type=int, default=8080, help="Specify the port for Flask app.")
args = parser.parse_args()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

def fetch_data():
    data = supabase.table('log_traffic').select('*').execute()
    df = pd.DataFrame(data.data)

    # Convert data types
    df = df.astype({
        'dt': 'str',
        'switch': 'str',
        'src': 'str',
        'dst': 'str',
        'pktcount': 'int',
        'bytecount': 'int',
        'dur': 'int',
        'dur_nsec': 'int',
        'tot_dur': 'float',
        'flows': 'int',
        'packetins': 'int',
        'pktperflow': 'float',
        'byteperflow': 'float',
        'pktrate': 'float',
        'pairflow': 'str',
        'protocol': 'str',
        'tx_bytes': 'int',
        'rx_bytes': 'int',
        'tx_kbps': 'float',
        'rx_kbps': 'float',
        'tot_kbps': 'float',
        'label': 'str'
    })
    return df

def save_classification(results):
    supabase.table('hasil_klasifikasi_1').insert(results).execute()

@app.route('/predict', methods=['POST'])
def predict():
    json_input = request.get_json()
    required_fields = ['dt', 'switch', 'src', 'dst', 'pktcount', 'bytecount', 'dur', 'dur_nsec', 'tot_dur', 'flows', 'packetins', 'pktperflow', 'byteperflow', 'pktrate', 'pairflow', 'protocol', 'port_no', 'tx_bytes', 'rx_bytes', 'tx_kbps', 'rx_kbps', 'tot_kbps']
    
    # Validate input JSON
    if not all(field in json_input for field in required_fields):
        return jsonify({'message': 'Missing fields in input data'}), 400

    df = pd.DataFrame([json_input])
    df = df.astype({
        'dt': 'int',
        'switch': 'str',
        'src': 'str',
        'dst': 'str',
        'pktcount': 'int',
        'bytecount': 'int',
        'dur': 'int',
        'dur_nsec': 'int',
        'tot_dur': 'float',
        'flows': 'int',
        'packetins': 'int',
        'pktperflow': 'float',
        'byteperflow': 'float',
        'pktrate': 'float',
        'pairflow': 'str',
        'protocol': 'str',
        'port_no': 'int',
        'tx_bytes': 'int',
        'rx_bytes': 'int',
        'tx_kbps': 'float',
        'rx_kbps': 'float',
        'tot_kbps': 'float'
    })
 
    print(df.dtypes)
    # Instantiate the TrafficClassifier outside the try block
    classifier = TrafficClassifier()

    try:
        classified_data = classifier.classify(df)
        save_classification(classified_data.to_dict(orient='records'))
        classification_result = classified_data.iloc[0]['classification']

        return jsonify({'Hasil_klasifikasi_Jaringan': classification_result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(port=args.port, debug=True)

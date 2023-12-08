import pandas as pd
from app import app
from flask import jsonify, request
from model import predict_traffic  # Import the predict_traffic function from model.py

@app.route('/predict', methods=['POST'])
def predict():
    json_input = request.get_json()
    df = pd.DataFrame([json_input])
    classified_data = predict_traffic(df)
    return jsonify(classified_data.to_dict(orient='records')), 200

# Endpoint untuk menguji koneksi dan fungsi API
@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        # Jika ada data yang dikirim, tampilkan data tersebut
        data = request.get_json()
        return jsonify({'message': 'Data received', 'data': data}), 200
    else:
        # Jika tidak ada data, kirim pesan bahwa API berfungsi
        return jsonify({'message': 'API is working!'}), 200

# Endpoint untuk menguji model klasifikasi
@app.route('/test-predict', methods=['POST'])
def test_predict():
    # Similar to the '/predict' endpoint, but for testing purposes
    json_input = request.get_json()
    df = pd.DataFrame([json_input])
    classified_data = predict_traffic(df)
    return jsonify(classified_data.to_dict(orient='records')), 200

if __name__ == '__main__':
    app.run(debug=True)

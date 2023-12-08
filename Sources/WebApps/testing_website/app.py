# app.py
from flask import Flask, request, jsonify
from server import logger  

app = Flask(__name__)

@app.route('/log-traffic', methods=['POST'])
def log_traffic():
    data = request.json
    logger.save_log_to_supabase(data)
    return jsonify({"message": "Log saved successfully"}), 201

@app.route('/start-sniffing', methods=['GET'])
def start_sniffing():
    logger.start_sniffing()
    return jsonify({"message": "Sniffing started successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)

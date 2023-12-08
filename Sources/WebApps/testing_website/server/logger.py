from flask import Flask, request, jsonify, send_from_directory
from scapy.all import sniff, IP, TCP
import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
from threading import Thread

load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

app = Flask(__name__)

# Set the path where your 'index.html' is located
html_path = '../index.html'

def save_log_to_supabase(log_data):
    response = supabase.table('hasil_klasifikasi').insert(log_data).execute()

def packet_callback(packet):
    if IP in packet and TCP in packet and (
        (packet[IP].src == '127.0.0.1' and packet[TCP].dport == 8081) or
        (packet[IP].dst == '127.0.0.1' and packet[TCP].sport == 8081)
    ):
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst

        log_data = {
            'created_at': datetime.now().isoformat(),
            'src': src_ip,
            'dst': dst_ip,
            'pktcount': 1,
            'byteperflow': len(packet),
            'pktperflow': 1,
            'pktrate': 1 / (datetime.now().timestamp() - packet.time),
            'tot_kbps': len(packet) * 8 / 1000,
            'rx_kbps': len(packet) * 8 / 1000,
            'flows': 1,
            'bytecount': len(packet),
            'dt': datetime.now().isoformat(),
            'protocol': 'TCP',
            'dur': int(packet.time),
            'tot_dur': int(packet.time),
        }
        log_data["dt"] = datetime.now().isoformat()
        save_log_to_supabase(log_data)

def sniff_packets():
    sniff(prn=packet_callback, filter="host 127.0.0.1 and port 8081", store=0)

@app.route('/log-traffic', methods=['POST'])
def log_traffic():
    data = request.json
    save_log_to_supabase(data)
    return jsonify({"message": "Log saved successfully"}), 201

@app.route('/')
def serve_index():
    return send_from_directory(os.path.dirname(html_path), 'index.html')

if __name__ == '__main__':
    # Jalankan sniffing di thread terpisah
    sniff_thread = Thread(target=sniff_packets)
    sniff_thread.start()

    # Jalankan aplikasi Flask di thread utama
    app.run(port=3000, debug=True)

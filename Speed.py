from flask import Flask, jsonify
import os
import speedtest

app = Flask(__name__)

def run_speedtest():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download = round(st.download() / 1_000_000, 2)  # in Mbps
        upload = round(st.upload() / 1_000_000, 2)      # in Mbps
        ping = round(st.results.ping, 2)                # in ms
        return ping, download, upload
    except Exception as e:
        print("⚠️ Speedtest failed:", e)
        return None, None, None

@app.route('/')
def show_speed():
    ping, download_speed, upload_speed = run_speedtest()
    if download_speed is None:
        return jsonify({"error": "Speed test failed"}), 500
    return jsonify({
        "ping_ms": ping,
        "download_mbps": download_speed,
        "upload_mbps": upload_speed
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

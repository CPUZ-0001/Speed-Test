from flask import Flask, jsonify
import subprocess
import os

app = Flask(__name__)

def run_speedtest():
    try:
        # Run CLI and capture output
        result = subprocess.check_output(["speedtest-cli", "--simple"]).decode()
        lines = result.strip().split("\n")

        ping = float(lines[0].split()[1])
        download = float(lines[1].split()[1])
        upload = float(lines[2].split()[1])
        return ping, download, upload
    except Exception as e:
        return None, None, None

# Run test only once on start
ping, download_speed, upload_speed = run_speedtest()

@app.route('/')
def show_speed():
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

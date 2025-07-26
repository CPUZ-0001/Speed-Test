# Speed.py

from flask import Flask, jsonify
import speedtest
import os

app = Flask(__name__)

@app.route("/")
def run_speedtest():
    st = speedtest.Speedtest()
    st.get_best_server()
    download = st.download()
    upload = st.upload()

    return jsonify({
        "download_mbps": round(download / 1_000_000, 2),
        "upload_mbps": round(upload / 1_000_000, 2)
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Render sets this env var
    app.run(host="0.0.0.0", port=port)

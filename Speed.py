# web_speedtest.py
from flask import Flask, jsonify
import speedtest

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
    app.run(host="0.0.0.0", port=8080)

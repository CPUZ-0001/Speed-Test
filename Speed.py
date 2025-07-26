from flask import Flask, jsonify
import speedtest
import os

app = Flask(__name__)

# Run the test once on startup
print("🌐 Testing internet speed...")
st = speedtest.Speedtest()
download_speed = round(st.download() / 1_000_000, 2)
upload_speed = round(st.upload() / 1_000_000, 2)
print(f"⬇️ Download Speed : {download_speed} Mbps")
print(f"⬆️ Upload Speed   : {upload_speed} Mbps")

@app.route('/')
def get_speed():
    return jsonify({
        "download_mbps": download_speed,
        "upload_mbps": upload_speed
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

import speedtest
import time

def check_bandwidth(duration_seconds=60):
    print(f"🌐 Running internet speed test for {duration_seconds} seconds...\n")
    
    st = speedtest.Speedtest()
    st.get_best_server()
    
    end_time = time.time() + duration_seconds
    download_speeds = []
    upload_speeds = []

    while time.time() < end_time:
        try:
            dl = st.download()
            ul = st.upload()
            download_speeds.append(dl)
            upload_speeds.append(ul)

            print(f"✔️ Sample: ⬇️ {dl / 1_000_000:.2f} Mbps | ⬆️ {ul / 1_000_000:.2f} Mbps")

        except Exception as e:
            print(f"❌ Error during test: {e}")
        
        time.sleep(5)  # Pause 5 seconds between samples (adjustable)

    if download_speeds and upload_speeds:
        avg_dl = sum(download_speeds) / len(download_speeds)
        avg_ul = sum(upload_speeds) / len(upload_speeds)

        print("\n📊 Test Summary:")
        print(f"➡️ Samples Taken: {len(download_speeds)}")
        print(f"📶 Average Download Speed : {avg_dl / 1_000_000:.2f} Mbps")
        print(f"📤 Average Upload Speed   : {avg_ul / 1_000_000:.2f} Mbps")
    else:
        print("⚠️ No successful samples collected.")

if __name__ == "__main__":
    check_bandwidth(duration_seconds=60)

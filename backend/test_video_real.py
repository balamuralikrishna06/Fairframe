import requests

with open("real_test.mp4", "rb") as f:
    files = {"file": ("real_test.mp4", f, "video/mp4")}
    r = requests.post("http://127.0.0.1:8000/api/video/analyze", files=files)
    print("STATUS:", r.status_code)
    try:
        data = r.json()
        if r.status_code == 200:
            print("SUCCESS!")
            print("overall_bias_score:", data.get("overall_bias_score"))
            print("reasoning:", data.get("reasoning", "")[:200])
        else:
            print("ERROR:", data.get("detail"))
    except:
        print("RAW:", r.text[:500])

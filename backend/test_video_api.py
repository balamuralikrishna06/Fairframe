import requests

url = "http://localhost:8000/api/video/analyze"
with open("test.py", "rb") as f: # Just sending a file that exists, backend validator only checks content type string, let's see if ffmpeg parses it or fails cleanly.
    files = {"file": ("test.mp4", f, "video/mp4")}
    headers = {"x-user-id": "test-user-id"}
    response = requests.post(url, files=files, headers=headers)
    print("STATUS:", response.status_code)
    try:
        print("JSON:", response.json())
    except:
        print("TEXT:", response.text)

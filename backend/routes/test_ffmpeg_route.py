import sys
import subprocess
from fastapi import APIRouter

router = APIRouter()

@router.get("/test-ffmpeg")
def test_ffmpeg():
    try:
        res = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        return {"stdout": res.stdout, "stderr": res.stderr}
    except Exception as e:
        return {"error": str(e)}

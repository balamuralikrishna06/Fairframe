from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routes import text_bias, image_bias, audio_bias, video_bias, test_ffmpeg_route
import uvicorn

app = FastAPI(title="Fair Frame API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(text_bias.router, prefix="/api/text", tags=["Text"])
app.include_router(image_bias.router, prefix="/api/image", tags=["Image"])
app.include_router(audio_bias.router, prefix="/api/audio", tags=["Audio"])
app.include_router(video_bias.router, prefix="/api/video", tags=["Video"])
app.include_router(test_ffmpeg_route.router, prefix="/api/test", tags=["Test"])

@app.get("/")
async def root():
    return {"message": "Welcome to Fair Frame AI API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

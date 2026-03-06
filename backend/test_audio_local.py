import asyncio
from services.groq_service import GroqService

async def test():
    gs = GroqService()
    # Let's create a dummy wav file
    with open("dummy.wav", "wb") as f:
        # 44 bytes of empty wav header
        f.write(b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00')
    
    try:
        res = await gs.transcribe_audio("dummy.wav")
        print("RESULT:")
        print(res)
    except Exception as e:
        print("EXCEPTION:")
        print(e)

if __name__ == "__main__":
    asyncio.run(test())

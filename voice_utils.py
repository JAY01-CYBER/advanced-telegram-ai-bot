import os
import openai

async def transcribe_audio(file_path: str) -> str:
    try:
        with open(file_path, "rb") as f:
            resp = openai.Audio.transcribe("whisper-1", f)
        return resp["text"]
    except Exception as e:
        print("Transcribe error:", e)
        return None

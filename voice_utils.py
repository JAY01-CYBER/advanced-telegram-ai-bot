import openai

def speech_to_text(filename):
    try:
        audio_file = open(filename, "rb")
        transcript = openai.Audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        return transcript.text
    except Exception:
        return "Could not recognize the voice."

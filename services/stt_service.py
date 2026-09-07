from openai import OpenAI
from config import Config


client = OpenAI(
    api_key=Config.OPENAI_API_KEY
)


def transcribe_audio(audio_path):
    """
    Convert processed audio into text using OpenAI STT.
    """

    with open(audio_path, "rb") as audio_file:

        response = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_file
        )

    return response.text


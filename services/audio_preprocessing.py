from pathlib import Path
import subprocess
import tempfile
import os


def preprocess_audio(audio_file):
    """
    Preprocess uploaded audio:
    1. Convert to WAV
    2. Convert to mono
    3. Resample to 16 kHz
    4. Reduce background noise
    5. Normalize audio volume

    Returns:
        Path to processed WAV file
    """

    suffix = Path(audio_file.filename).suffix or ".audio"

    # Save uploaded audio temporarily
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp_input:

        audio_file.save(temp_input.name)
        input_path = temp_input.name

    # Temporary output file
    output_path = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    ).name

    command = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,

        # Convert to mono
        "-ac",
        "1",

        # Resample to 16 kHz
        "-ar",
        "16000",

        # Noise reduction + normalization
        "-af",
        "afftdn,loudnorm",

        # Standard WAV format
        "-c:a",
        "pcm_s16le",

        output_path
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    # Remove temporary original
    try:
        os.remove(input_path)
    except OSError:
        pass

    if result.returncode != 0:

        try:
            os.remove(output_path)
        except OSError:
            pass

        raise RuntimeError(
            f"Audio preprocessing failed:\n{result.stderr}"
        )

    return output_path

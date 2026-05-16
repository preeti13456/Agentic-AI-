"""
tts.py — Text-to-Speech using gTTS with reliable cross-platform playback.

Bug fix: the original code used `delete=True` on the NamedTemporaryFile,
which deleted the file before the OS audio player could open it on
Windows and some Linux setups.  We now write to a persistent temp path,
play it, then clean up manually.
"""

import os
import platform
import tempfile

from gtts import gTTS


def speak(text: str, lang: str = "en") -> None:
    """
    Convert *text* to speech and play it through the system audio.

    Falls back gracefully if playback fails (e.g. no audio device in CI).
    """
    if not text or not text.strip():
        return

    # Write to a temp file that we control (no auto-delete)
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".mp3")
    os.close(tmp_fd)  # close the fd; gTTS opens the path itself

    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(tmp_path)

        system = platform.system()
        if system == "Windows":
            # `start` is async on Windows; wait for it with /WAIT
            os.system(f'start /WAIT "" "{tmp_path}"')
        elif system == "Darwin":
            os.system(f'afplay "{tmp_path}"')
        else:
            # Linux: try mpg123, fall back to ffplay, then aplay
            if os.system(f'mpg123 -q "{tmp_path}" 2>/dev/null') != 0:
                if os.system(f'ffplay -nodisp -autoexit -loglevel quiet "{tmp_path}" 2>/dev/null') != 0:
                    os.system(f'aplay "{tmp_path}" 2>/dev/null')

    except Exception as e:
        print(f"[TTS] Playback error: {e}")

    finally:
        # Always remove the temp file
        try:
            os.remove(tmp_path)
        except OSError:
            pass

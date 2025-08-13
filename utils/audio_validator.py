from pathlib import Path
import requests,tempfile
import webrtcvad
from pydub import AudioSegment
import tempfile
import threading
import time

SUPPORTED_FORMATS = {'.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac'}

def validate_audio_file(file_path: str) -> tuple[bool, str]:
    
    if not file_path:
        return False, "File path is empty"
    
    path = Path(file_path)
    
    if not path.exists():
        return False, f"File not found: {file_path}"
    
    if not path.is_file():
        return False, f"Path is not a file: {file_path}"
    
    if path.suffix.lower() not in SUPPORTED_FORMATS:
        return False, f"Unsupported format: {path.suffix}. Supported: {SUPPORTED_FORMATS}"
    
    return True, ""

# if url is given saves as a temp file and then the temp file path is given
def get_local_audio_path(audio_path: str)->str:

    if audio_path.startswith("http://") or audio_path.startswith("https://"):
        response = requests.get(audio_path)
        response.raise_for_status()
        suffix = Path(audio_path).suffix or ".tmp"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.write(response.content)
        temp_file.close()
        return temp_file.name
    return audio_path


# wrote this funtionn to chunk audio for better processing but made the application slow
# def chunk_audio(audio_path: str, chunk_length_ms: int = 5000) -> list[str]:
#     audio = AudioSegment.from_file(audio_path)
#     vad = webrtcvad.Vad(2)  # Moderately aggressive
    
#     # Create a temp directory to store chunk files
#     temp_dir = tempfile.TemporaryDirectory(prefix="audio_chunks_")
#     chunk_files = []
    
#     def cleanup_files_later(directory, delay_seconds=300):
#         """Delete temp directory and all files after delay_seconds (default 5 minutes)."""
#         def _cleanup():
#             time.sleep(delay_seconds)
#             directory.cleanup()  # This deletes the directory and all its contents
#         threading.Thread(target=_cleanup, daemon=True).start()
    
#     # Start cleanup thread to delete after 5 minutes
#     cleanup_files_later(temp_dir)
    
#     for i in range(0, len(audio), chunk_length_ms):
#         chunk = audio[i:i+chunk_length_ms]
#         pcm_chunk = chunk.set_frame_rate(16000).set_channels(1).set_sample_width(2).raw_data
        
#         frame_duration = 30  # ms
#         frame_size = int(16000 * (frame_duration / 1000.0) * 2)  # sample_rate * duration * bytes_per_sample
        
#         frames = [pcm_chunk[start:start+frame_size] for start in range(0, len(pcm_chunk), frame_size)]
        
#         speech_detected = any(vad.is_speech(frame, sample_rate=16000) for frame in frames if len(frame) == frame_size)
        
#         if speech_detected:
#             chunk_path = Path(temp_dir.name) / f"chunk_{i//chunk_length_ms}.wav"
#             chunk.export(chunk_path, format="wav")
#             chunk_files.append(str(chunk_path))
    
#     return chunk_files

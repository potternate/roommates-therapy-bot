import os
import time
import threading
import queue
import numpy as np
import wave
import pyaudio
import speech_recognition as sr
from pydub import AudioSegment
import webrtcvad
import torch
# Try different import formats for pyannote
try:
    from pyannote.audio import Pipeline
except ImportError:
    try:
        from pyannote_audio import Pipeline
    except ImportError:
        print("Warning: Could not import pyannote audio. Speaker diarization will be limited.")
        Pipeline = None
from scipy.io import wavfile
import tempfile

# Global variables
audio_queue = queue.Queue()
is_recording = False
recognizer = sr.Recognizer()
vad = webrtcvad.Vad(3)  # Aggressiveness level 3 (highest)

# Initialize speaker diarization pipeline
diarization_pipeline = None

# Only attempt to initialize if Pipeline is available
if Pipeline is not None:
    try:
        # Check if HuggingFace token is available
        hf_token = os.environ.get("HF_TOKEN")
        if hf_token:
            diarization_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.0",
                use_auth_token=hf_token
            )
        else:
            print("Warning: HF_TOKEN not found. Speaker diarization will be limited.")
    except Exception as e:
        print(f"Error loading diarization pipeline: {e}")
else:
    print("Warning: PyAnnote Pipeline not available. Using fallback speaker identification.")


class AudioRecorder:
    def __init__(self, sample_rate=16000, chunk_size=1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.is_recording = False
        self.temp_dir = tempfile.mkdtemp()
        
    def start_recording(self):
        """Start recording audio"""
        self.frames = []
        self.is_recording = True
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=self._callback
        )
        self.stream.start_stream()
        print("Recording started...")
        
    def _callback(self, in_data, frame_count, time_info, status):
        """Callback function for audio stream"""
        self.frames.append(in_data)
        return (in_data, pyaudio.paContinue)
    
    def stop_recording(self):
        """Stop recording and return the recorded audio"""
        if not self.is_recording:
            return None
            
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
        print("Recording stopped.")
        
        # Save the recorded audio to a temporary WAV file
        if not self.frames:
            return None
            
        temp_file = os.path.join(self.temp_dir, f"recording_{int(time.time())}.wav")
        wf = wave.open(temp_file, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        
        return temp_file
    
    def close(self):
        """Clean up resources"""
        if self.stream:
            self.stream.close()
        self.p.terminate()


def transcribe_audio(audio_file):
    """Transcribe audio file using Google Speech Recognition"""
    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""


def identify_speakers(audio_file):
    """
    Identify different speakers in the audio file using pyannote.audio
    Returns a list of segments with speaker labels and timestamps
    """
    if diarization_pipeline is None:
        # Fallback to a simpler method if diarization is not available
        return [{"speaker": "unknown", "text": transcribe_audio(audio_file)}]
    
    try:
        # Run diarization
        diarization = diarization_pipeline(audio_file)
        
        # Extract segments
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            # Get audio segment
            start_time = turn.start
            end_time = turn.end
            
            # Create a temporary file for this segment
            temp_segment = os.path.join(os.path.dirname(audio_file), f"segment_{speaker}_{start_time}_{end_time}.wav")
            
            # Extract segment from original audio
            audio = AudioSegment.from_wav(audio_file)
            segment_audio = audio[start_time*1000:end_time*1000]
            segment_audio.export(temp_segment, format="wav")
            
            # Transcribe segment
            text = transcribe_audio(temp_segment)
            
            if text:
                segments.append({
                    "speaker": speaker,
                    "start": start_time,
                    "end": end_time,
                    "text": text
                })
            
            # Clean up temporary file
            os.remove(temp_segment)
            
        return segments
    except Exception as e:
        print(f"Error in speaker identification: {e}")
        return [{"speaker": "unknown", "text": transcribe_audio(audio_file)}]


def process_audio_for_therapy(audio_file):
    """
    Process audio file for therapy session:
    1. Identify speakers
    2. Transcribe what each speaker said
    3. Return structured data for the therapy bot
    """
    segments = identify_speakers(audio_file)
    
    # If we only have one segment with unknown speaker, try to split by silence
    if len(segments) == 1 and segments[0]["speaker"] == "unknown":
        text = segments[0]["text"]
        # Very basic attempt to split by natural pauses
        sentences = text.split('. ')
        if len(sentences) > 1:
            # Alternate speakers for sentences
            new_segments = []
            for i, sentence in enumerate(sentences):
                if not sentence.strip():
                    continue
                new_segments.append({
                    "speaker": f"Speaker {i % 2 + 1}",
                    "text": sentence.strip()
                })
            segments = new_segments
    
    # Map speakers to Person 1 and Person 2
    speaker_mapping = {}
    for segment in segments:
        speaker = segment["speaker"]
        if speaker not in speaker_mapping:
            speaker_mapping[speaker] = f"Person {len(speaker_mapping) + 1}"
    
    # Apply mapping
    for segment in segments:
        segment["mapped_speaker"] = speaker_mapping[segment["speaker"]]
    
    return segments


def start_voice_recording():
    """Start recording voice in a separate thread"""
    global is_recording
    
    if is_recording:
        return False
    
    is_recording = True
    recorder = AudioRecorder()
    
    def record_thread():
        global is_recording
        recorder.start_recording()
        
        # Record for a maximum of 60 seconds
        max_time = 60
        start_time = time.time()
        
        while is_recording and (time.time() - start_time) < max_time:
            time.sleep(0.1)
        
        audio_file = recorder.stop_recording()
        recorder.close()
        
        if audio_file:
            # Process the audio file
            segments = process_audio_for_therapy(audio_file)
            
            # Put the processed segments in the queue
            audio_queue.put(segments)
            
            # Clean up the audio file
            os.remove(audio_file)
        
        is_recording = False
    
    # Start recording in a separate thread
    threading.Thread(target=record_thread).start()
    return True


def stop_voice_recording():
    """Stop the current voice recording"""
    global is_recording
    is_recording = False
    return True


def get_processed_voice():
    """Get processed voice data if available"""
    if not audio_queue.empty():
        return audio_queue.get()
    return None

import os
import asyncio
import base64
import io
import traceback

import cv2
import pyaudio
import PIL.Image
import mss

import argparse

import speech_recognition as sr
import threading
from queue import Queue

from google import genai
from google.genai import types

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, try to load manually
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    os.environ[key] = value

FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

MODEL = "models/gemini-2.5-flash-native-audio-preview-12-2025"

DEFAULT_MODE = "screen"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(
    http_options={"api_version": "v1beta"},
    api_key=os.environ.get("GEMINI_API_KEY"),
)


CONFIG = types.LiveConnectConfig(
    response_modalities=[
        "AUDIO",
    ],
    media_resolution="MEDIA_RESOLUTION_MEDIUM",
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
        )
    ),
    context_window_compression=types.ContextWindowCompressionConfig(
        trigger_tokens=25600,
        sliding_window=types.SlidingWindow(target_tokens=12800),
    ),
)

pya = pyaudio.PyAudio()

class VoiceToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.audio_queue = Queue()
        self.is_running = False

        self.recognizer.energy_threshold = 300  # Minimum audio energy to consider for recording
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = 0.8  # Seconds of non-speaking audio before phrase is complete
        self.recognizer.operation_timeout = None  # No timeout for recognition operation
        
        
        # Calibrate for ambient noise
        print("Calibrating microphone for ambient noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        print("Microphone calibrated!")
    
    def start_listening(self):
        """Start continuous listening in a separate thread"""
        self.is_running = True
        self.listen_thread = threading.Thread(target=self._listen_continuously)
        self.listen_thread.daemon = True
        self.listen_thread.start()
    
    def stop_listening(self):
        """Stop the continuous listening"""
        self.is_running = False
        if hasattr(self, 'listen_thread'):
            self.listen_thread.join()
    
    def _listen_continuously(self):
        """Continuously listen for audio and add to queue"""
        with self.microphone as source:
            while self.is_running:
                try:
                    # Listen for audio with timeout
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=15)
                    self.audio_queue.put(audio)
                except sr.WaitTimeoutError:
                    pass  # Continue if no audio detected
                except Exception as e:
                    if self.is_running:  # Only print error if we're still supposed to be running
                        print(f"Error in continuous listening: {e}")
    
    def process_audio_queue(self):
        """Process audio from queue and convert to text"""
        while not self.audio_queue.empty():
            try:
                audio = self.audio_queue.get_nowait()
                # Use Google's speech recognition
                text = self.recognizer.recognize_google(audio)
                print(f"\n[USER SPEECH]: {text}")
            except sr.UnknownValueError:
                print("\n")
                #print("\n[USER SPEECH]: Could not understand audio")
            except sr.RequestError as e:
                print(f"\n[USER SPEECH]: Error with speech recognition service: {e}")
            except Exception as e:
                print(f"\n[USER SPEECH]: Unexpected error: {e}")

class AudioLoop:
    def __init__(self, video_mode=DEFAULT_MODE, enable_voice_to_text=True):
        self.video_mode = video_mode

        self.audio_in_queue = asyncio.Queue()
        self.out_queue = asyncio.Queue()

        self.session = None

        self.send_text_task = None
        self.receive_audio_task = None
        self.play_audio_task = None

        self.enable_voice_to_text = enable_voice_to_text
        if self.enable_voice_to_text:
            self.voice_to_text = VoiceToText()

    async def process_voice_to_text(self):
        """Background task to process voice-to-text conversion"""
        if not hasattr(self, 'enable_voice_to_text') or not self.enable_voice_to_text:
            return
            
        while True:
            await asyncio.sleep(0.5)  # Check every 500ms
            await asyncio.to_thread(self.voice_to_text.process_audio_queue)

    async def send_text(self):
        while True:
            text = await asyncio.to_thread(
                input,
                "message > ",
            )
            if text.lower() == "q":
                break
            await self.session.send(input=text or ".", end_of_turn=True)

    def _get_frame(self, cap):
        # Read the frame
        ret, frame = cap.read()
        # Check if the frame was read successfully
        if not ret:
            return None
        # Fix: Convert BGR to RGB color space
        # OpenCV captures in BGR but PIL expects RGB format
        # This prevents the blue tint in the video feed
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(frame_rgb)  # Now using RGB frame
        img.thumbnail([1024, 1024])

        image_io = io.BytesIO()
        img.save(image_io, format="jpeg")
        image_io.seek(0)

        mime_type = "image/jpeg"
        image_bytes = image_io.read()
        return {"mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()}

    async def get_frames(self):
        # This takes about a second, and will block the whole program
        # causing the audio pipeline to overflow if you don't to_thread it.
        cap = await asyncio.to_thread(
            cv2.VideoCapture, 0
        )  # 0 represents the default camera

        while True:
            frame = await asyncio.to_thread(self._get_frame, cap)
            if frame is None:
                break

            await asyncio.sleep(1.0)

            await self.out_queue.put(frame)

        # Release the VideoCapture object
        cap.release()

    def _get_screen(self):
        sct = mss.mss()
        monitor = sct.monitors[0]

        i = sct.grab(monitor)

        mime_type = "image/jpeg"
        image_bytes = mss.tools.to_png(i.rgb, i.size)
        img = PIL.Image.open(io.BytesIO(image_bytes))

        image_io = io.BytesIO()
        img.save(image_io, format="jpeg")
        image_io.seek(0)

        image_bytes = image_io.read()
        return {"mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()}

    async def get_screen(self):
        while True:
            frame = await asyncio.to_thread(self._get_screen)
            if frame is None:
                break

            await asyncio.sleep(1.0)

            await self.out_queue.put(frame)

    async def send_realtime(self):
        while True:
            msg = await self.out_queue.get()
            await self.session.send(input=msg)
            await asyncio.sleep(0.01) # Small yield to event loop

    async def listen_audio(self):
        mic_info = pya.get_default_input_device_info()
        self.audio_stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )
        if __debug__:
            kwargs = {"exception_on_overflow": False}
        else:
            kwargs = {}
        while True:
            data = await asyncio.to_thread(self.audio_stream.read, CHUNK_SIZE, **kwargs)
            await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})
            await asyncio.sleep(0) # Yield to event loop

    async def receive_audio(self):
        """Background task to reads from the websocket and write pcm chunks to the output queue"""
        while True:
            turn = self.session.receive()
            async for response in turn:
                if data := response.data:
                    await self.audio_in_queue.put(data)
                    continue
                if text := response.text:
                    print(f"\n[AI TEXT]: {text}")

            # If you interrupt the model, it sends a turn_complete.
            # For interruptions to work, we need to stop playbook.
            # So empty out the audio queue because it may have loaded
            # much more audio than has played yet.
            while not self.audio_in_queue.empty():
                try:
                    self.audio_in_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

    async def play_audio(self):
        stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )
        while True:
            bytestream = await self.audio_in_queue.get()
            await asyncio.to_thread(stream.write, bytestream)

    async def run(self):
        try:
            # Voice-to-text startup
            if hasattr(self, 'enable_voice_to_text') and self.enable_voice_to_text:
                self.voice_to_text.start_listening()
                print("Voice-to-text enabled. Your speech will be displayed as text.")
                
            # Create the Live API session
            async with client.aio.live.connect(model=MODEL, config=CONFIG) as session:
                self.session = session
                
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(self.send_text())
                    tg.create_task(self.listen_audio())
                    tg.create_task(self.send_realtime())
                    tg.create_task(self.receive_audio())
                    tg.create_task(self.play_audio())
                    
                    # Add video tasks based on mode
                    if self.video_mode == "camera":
                        tg.create_task(self.get_frames())
                    elif self.video_mode == "screen":
                        tg.create_task(self.get_screen())
                    
                    # Add voice-to-text task if enabled
                    if hasattr(self, 'enable_voice_to_text') and self.enable_voice_to_text:
                        tg.create_task(self.process_voice_to_text())
                        
        except* Exception as eg:
            traceback.print_exception(type(eg), eg, eg.__traceback__)
            
        finally:
            # Cleanup
            if hasattr(self, 'audio_stream'):
                self.audio_stream.close()
            if hasattr(self, 'enable_voice_to_text') and self.enable_voice_to_text:
                self.voice_to_text.stop_listening()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        type=str,
        default=DEFAULT_MODE,
        help="pixels to stream from",
        choices=["camera", "screen", "none"],
    )
    parser.add_argument(
        "--voice-to-text",
        action="store_true",
        default=True,
        help="Enable voice-to-text conversion (default: True)",
    )
    parser.add_argument(
        "--no-voice-to-text",
        action="store_true",
        help="Disable voice-to-text conversion",
    )
    
    args = parser.parse_args()
    
    # Check if API key is set
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY environment variable is not set.")
        print("Please set your Gemini API key in a .env file or as an environment variable.")
        exit(1)
    
    # Determine if voice-to-text should be enabled
    enable_vtt = args.voice_to_text and not args.no_voice_to_text
    
    main = AudioLoop(video_mode=args.mode, enable_voice_to_text=enable_vtt)
    asyncio.run(main.run())
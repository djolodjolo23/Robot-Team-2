from gtts import gTTS
from pydub import AudioSegment
import os

def text_to_wav(text, filename="output.wav", language='en',
                target_sample_rate=16000, # Example: 16kHz - CHANGE AS NEEDED
                target_channels=1,       # Example: Mono - CHANGE AS NEEDED
                target_sample_width=2):  # Example: 16-bit (2 bytes) - CHANGE AS NEEDED
    """
    Generates a WAV file from the given text, conforming to specific audio properties.

    Args:
        text (str): The string to convert to speech.
        filename (str, optional): The name of the WAV file to save. Defaults to "output.wav".
        language (str, optional): The language of the text. Defaults to 'en'.
        target_sample_rate (int, optional): Desired sample rate in Hz.
        target_channels (int, optional): Desired number of channels (1 for mono, 2 for stereo).
        target_sample_width (int, optional): Desired sample width in bytes (1 for 8-bit, 2 for 16-bit).
    """
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        temp_mp3 = "temp_audio.mp3"
        tts.save(temp_mp3)

        # Load the MP3 and convert to the target WAV format
        audio = AudioSegment.from_mp3(temp_mp3)

        # Set desired properties
        audio = audio.set_frame_rate(target_sample_rate)
        audio = audio.set_channels(target_channels)
        audio = audio.set_sample_width(target_sample_width)

        # Export as WAV
        audio.export(filename, format="wav")
        print(f"Successfully generated '{filename}' with target format.")
        print(f"  Sample Rate: {audio.frame_rate} Hz")
        print(f"  Channels: {audio.channels}")
        print(f"  Sample Width: {audio.sample_width} bytes ({audio.sample_width * 8}-bit)")


    except ImportError:
        print("Pydub library is not installed. Cannot convert to specific WAV format.")
        print("Please install pydub: pip install pydub")
        # Optionally save the MP3 if pydub is missing
        # os.rename(temp_mp3, filename.replace(".wav", ".mp3"))
        # print(f"Saved as '{filename.replace('.wav', '.mp3')}'")
        return
    except Exception as e:
        print(f"Error during audio processing: {e}")
        print("This might be due to ffmpeg not being installed or not found in PATH,")
        print("or an issue with the target audio format parameters.")
        return
    finally:
        if os.path.exists(temp_mp3):
            os.remove(temp_mp3)

# --- Example Usage ---
# IMPORTANT: Replace with actual values required by your robot!
# Common for DJI Tello EDU / RoboMaster:
ROBOT_SAMPLE_RATE = 48000  # Or 32000, check documentation
ROBOT_CHANNELS = 1         # Mono
ROBOT_SAMPLE_WIDTH = 2     # 16-bit

input_string = "You look nice today!"
output_filename = "compliment.wav" # This will be played by the robot

text_to_wav(input_string, output_filename,
            target_sample_rate=ROBOT_SAMPLE_RATE,
            target_channels=ROBOT_CHANNELS,
            target_sample_width=ROBOT_SAMPLE_WIDTH)

# To verify the generated file's properties (optional, for debugging):
# try:
#     check_audio = AudioSegment.from_wav(output_filename)
#     print(f"\nVerification of '{output_filename}':")
#     print(f"  Frame Rate: {check_audio.frame_rate}")
#     print(f"  Channels: {check_audio.channels}")
#     print(f"  Sample Width: {check_audio.sample_width} bytes")
#     print(f"  Duration: {len(check_audio) / 1000.0}s")
# except Exception as e:
# print(f"Could not verify audio file: {e}")
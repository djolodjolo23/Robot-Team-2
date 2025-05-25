from gtts import gTTS
from pydub import AudioSegment
import os

def text_to_wav(text, filename="output.wav", language='en',
                target_sample_rate=16000,
                target_channels=1,
                target_sample_width=2):
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
        # Use a more robust unique temp file name based on the final filename
        base_filename_no_ext = os.path.splitext(os.path.basename(filename))[0]
        temp_mp3 = f"temp_audio_{base_filename_no_ext}_{os.getpid()}.mp3"
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
        print(f"  Text: \"{text}\"")
        print(f"  Sample Rate: {audio.frame_rate} Hz")
        print(f"  Channels: {audio.channels}")
        print(f"  Sample Width: {audio.sample_width} bytes ({audio.sample_width * 8}-bit)")
        print("-" * 30)


    except ImportError:
        print("Pydub library is not installed. Cannot convert to specific WAV format.")
        print("Please install pydub: pip install pydub")
        return
    except Exception as e:
        print(f"Error during audio processing for '{filename}': {e}")
        print("This might be due to ffmpeg not being installed or not found in PATH,")
        print("or an issue with the target audio format parameters.")
        return
    finally:
        if 'temp_mp3' in locals() and os.path.exists(temp_mp3):
            os.remove(temp_mp3)

# --- Robot Audio Configuration ---
# IMPORTANT: Replace with actual values required by your robot!
# Common for DJI Tello EDU / RoboMaster:
ROBOT_SAMPLE_RATE = 48000  # Or 32000, check documentation
ROBOT_CHANNELS = 1         # Mono
ROBOT_SAMPLE_WIDTH = 2     # 16-bit (2 bytes)

# --- List of Office-Appropriate Compliments (Greeting Style) ---
compliments = [
    "You're looking very cheerful today.",
    "That's a great color on you.",
    "You seem full of energy this morning.",
    "It's always nice to see your friendly face.",
    "You look really well today!",
    "You're looking ready for a great day."
]

# --- Generate WAV files for each compliment ---
output_directory = "compliment_audio_greetings" # Changed directory name slightly
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

for i, compliment_text in enumerate(compliments):
    # Sanitize text for filename (simple version, taking first few words)
    # Replace non-alphanumeric characters with underscore, convert to lowercase
    safe_filename_parts = [
        "".join(char if char.isalnum() else "" for char in word)
        for word in compliment_text.lower().split()[:4] # Take up to first 4 words
    ]
    safe_filename_text = "_".join(filter(None, safe_filename_parts)) # Filter out empty strings from sanitization
    if not safe_filename_text: # Fallback if all characters were non-alphanumeric
        safe_filename_text = f"compliment_{i+1}"

    output_filename = os.path.join(output_directory, f"greeting_{i+1}_{safe_filename_text}.wav")

    print(f"Generating audio for: \"{compliment_text}\"")
    text_to_wav(compliment_text, output_filename,
                target_sample_rate=ROBOT_SAMPLE_RATE,
                target_channels=ROBOT_CHANNELS,
                target_sample_width=ROBOT_SAMPLE_WIDTH)

print(f"\nFinished generating all compliment WAV files in '{output_directory}'.")

# --- Optional: Verification of generated files ---
# print("\n--- Verifying generated files (first file as example) ---")
# if compliments:
#     first_compliment_text = compliments[0]
#     safe_filename_parts = [
#         "".join(char if char.isalnum() else "" for char in word)
#         for word in first_compliment_text.lower().split()[:4]
#     ]
#     safe_filename_text = "_".join(filter(None, safe_filename_parts))
#     if not safe_filename_text:
#         safe_filename_text = "compliment_1"
#
#     example_file_to_check = os.path.join(output_directory, f"greeting_1_{safe_filename_text}.wav")
#
#     if os.path.exists(example_file_to_check):
#         try:
#             check_audio = AudioSegment.from_wav(example_file_to_check)
#             print(f"\nVerification of '{example_file_to_check}':")
#             print(f"  Frame Rate: {check_audio.frame_rate}")
#             print(f"  Channels: {check_audio.channels}")
#             print(f"  Sample Width: {check_audio.sample_width} bytes")
#             print(f"  Duration: {len(check_audio) / 1000.0}s")
#         except Exception as e:
#             print(f"Could not verify audio file '{example_file_to_check}': {e}")
#     else:
#         print(f"File '{example_file_to_check}' not found for verification.")
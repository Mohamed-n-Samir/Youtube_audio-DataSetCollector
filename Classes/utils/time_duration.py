import os
from pydub.utils import mediainfo
from pydub import AudioSegment

def is_audio_file(file_path):
    try:
        # Check if the file is an audio file using its metadata
        info = mediainfo(file_path)
        return 'duration' in info
    except:
        return False

def get_audio_duration(file_path):
    try:
        # Load audio file and get duration in seconds
        audio = AudioSegment.from_file(file_path)
        return len(audio) / 1000  # Duration in seconds
    except:
        return 0

def calculate_total_audio_duration(directory):
    total_duration = 0
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if is_audio_file(file_path):
                duration = get_audio_duration(file_path)
                total_duration += duration
                print(f"File: {file} - Duration: {duration / 60:.2f} minutes")
            else:
                print(f"Skipping non-audio file: {file}")
    return total_duration

# Specify the folder containing audio files
folder_path = "./audio"
total_time = calculate_total_audio_duration(folder_path)

print(f"\nTotal audio duration: {total_time / 60:.2f} minutes")

# path = "./audio/Z8het4evBqA_503.456.wav"

# print(is_audio_file(path))
# print(get_audio_duration(path))
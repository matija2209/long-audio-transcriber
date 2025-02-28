# Audio Transcription Tool

This tool transcribes audio files using OpenAI's Whisper API, with support for large files by automatically splitting them into chunks. It includes features for progress tracking and time-stamped output.

## Features

- Transcribe audio files of any size (automatically splits files > 25MB)
- Resume interrupted transcriptions
- Generate timestamped transcriptions
- Group transcriptions into time intervals
- Support for multiple audio formats (mp3, mp4, mpeg, mpga, m4a, wav, webm)


## Prerequisites

- Python 3.8 or higher
- ffmpeg installed on your system
- OpenAI API key


### Installing ffmpeg

**macOS:**
```
brew install ffmpeg
```

**Ubuntu:**
```
sudo apt-get install ffmpeg
```

**Windows:**
```
choco install ffmpeg
```

## Installation

1. Clone the repository:

```
git clone https://github.com/yourusername/audio-transcription-tool.git
cd audio-transcription-tool
```

1. Create and activate virtual environment:

```
python -m venv venv
```

# windows:
```
venv\Scripts\activate
```

# unix:
```
source venv/bin/activate
```

1. Install required packages:

```
pip install -r requirements.txt
```

1. Configure environment:

Create a .env file in the project root and add your OpenAI API key

```
WHISPER_API_KEY="your-api-key-here"
```

## Usage

### Basic Transcription

Transcribes audio file, splitting into chunks if necessary

```
python main.py
```

### Process Transcription into Intervals

Groups transcribed text into time intervals

```
python process_transcription.py
```

## Output Files

- `transcription.txt`: Raw transcription text

- `transcription_timestamps.json`: Complete JSON with timestamps

- `transcription_by_intervals.txt`: Text grouped by time intervals

- `transcription_progress.json`: Progress tracking file

## Configuration

### Main Variables

- `AUDIO_PATH`: Path to input audio file

- `OUTPUT_PATH_TEXT`: Path for output text file

- `MAX_SIZE_MB`: Maximum chunk size (default: 24)


### Interval Processing

Adjust interval size in process_transcription.py

```python
intervals = parse_transcription(interval_minutes=5)
```

## Error Handling

- Progress saved after each chunk

- Automatic resume from last successful chunk

- Delete transcription_progress.json to start fresh

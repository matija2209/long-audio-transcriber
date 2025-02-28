# Building a Long Audio Transcription Tool with OpenAI's Whisper API

In this tutorial, we'll build a robust audio transcription tool that can handle files of any length using OpenAI's Whisper API. The tool automatically splits large files into chunks, tracks progress, and provides timestamped output.

## What We've Built

We've created a Python-based transcription tool that solves several common challenges:
- Handling large audio files (>25MB OpenAI limit)
- Maintaining correct timestamps across file chunks
- Resuming interrupted transcriptions
- Organizing transcribed text into time intervals

### Key Features
- Automatic file splitting
- Progress tracking and resume capability
- Timestamped word-level transcription
- Time-interval grouping of transcriptions
- Support for multiple audio formats

## Step-by-Step Guide

### 1. Project Setup

First, create a new project directory and set up the environment:

```bash
mkdir long-audio-transcriber
cd long-audio-transcriber
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

Install required packages:

```bash
pip install requests ffmpeg-python python-dotenv
```

### 3. Environment Configuration

Create a `.env` file to store your OpenAI API key:

```bash
echo "WHISPER_API_KEY=your-api-key-here" > .env
```

### 4. Core Components

The project consists of two main Python files:

#### main.py
This handles:
- Audio file splitting
- Chunk processing
- Progress tracking
- Transcription merging

Key features:
```python
# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure chunk size
MAX_SIZE_MB = 24

# Progress tracking
def save_progress(chunk_path, transcription):
    progress = load_progress()
    progress['processed_chunks'][chunk_path] = transcription
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)
```

#### process_transcription.py
This handles:
- Time-interval grouping
- Timestamp adjustment
- Output formatting

### 5. Using the Tool

1. **Prepare Your Audio File**
   - Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm
   - No size limitation (automatically splits files)

2. **Run the Transcription**
   ```bash
   python main.py
   ```
   The script will:
   - Split large files if needed
   - Process each chunk
   - Save progress after each chunk
   - Merge results with correct timestamps

3. **Process Time Intervals**
   ```bash
   python process_transcription.py
   ```
   This creates time-grouped transcriptions.

### 6. Output Files

The tool generates several output files:
- `transcription.txt`: Raw transcription text
- `transcription_timestamps.json`: JSON with word-level timestamps
- `transcription_by_intervals.txt`: Text grouped by time intervals
- `transcription_progress.json`: Progress tracking file

## Advanced Features

### Progress Tracking
The tool maintains a progress file that allows you to resume interrupted transcriptions:
```json
{
  "processed_chunks": {
    "chunk_001.wav": {
      "text": "transcribed text...",
      "words": [{"word": "example", "start": 0.0, "end": 0.5}]
    }
  }
}
```

### Time Interval Processing
Transcriptions are grouped into configurable time intervals:
```python
intervals = parse_transcription(interval_minutes=5)  # 5-minute intervals
```

## Error Handling

The tool includes robust error handling:
- Saves progress after each chunk
- Maintains temporary files for resume capability
- Validates input files and API responses

## Best Practices

1. **Large Files**
   - Let the tool handle splitting
   - Don't pre-split audio files
   - Keep original timing information

2. **Progress Management**
   - Don't delete progress files during processing
   - Use them to resume interrupted jobs
   - Clear them only when starting fresh

3. **Time Intervals**
   - Choose interval size based on content
   - Smaller intervals for detailed navigation
   - Larger intervals for overview

## Conclusion

This tool makes it practical to transcribe long audio files using OpenAI's Whisper API. It handles the complexities of file splitting, progress tracking, and timestamp management, allowing you to focus on using the transcriptions rather than managing the technical details.

The complete code is available on GitHub: [long-audio-transcriber](https://github.com/matija2209/long-audio-transcriber) 
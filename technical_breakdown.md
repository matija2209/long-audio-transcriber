# Technical Breakdown: Building the Long Audio Transcription Tool

## 1. Audio File Splitting Implementation

We used ffmpeg to split large audio files into manageable chunks:

```python
def split_audio_file(file_path):
    """Split audio file into chunks smaller than 25MB."""
    # Get audio duration using ffmpeg
    total_duration = get_audio_duration(file_path)
    file_size = os.path.getsize(file_path)
    
    # Calculate optimal number of chunks
    num_chunks = (file_size / (MAX_SIZE_MB * 1024 * 1024)) + 1
    chunk_duration = total_duration / num_chunks
    
    chunks = []
    for i in range(int(num_chunks)):
        start_time = i * chunk_duration
        chunk_path = f"temp_chunks/chunk_{i:03d}.wav"
        
        # Extract chunk using ffmpeg
        stream = ffmpeg.input(file_path, ss=start_time, t=chunk_duration)
        stream = ffmpeg.output(stream, chunk_path, acodec='pcm_s16le')
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        
        chunks.append(chunk_path)
```

Key points:
- Used ffmpeg for precise audio splitting
- Maintained PCM WAV format for best quality
- Calculated chunk size based on file size and duration
- Preserved timing information for later merging

## 2. OpenAI API Setup

1. Get API Key:
   - Go to https://platform.openai.com/
   - Sign up/Login
   - Navigate to API Keys section
   - Create new secret key
   - Save key in `.env` file:
   ```
   WHISPER_API_KEY="your-key-here"
   ```

2. API Configuration:
```python
def transcribe_chunk(chunk_path, is_first_chunk=""):
    """Transcribe a single chunk with timestamps."""
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    with open(chunk_path, "rb") as audio_file:
        files = {"file": audio_file}
        data = {
            "model": "whisper-1",
            "language": "sl",
            "response_format": "verbose_json",
            "timestamp_granularities[]": "word"
        }
        
        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
```

## 3. Progress Tracking System

We implemented a robust progress tracking system:

1. Progress File Structure:
```python
def save_progress(chunk_path, transcription):
    """Save progress after each chunk is processed."""
    progress = load_progress()
    progress['processed_chunks'][chunk_path] = transcription
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)
```

2. Progress Loading:
```python
def load_progress():
    """Load progress from file if it exists."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {'processed_chunks': {}, 'completed': False}
```

3. Completion Tracking:
```python
def mark_completed():
    """Mark the transcription as completed."""
    progress = load_progress()
    progress['completed'] = True
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)
```

## 4. Timestamp Management

The crucial part was maintaining correct timestamps across chunks:

```python
def merge_transcriptions(transcriptions):
    """Merge multiple transcription chunks."""
    merged_text = ""
    all_words = []
    time_offset = 0
    
    for trans in transcriptions:
        # Add text
        merged_text += trans.get('text', '') + " "
        
        # Adjust timestamps for words
        chunk_words = trans.get('words', [])
        for word in chunk_words:
            word['start'] += time_offset
            word['end'] += time_offset
        all_words.extend(chunk_words)
        
        # Update time offset for next chunk
        if chunk_words:
            time_offset = chunk_words[-1]['end']
```

## 5. Time Interval Processing

We added time-based grouping of transcriptions:

```python
def parse_transcription(progress_file_path="transcription_progress.json", interval_minutes=1):
    # Load all words from chunks
    all_words = []
    time_offset = 0
    
    # Sort chunks by their number to maintain order
    sorted_chunks = sorted(progress_data['processed_chunks'].items())
    
    for chunk_path, chunk_data in sorted_chunks:
        if 'words' in chunk_data:
            chunk_words = chunk_data['words']
            
            # Adjust timestamps for this chunk's words
            for word in chunk_words:
                word['start'] = float(word['start']) + time_offset
                word['end'] = float(word['end']) + time_offset
                all_words.append(word)
            
            # Update offset for next chunk
            if chunk_words:
                time_offset = all_words[-1]['end']
```

## 6. Output Generation

The tool generates three types of output:

1. Raw Text:
```python
with open(OUTPUT_PATH_TEXT, "w", encoding="utf-8") as f:
    f.write(merged_result['text'])
```

2. Timestamped JSON:
```python
with open(OUTPUT_PATH_JSON, "w", encoding="utf-8") as f:
    json.dump(merged_result, f, ensure_ascii=False, indent=2)
```

3. Time-Interval Text:
```python
with open("transcription_by_intervals.txt", "w", encoding="utf-8") as f:
    for time_range, data in sorted_intervals.items():
        f.write(f"\n[{time_range}]\n")
        f.write(data['text'].strip() + "\n")
        f.write("-" * 80 + "\n")
```

## 7. Error Recovery System

We implemented several error recovery mechanisms:

1. Chunk Processing Recovery:
```python
if chunk_path in progress['processed_chunks']:
    print(f"Loading previously processed chunk {i+1}/{len(chunk_paths)}")
    transcriptions.append(progress['processed_chunks'][chunk_path])
    continue
```

2. Temporary File Management:
```python
def cleanup_temp_directory():
    """Remove temporary chunks only after successful completion."""
    if progress.get('completed', False):
        if os.path.exists(CHUNK_DIR):
            for file in os.listdir(CHUNK_DIR):
                os.remove(os.path.join(CHUNK_DIR, file))
            os.rmdir(CHUNK_DIR)
```

This technical breakdown shows how each component works together to create a reliable transcription system that can handle files of any size while maintaining accurate timestamps and providing recovery options. 
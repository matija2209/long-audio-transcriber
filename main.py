import requests
import json
from pathlib import Path
import ffmpeg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
API_KEY = os.getenv("WHISPER_API_KEY")

AUDIO_PATH = "/Users/ziberna/output_fast.wav"
OUTPUT_PATH_TEXT = "transcription.txt"
OUTPUT_PATH_JSON = "transcription_timestamps.json"
CHUNK_DIR = "temp_chunks"
PROGRESS_FILE = "transcription_progress.json"
MAX_SIZE_MB = 24  # Using 24MB to be safe

def load_progress():
    """Load progress from file if it exists."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {'processed_chunks': {}, 'completed': False}

def save_progress(chunk_path, transcription):
    """Save progress after each chunk is processed."""
    progress = load_progress()
    progress['processed_chunks'][chunk_path] = transcription
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def mark_completed():
    """Mark the transcription as completed."""
    progress = load_progress()
    progress['completed'] = True
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def setup_temp_directory():
    """Create temporary directory for chunks if it doesn't exist."""
    if not os.path.exists(CHUNK_DIR):
        os.makedirs(CHUNK_DIR)

def cleanup_temp_directory():
    """Remove temporary chunks."""
    if os.path.exists(CHUNK_DIR):
        for file in os.listdir(CHUNK_DIR):
            os.remove(os.path.join(CHUNK_DIR, file))
        os.rmdir(CHUNK_DIR)

def get_audio_duration(file_path):
    """Get duration of audio file in seconds."""
    probe = ffmpeg.probe(file_path)
    audio_info = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
    return float(probe['format']['duration'])

def split_audio_file(file_path):
    """Split audio file into chunks smaller than 25MB."""
    print(f"Loading audio file: {file_path}")
    
    total_duration = get_audio_duration(file_path)
    file_size = os.path.getsize(file_path)
    
    # Calculate how many chunks we need
    num_chunks = (file_size / (MAX_SIZE_MB * 1024 * 1024)) + 1
    chunk_duration = total_duration / num_chunks
    
    chunks = []
    for i in range(int(num_chunks)):
        start_time = i * chunk_duration
        chunk_path = os.path.join(CHUNK_DIR, f"chunk_{i:03d}.wav")
        
        # Skip if chunk already exists and is processed
        progress = load_progress()
        if chunk_path in progress['processed_chunks']:
            print(f"Chunk {i+1} already processed, skipping creation")
            chunks.append(chunk_path)
            continue
            
        print(f"Creating chunk {i+1}: {chunk_path}")
        
        # Use ffmpeg to extract chunk
        stream = ffmpeg.input(file_path, ss=start_time, t=chunk_duration)
        stream = ffmpeg.output(stream, chunk_path, acodec='pcm_s16le')
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        
        chunks.append(chunk_path)
    
    return chunks

def transcribe_chunk(chunk_path, is_first_chunk=""):
    """Transcribe a single chunk with timestamps."""
    print(f"\nProcessing chunk: {chunk_path}")
    
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
        
        if is_first_chunk:
            print("Sending request for first chunk...")
        response = requests.post(url, headers=headers, files=files, data=data)
        response.raise_for_status()
        
    return response.json()

def merge_transcriptions(transcriptions):
    """Merge multiple transcription chunks."""
    merged_text = ""
    all_words = []
    time_offset = 0
    
    for i, trans in enumerate(transcriptions):
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
    
    return {
        'text': merged_text.strip(),
        'words': all_words
    }

def parse_progress_file(progress_file_path="transcription_progress.json", interval_minutes=1):
    """Parse progress file and group text into minute intervals."""
    try:
        with open(progress_file_path, 'r', encoding='utf-8') as f:
            progress_data = json.load(f)
        
        # Collect all words from all chunks
        all_words = []
        for chunk_data in progress_data['processed_chunks'].values():
            if 'words' in chunk_data:
                all_words.extend(chunk_data['words'])
        
        # Sort words by start time
        all_words.sort(key=lambda x: x['start'])
        
        # Group into minute intervals
        interval_seconds = interval_minutes * 60
        intervals = {}
        
        for word in all_words:
            interval_index = int(word['start'] // interval_seconds)
            start_time = interval_index * interval_seconds
            end_time = start_time + interval_seconds
            
            interval_key = f"{start_time//60:02d}:{start_time%60:02d}-{end_time//60:02d}:{end_time%60:02d}"
            
            if interval_key not in intervals:
                intervals[interval_key] = {
                    'text': '',
                    'words': [],
                    'start_time': start_time,
                    'end_time': end_time
                }
            
            intervals[interval_key]['words'].append(word)
            intervals[interval_key]['text'] += word['text'] + ' '
        
        # Sort intervals by time and create output
        sorted_intervals = dict(sorted(intervals.items(), key=lambda x: x[1]['start_time']))
        
        # Save to file
        output_path = "transcription_by_intervals.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            for time_range, data in sorted_intervals.items():
                f.write(f"\n[{time_range}]\n")
                f.write(data['text'].strip() + "\n")
                f.write("-" * 80 + "\n")
        
        print(f"\nTranscription grouped by {interval_minutes}-minute intervals saved to: {output_path}")
        
        return sorted_intervals
        
    except Exception as e:
        print(f"Error parsing progress file: {str(e)}")
        return None

def main():
    try:
        # Check if previous transcription was completed
        progress = load_progress()
        if progress['completed']:
            print("Previous transcription was completed. Remove progress file to start over.")
            return
            
        print("Starting transcription process...")
        
        # Check if file exists
        if not Path(AUDIO_PATH).is_file():
            print(f"Error: Audio file not found at {AUDIO_PATH}")
            return
        
        # Create temporary directory
        setup_temp_directory()
        
        # Split file if needed
        file_size_mb = os.path.getsize(AUDIO_PATH) / (1024 * 1024)
        if file_size_mb > MAX_SIZE_MB:
            print(f"File size ({file_size_mb:.1f}MB) exceeds {MAX_SIZE_MB}MB limit. Splitting file...")
            chunk_paths = split_audio_file(AUDIO_PATH)
        else:
            chunk_paths = [AUDIO_PATH]
        
        # Process each chunk
        transcriptions = []
        for i, chunk_path in enumerate(chunk_paths):
            try:
                # Check if chunk was already processed
                progress = load_progress()
                if chunk_path in progress['processed_chunks']:
                    print(f"Loading previously processed chunk {i+1}/{len(chunk_paths)}")
                    transcriptions.append(progress['processed_chunks'][chunk_path])
                    continue
                
                is_first_chunk = (i == 0)
                result = transcribe_chunk(chunk_path, is_first_chunk)
                transcriptions.append(result)
                
                # Save progress after each chunk
                save_progress(chunk_path, result)
                
                print(f"Successfully transcribed chunk {i+1}/{len(chunk_paths)}")
            except Exception as e:
                print(f"Error processing chunk {i+1}: {str(e)}")
                raise
        
        # Merge results
        print("\nMerging transcriptions...")
        merged_result = merge_transcriptions(transcriptions)
        
        # Save results
        print(f"Saving plain text transcription to {OUTPUT_PATH_TEXT}")
        with open(OUTPUT_PATH_TEXT, "w", encoding="utf-8") as f:
            f.write(merged_result['text'])
        
        print(f"Saving timestamped transcription to {OUTPUT_PATH_JSON}")
        with open(OUTPUT_PATH_JSON, "w", encoding="utf-8") as f:
            json.dump(merged_result, f, ensure_ascii=False, indent=2)
        
        # Mark transcription as completed
        mark_completed()
        
        # Print sample
        print("\nTranscription completed successfully!")
        print(f"Text version saved to: {OUTPUT_PATH_TEXT}")
        print(f"Timestamped version saved to: {OUTPUT_PATH_JSON}")
        
        print("\nFirst few words with timestamps:")
        for word in merged_result['words'][:5]:
            print(f"Word: {word['text']}, Start: {word['start']:.2f}s, End: {word['end']:.2f}s")
            
        if progress.get('completed', False):
            print("\nCreating time-grouped transcription...")
            parse_progress_file(interval_minutes=1)  # You can adjust the interval
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    finally:
        # Don't cleanup if there was an error - keep chunks for resuming
        if progress.get('completed', False):
            cleanup_temp_directory()

if __name__ == "__main__":
    main()
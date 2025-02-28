import json
from pathlib import Path

def parse_transcription(progress_file_path="transcription_progress.json", interval_minutes=1):
    """Parse transcription and group text into minute intervals."""
    try:
        # Check if file exists
        if not Path(progress_file_path).is_file():
            print(f"Error: Progress file not found at {progress_file_path}")
            return None
            
        print(f"Reading transcription from {progress_file_path}")
        with open(progress_file_path, 'r', encoding='utf-8') as f:
            progress_data = json.load(f)
        
        # Collect all words from all chunks and adjust timestamps
        all_words = []
        time_offset = 0
        
        # Sort chunks by their number to maintain order
        sorted_chunks = sorted(progress_data['processed_chunks'].items())
        
        for chunk_path, chunk_data in sorted_chunks:
            print(f"Processing chunk: {chunk_path}")
            if 'words' in chunk_data:
                chunk_words = chunk_data['words']
                
                # Adjust timestamps for this chunk's words
                for word in chunk_words:
                    word['start'] = float(word['start']) + time_offset
                    word['end'] = float(word['end']) + time_offset
                    all_words.append(word)
                
                # Update offset for next chunk
                if chunk_words:
                    time_offset = all_words[-1]['end']  # Use the last word's end time
        
        if not all_words:
            print("No words found in transcription!")
            return None
            
        print(f"Total words found: {len(all_words)}")
        print(f"Total duration: {time_offset:.2f} seconds ({time_offset/60:.1f} minutes)")
        
        # Group into minute intervals
        interval_seconds = interval_minutes * 60
        intervals = {}
        
        for word in all_words:
            interval_index = int(word['start'] // interval_seconds)
            interval_start = interval_index * interval_seconds
            interval_end = interval_start + interval_seconds
            
            interval_key = f"{int(interval_start//60):02d}:{int(interval_start%60):02d}-{int(interval_end//60):02d}:{int(interval_end%60):02d}"
            
            if interval_key not in intervals:
                intervals[interval_key] = {
                    'text': '',
                    'words': [],
                    'start_time': interval_start,
                    'end_time': interval_end
                }
            
            intervals[interval_key]['words'].append(word)
            intervals[interval_key]['text'] += word['word'] + ' '
        
        # Sort intervals by time and create output
        sorted_intervals = dict(sorted(intervals.items(), key=lambda x: x[1]['start_time']))
        
        # Save to file
        output_path = "transcription_by_intervals.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Total duration: {time_offset:.2f} seconds ({time_offset/60:.1f} minutes)\n")
            f.write(f"Number of intervals: {len(sorted_intervals)}\n")
            f.write("-" * 80 + "\n")
            
            for time_range, data in sorted_intervals.items():
                f.write(f"\n[{time_range}]\n")
                f.write(data['text'].strip() + "\n")
                f.write("-" * 80 + "\n")
        
        print(f"\nTranscription grouped by {interval_minutes}-minute intervals saved to: {output_path}")
        
        return sorted_intervals
        
    except Exception as e:
        print(f"Error parsing transcription: {str(e)}")
        raise

if __name__ == "__main__":
    # You can adjust the interval (in minutes)
    intervals = parse_transcription(interval_minutes=5)  # Changed to 5-minute intervals
    
    if intervals:
        print("\nTime ranges found:")
        for time_range in list(intervals.keys())[:5]:  # Show first 5 intervals
            print(time_range) 
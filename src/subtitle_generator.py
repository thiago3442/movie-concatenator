#!/usr/bin/env python3
"""
Subtitle Generator with Audio Analysis
Generates synchronized subtitles for videos based on transcript files.
Uses audio analysis to detect speech segments and align with transcript.
No AI/ML models required - works on CPU-only systems.
"""

import os
import re
from pathlib import Path
from moviepy import VideoFileClip, TextClip, CompositeVideoClip
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import numpy as np
from datetime import timedelta


def parse_transcript(transcript_path):
    """
    Parse transcript file and extract sentences.
    Returns a list of sentences without quotes.
    """
    with open(transcript_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract sentences from lines
    sentences = []
    for line in content.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Check for quotes (Unicode 8220 and 8221, or ASCII 34)
        if len(line) >= 2:
            first_char = ord(line[0])
            last_char = ord(line[-1])
            
            # Unicode left quote (8220) or ASCII quote (34)
            starts_with_quote = first_char in [8220, 34]
            # Unicode right quote (8221) or ASCII quote (34)
            ends_with_quote = last_char in [8221, 34]
            
            if starts_with_quote and ends_with_quote:
                sentence = line[1:-1].strip()
                if sentence:
                    sentences.append(sentence)
    
    return sentences


def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)"""
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    secs = td.seconds % 60
    millis = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def extract_audio_from_video(video_path, output_audio_path):
    """Extract audio from video file."""
    print("  Extracting audio from video...")
    video = VideoFileClip(str(video_path))
    video.audio.write_audiofile(str(output_audio_path), logger=None)
    video.close()


def detect_speech_segments(audio_path, min_silence_len=500, silence_thresh=-40):
    """
    Detect speech segments in audio by finding non-silent parts.
    
    Args:
        audio_path: Path to audio file
        min_silence_len: Minimum length of silence to be used for segment separation (ms)
        silence_thresh: Silence threshold in dBFS
    
    Returns:
        List of (start_ms, end_ms) tuples for speech segments
    """
    print("  Analyzing audio to detect speech segments...")
    
    # Load audio
    audio = AudioSegment.from_file(str(audio_path))
    
    # Detect non-silent chunks
    nonsilent_ranges = detect_nonsilent(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        seek_step=10
    )
    
    print(f"  Found {len(nonsilent_ranges)} speech segments")
    
    return nonsilent_ranges


def merge_close_segments(segments, max_gap_ms=300):
    """
    Merge speech segments that are close together.
    This helps group words into sentences.
    
    Args:
        segments: List of (start_ms, end_ms) tuples
        max_gap_ms: Maximum gap between segments to merge (ms)
    
    Returns:
        List of merged (start_ms, end_ms) tuples
    """
    if not segments:
        return []
    
    merged = []
    current_start, current_end = segments[0]
    
    for start, end in segments[1:]:
        # If gap is small, merge with current segment
        if start - current_end <= max_gap_ms:
            current_end = end
        else:
            # Save current segment and start new one
            merged.append((current_start, current_end))
            current_start, current_end = start, end
    
    # Add the last segment
    merged.append((current_start, current_end))
    
    return merged


def align_transcript_with_segments(transcript_sentences, speech_segments):
    """
    Align transcript sentences with detected speech segments.
    
    Args:
        transcript_sentences: List of sentences from transcript
        speech_segments: List of (start_ms, end_ms) tuples
    
    Returns:
        List of (sentence, start_seconds, end_seconds) tuples
    """
    print("  Aligning transcript with speech segments...")
    
    aligned_subtitles = []
    
    # If we have more segments than sentences, merge segments
    if len(speech_segments) > len(transcript_sentences) * 1.5:
        print(f"  Merging segments (found {len(speech_segments)} segments for {len(transcript_sentences)} sentences)...")
        speech_segments = merge_close_segments(speech_segments, max_gap_ms=400)
        print(f"  After merging: {len(speech_segments)} segments")
    
    # Try to match sentences to segments
    if len(speech_segments) >= len(transcript_sentences):
        # We have enough segments - assign one or more segments per sentence
        segments_per_sentence = len(speech_segments) / len(transcript_sentences)
        
        segment_idx = 0
        for i, sentence in enumerate(transcript_sentences):
            # Calculate how many segments this sentence should span
            start_seg = int(segment_idx)
            segment_idx += segments_per_sentence
            end_seg = min(int(segment_idx), len(speech_segments) - 1)
            
            # Use the start of first segment and end of last segment
            start_ms = speech_segments[start_seg][0]
            end_ms = speech_segments[end_seg][1]
            
            aligned_subtitles.append((
                sentence,
                start_ms / 1000.0,  # Convert to seconds
                end_ms / 1000.0
            ))
    else:
        # We have fewer segments than sentences - distribute sentences across segments
        print(f"  Warning: Only {len(speech_segments)} segments for {len(transcript_sentences)} sentences")
        print("  Distributing sentences across available segments...")
        
        sentences_per_segment = len(transcript_sentences) / len(speech_segments)
        
        sentence_idx = 0
        for seg_start_ms, seg_end_ms in speech_segments:
            # Calculate how many sentences fit in this segment
            start_sent = int(sentence_idx)
            sentence_idx += sentences_per_segment
            end_sent = min(int(sentence_idx) + 1, len(transcript_sentences))
            
            # Combine sentences for this segment
            combined_sentence = " ".join(transcript_sentences[start_sent:end_sent])
            
            if combined_sentence:
                aligned_subtitles.append((
                    combined_sentence,
                    seg_start_ms / 1000.0,
                    seg_end_ms / 1000.0
                ))
    
    print(f"  Successfully created {len(aligned_subtitles)} subtitle entries")
    return aligned_subtitles


def create_srt_file(aligned_subtitles, output_path):
    """Create an SRT subtitle file from aligned subtitles."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for idx, (sentence, start_time, end_time) in enumerate(aligned_subtitles, 1):
            f.write(f"{idx}\n")
            f.write(f"{format_timestamp(start_time)} --> {format_timestamp(end_time)}\n")
            f.write(f"{sentence}\n\n")
    
    print(f"  ✓ Created SRT file: {output_path}")


def add_subtitles_to_video(video_path, srt_path, output_path):
    """Add subtitles to video by burning them in."""
    print(f"  Adding subtitles to video...")
    
    # Load video
    video = VideoFileClip(str(video_path))
    
    # Parse SRT file
    with open(srt_path, 'r', encoding='utf-8') as f:
        srt_content = f.read()
    
    # Extract subtitle entries
    subtitle_pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)'
    matches = re.findall(subtitle_pattern, srt_content, re.DOTALL)
    
    subtitle_clips = []
    
    for _, start_str, end_str, text in matches:
        # Convert SRT timestamp to seconds
        start_time = parse_srt_timestamp(start_str)
        end_time = parse_srt_timestamp(end_str)
        
        # Create text clip with better formatting
        txt_clip = (TextClip(
            text.strip(),
            fontsize=42,
            color='white',
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=2.5,
            method='caption',
            size=(int(video.w * 0.85), None),
            align='center'
        )
        .set_position(('center', 'bottom'), relative=False)
        .set_position(('center', video.h - 100))
        .set_start(start_time)
        .set_duration(end_time - start_time))
        
        subtitle_clips.append(txt_clip)
    
    # Composite video with subtitles
    final_video = CompositeVideoClip([video] + subtitle_clips)
    
    # Write output
    final_video.write_videofile(
        str(output_path),
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True,
        fps=video.fps,
        logger=None
    )
    
    # Clean up
    video.close()
    final_video.close()
    
    print(f"  ✓ Video with subtitles saved: {output_path}")


def parse_srt_timestamp(timestamp_str):
    """Convert SRT timestamp to seconds."""
    time_parts = timestamp_str.replace(',', '.').split(':')
    hours = int(time_parts[0])
    minutes = int(time_parts[1])
    seconds = float(time_parts[2])
    return hours * 3600 + minutes * 60 + seconds


def process_video(video_path, transcript_path, output_dir):
    """
    Process a single video: analyze audio, align transcript, create subtitles.
    
    Args:
        video_path: Path to input video
        transcript_path: Path to transcript file
        output_dir: Directory for output files
    """
    video_name = Path(video_path).stem
    print(f"\n{'='*60}")
    print(f"Processing: {video_name}")
    print('='*60)
    
    # Create temp directory for audio
    temp_dir = Path(output_dir) / 'temp'
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Parse transcript
    print("  Reading transcript...")
    transcript_sentences = parse_transcript(transcript_path)
    print(f"  Found {len(transcript_sentences)} sentences in transcript")
    
    # Extract audio
    audio_path = temp_dir / f"{video_name}.wav"
    extract_audio_from_video(video_path, audio_path)
    
    # Detect speech segments
    speech_segments = detect_speech_segments(
        audio_path,
        min_silence_len=400,  # 400ms of silence to separate segments
        silence_thresh=-45     # Silence threshold in dBFS
    )
    
    # Align transcript with speech segments
    aligned_subtitles = align_transcript_with_segments(
        transcript_sentences,
        speech_segments
    )
    
    # Create SRT file
    srt_path = Path(output_dir) / 'subtitles' / f"{video_name}.srt"
    srt_path.parent.mkdir(parents=True, exist_ok=True)
    create_srt_file(aligned_subtitles, srt_path)
    
    # Add subtitles to video
    output_video_path = Path(output_dir) / f"{video_name}_subtitled.mp4"
    add_subtitles_to_video(video_path, srt_path, output_video_path)
    
    # Clean up temp audio file
    if audio_path.exists():
        audio_path.unlink()
    
    return output_video_path


def main():
    """Main entry point for subtitle generation."""
    video_dir = Path("output_video")
    transcript_dir = Path("transcripts")
    output_dir = Path("output_video_with_subtitles")
    
    output_dir.mkdir(exist_ok=True)
    
    print("\n" + "="*60)
    print("Subtitle Generator - Audio Analysis Based")
    print("="*60)
    print("This tool analyzes audio to detect speech segments")
    print("and synchronizes subtitles with the detected speech.")
    print("="*60)
    
    # Get all video files
    video_files = sorted([
        f for f in video_dir.glob("*.mp4") 
        if not f.stem.endswith('_subtitled') and f.stem != 'concatenated_output'
    ])
    
    if not video_files:
        print("\n✗ No video files found in output_video directory!")
        return
    
    print(f"\nFound {len(video_files)} videos to process")
    
    # Process each video
    successful = 0
    failed = 0
    
    for video_file in video_files:
        video_name = video_file.stem
        transcript_file = transcript_dir / f"{video_name}.txt"
        
        if not transcript_file.exists():
            print(f"\n⚠ Warning: No transcript found for {video_name}, skipping...")
            failed += 1
            continue
        
        try:
            process_video(video_file, transcript_file, output_dir)
            print(f"\n✓ Successfully processed: {video_name}")
            successful += 1
        except Exception as e:
            print(f"\n✗ Error processing {video_name}: {e}")
            failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("Processing Complete!")
    print("="*60)
    print(f"Successfully processed: {successful} videos")
    if failed > 0:
        print(f"Failed: {failed} videos")
    print(f"\nOutput directory: {output_dir}")
    print(f"SRT files saved in: {output_dir / 'subtitles'}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

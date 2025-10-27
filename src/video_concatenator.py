#!/usr/bin/env python3
"""
Video Concatenator
Concatenates multiple .MOV files in numerical order into a single output video.
"""

import os
import re
from pathlib import Path
from moviepy import VideoFileClip, concatenate_videoclips


def extract_number_from_filename(filename):
    """
    Extract the number from a filename like 'Video1.MOV' or 'video2.mov'.
    Returns the number as an integer, or float('inf') if no number is found.
    """
    match = re.search(r'(\d+)', filename)
    if match:
        return int(match.group(1))
    return float('inf')


def get_sorted_video_files(input_dir):
    """
    Get all .MOV files from the input directory, sorted by the number in their filename.
    """
    input_path = Path(input_dir)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory '{input_dir}' does not exist")
    
    # Get all .MOV files (case-insensitive)
    video_files = [
        f for f in input_path.iterdir()
        if f.suffix.lower() in ['.mov', '.mp4', '.avi', '.mkv']
    ]
    
    if not video_files:
        raise ValueError(f"No video files found in '{input_dir}'")
    
    # Sort by the number in the filename
    video_files.sort(key=lambda f: extract_number_from_filename(f.name))
    
    return video_files


def concatenate_videos(input_dir, output_file):
    """
    Concatenate all video files from input_dir into a single output file.
    
    Args:
        input_dir (str): Directory containing input video files
        output_file (str): Path to the output concatenated video file
    """
    print(f"Scanning for videos in: {input_dir}")
    
    # Get sorted video files
    video_files = get_sorted_video_files(input_dir)
    
    print(f"\nFound {len(video_files)} video file(s):")
    for i, video_file in enumerate(video_files, 1):
        print(f"  {i}. {video_file.name}")
    
    print("\nLoading video clips...")
    clips = []
    
    try:
        for video_file in video_files:
            print(f"  Loading: {video_file.name}")
            clip = VideoFileClip(str(video_file))
            clips.append(clip)
        
        print("\nConcatenating videos...")
        final_clip = concatenate_videoclips(clips, method="compose")
        
        print(f"Writing output to: {output_file}")
        # Create output directory if it doesn't exist
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the final video
        final_clip.write_videofile(
            str(output_file),
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            fps=30
        )
        
        print("\n✓ Video concatenation completed successfully!")
        print(f"✓ Output saved to: {output_file}")
        
    finally:
        # Clean up - close all clips
        for clip in clips:
            clip.close()
        if 'final_clip' in locals():
            final_clip.close()


def main():
    """Main entry point for the video concatenator."""
    # Define paths
    input_dir = "input_videos"
    output_file = "output_video/concatenated_output.mp4"
    
    try:
        concatenate_videos(input_dir, output_file)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise


if __name__ == "__main__":
    main()

# Movie Concatenator

A Python tool to concatenate multiple video files into a single output video. The videos are automatically sorted by the numbers in their filenames (e.g., Video1, Video2, Video3) before concatenation.

## Features

- Automatically sorts videos by numeric order in filenames
- Supports multiple video formats (.MOV, .MP4, .AVI, .MKV)
- Handles mixed case filenames (e.g., Video1.MOV, video2.mov)
- Creates output directory automatically if it doesn't exist
- Provides detailed progress information during processing

## Requirements

- Python 3.x
- moviepy library

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your video files in the `input_videos/` directory
2. Run the concatenator:
```bash
python src/video_concatenator.py
```

3. The concatenated video will be saved in `output_video/concatenated_output.mp4`

## How it works

The script:
1. Scans the `input_videos/` directory for video files
2. Extracts numbers from filenames and sorts them numerically
3. Loads each video clip in order
4. Concatenates all clips into a single video
5. Outputs the final video as an MP4 file with H.264 codec

## Example

If you have files:
- Video1.MOV
- Video2.MOV
- Video3.MOV
- Video4.MOV

They will be concatenated in this exact order, regardless of file creation time or alphabetical order.

## Notes

- The tool uses the `compose` method for concatenation, which handles videos with different resolutions
- Output is encoded with libx264 codec and AAC audio
- Default output FPS is 30

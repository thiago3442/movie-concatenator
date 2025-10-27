# Movie Concatenator

A Python tool to concatenate multiple video files into a single output video and add synchronized subtitles based on audio analysis.

## Features

### Video Concatenation
- Automatically sorts videos by numeric order in filenames (e.g., Video1, Video2, Video3)
- Supports multiple video formats (.MOV, .MP4, .AVI, .MKV)
- Handles mixed case filenames (e.g., Video1.MOV, video2.mov)
- Creates output directory automatically if it doesn't exist
- Provides detailed progress information during processing

### Subtitle Generation
- Analyzes audio to detect speech segments (no AI/LLMs required)
- Synchronizes transcript sentences with detected speech
- Creates SRT subtitle files for external use
- Burns subtitles directly into videos
- Works on CPU-only systems without GPU acceleration

## Requirements

- Python 3.x
- moviepy library
- pydub library
- FFmpeg (system dependency)

## Installation

1. Install FFmpeg (required for audio processing):
   - **Windows**: Download from https://ffmpeg.org/download.html and add to PATH
   - **Linux**: `sudo apt-get install ffmpeg`
   - **macOS**: `brew install ffmpeg`

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Video Concatenation

Place your video files in the `input_videos/` directory and run:

```bash
python src/video_concatenator.py
```

The concatenated video will be saved in `output_video/concatenated_output.mp4`

### 2. Adding Subtitles

To add synchronized subtitles to individual videos:

1. Place your videos in the `output_video/` directory
2. Create matching transcript files in the `transcripts/` directory
   - Each transcript file should have the same name as the video (e.g., `video_name.txt` for `video_name.mp4`)
   - Format: Each sentence in double quotes on separate lines:
     ```
     "First sentence here."
     "Second sentence here."
     "Third sentence here."
     ```

3. Run the subtitle generator:
```bash
python src/subtitle_generator.py
```

4. Output will be saved in `output_video_with_subtitles/` with:
   - Videos with burned-in subtitles (`*_subtitled.mp4`)
   - SRT subtitle files in the `subtitles/` subdirectory

## How Video Concatenation Works

The script:
1. Scans the `input_videos/` directory for video files
2. Extracts numbers from filenames and sorts them numerically
3. Loads each video clip in order
4. Concatenates all clips into a single video
5. Outputs the final video as an MP4 file with H.264 codec

## How Subtitle Synchronization Works

The subtitle generator:
1. Extracts audio from the video
2. Analyzes audio amplitude to detect speech segments
3. Identifies silent pauses that separate sentences
4. Aligns transcript sentences with detected speech segments
5. Creates SRT files with precise timestamps
6. Burns subtitles into the video with professional styling

**Note**: This method uses audio analysis, not speech recognition, so it doesn't require AI models or GPU. It works by detecting when speech occurs and aligning your provided transcript accordingly.

## Project Structure

```
movie-concatenator/
├── input_videos/          # Place videos to concatenate here
├── output_video/          # Concatenated and individual videos
├── transcripts/           # Transcript files for subtitles
├── output_video_with_subtitles/  # Videos with subtitles
│   └── subtitles/        # SRT subtitle files
├── src/
│   ├── video_concatenator.py   # Main concatenation script
│   └── subtitle_generator.py   # Subtitle sync script
├── requirements.txt
└── README.md
```

## Example Workflow

1. **Concatenate videos**:
```bash
python src/video_concatenator.py
```

2. **Add subtitles to individual videos**:
```bash
python src/subtitle_generator.py
```

## Configuration

### Subtitle Generator Settings

You can adjust these parameters in `src/subtitle_generator.py`:

- `min_silence_len`: Minimum silence duration to separate segments (default: 400ms)
- `silence_thresh`: Silence threshold in dBFS (default: -45)
- `max_gap_ms`: Maximum gap to merge close segments (default: 400ms)

Lower `silence_thresh` values (e.g., -50) detect quieter speech segments.
Higher values (e.g., -35) require louder audio to be considered speech.

## Troubleshooting

### FFmpeg Not Found
If you get an error about FFmpeg:
- Make sure FFmpeg is installed and in your system PATH
- Test by running `ffmpeg -version` in terminal

### Subtitle Timing Issues
If subtitles are not well-synchronized:
- Adjust `silence_thresh` in the script (try -40 to -50)
- Adjust `min_silence_len` (try 300-600ms)
- Check that your transcript exactly matches the spoken words

### Video Quality
Output videos use H.264 codec with AAC audio at the same FPS as input videos.

## Notes

- The concatenation tool uses the `compose` method, which handles videos with different resolutions
- Subtitles are styled with white text, black outline, and centered at the bottom
- SRT files are created separately and can be used with video players
- Temporary audio files are automatically cleaned up after processing

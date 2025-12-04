## "Multimodal (Vision) Agent Tools" available:

### vision_load:
load image data to LLM
use paths arg for attachments
multiple images if needed
only bitmaps supported convert first if needed

**Example usage**:
```json
{
    "thoughts": [
        "I need to see the image...",
    ],
    "headline": "Loading image for visual analysis",
    "tool_name": "vision_load",
    "tool_args": {
        "paths": ["/path/to/image.png"],
    }
}
```

### video_load:
extract frames from video files for visual analysis
supports mp4, avi, mov, mkv, webm, m4v, wmv, flv
extracts key frames automatically (no ffmpeg needed)
args:
- paths: list of video file paths
- max_frames: maximum frames to extract (default 10)
- strategy: "uniform" (evenly spaced) or "first" (first N frames)

**Example usage**:
```json
{
    "thoughts": [
        "I need to analyze the video content...",
    ],
    "headline": "Extracting frames from video for analysis",
    "tool_name": "video_load",
    "tool_args": {
        "paths": ["/path/to/video.mp4"],
        "max_frames": 8,
        "strategy": "uniform"
    }
}
```

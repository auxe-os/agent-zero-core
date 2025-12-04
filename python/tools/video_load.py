import base64
import os
from python.helpers.print_style import PrintStyle
from python.helpers.tool import Tool, Response
from python.helpers import files, images
from python.helpers import history

# Frame extraction settings
MAX_FRAMES = 6  # Reduced to stay within model limits
MAX_PIXELS = 768_000
QUALITY = 75
TOKENS_PER_FRAME = 1500

VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v", ".wmv", ".flv"}


class VideoLoad(Tool):
    async def execute(
        self,
        paths: list[str] = [],
        max_frames: int = MAX_FRAMES,
        strategy: str = "uniform",
        **kwargs,
    ) -> Response:
        """
        Extract frames from video files for vision analysis.

        Args:
            paths: List of video file paths
            max_frames: Maximum number of frames to extract (default 10)
            strategy: Frame selection strategy
                - "uniform": Evenly spaced frames across video
                - "first": First N frames (good for short clips)
        """
        self.frames_data: list[dict] = []
        self.errors: list[str] = []
        self.video_info: list[dict] = []

        for path in paths:
            # Convert /a0/ paths to local paths in development mode
            local_path = files.fix_dev_path(path)
            
            ext = "." + path.split(".")[-1].lower() if "." in path else ""
            if ext not in VIDEO_EXTENSIONS:
                self.errors.append(f"Unsupported format: {path}")
                continue

            if not os.path.exists(local_path):
                self.errors.append(f"File not found: {path}")
                continue

            try:
                frames, info = await self._extract_frames(path, local_path, max_frames, strategy)
                self.frames_data.extend(frames)
                self.video_info.append(info)
            except Exception as e:
                self.errors.append(f"Error processing {path}: {e}")
                PrintStyle().error(f"Error processing video {path}: {e}")

        return Response(message="dummy", break_loop=False)

    async def _extract_frames(
        self, path: str, local_path: str, max_frames: int, strategy: str
    ) -> tuple[list[dict], dict]:
        """Extract frames from a video file.
        
        Args:
            path: Original path (for display/metadata)
            local_path: Actual filesystem path to read from
            max_frames: Maximum frames to extract
            strategy: Frame selection strategy
        """
        import cv2
        from PIL import Image
        import io

        # Open video directly from local path (no temp file needed)
        cap = cv2.VideoCapture(local_path)
        try:
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {path}")

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = total_frames / fps if fps > 0 else 0

            video_info = {
                "path": path,
                "duration": round(duration, 2),
                "fps": round(fps, 2),
                "resolution": f"{width}x{height}",
                "total_frames": total_frames,
            }

            # Determine which frames to extract
            frame_indices = self._get_frame_indices(total_frames, max_frames, strategy)

            frames = []
            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if not ret:
                    continue

                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Convert to PIL Image and compress
                pil_img = Image.fromarray(frame_rgb)
                img_bytes = io.BytesIO()
                pil_img.save(img_bytes, format="JPEG", quality=95)
                compressed = images.compress_image(
                    img_bytes.getvalue(), max_pixels=MAX_PIXELS, quality=QUALITY
                )

                timestamp = idx / fps if fps > 0 else 0
                frames.append(
                    {
                        "path": path,
                        "frame_index": idx,
                        "timestamp": round(timestamp, 2),
                        "image_b64": base64.b64encode(compressed).decode("utf-8"),
                    }
                )

            return frames, video_info

        finally:
            cap.release()

    def _get_frame_indices(
        self, total_frames: int, max_frames: int, strategy: str
    ) -> list[int]:
        """Calculate which frame indices to extract."""
        if total_frames <= 0:
            return []

        if total_frames <= max_frames:
            return list(range(total_frames))

        if strategy == "first":
            return list(range(min(max_frames, total_frames)))

        # Default: uniform spacing including first and last frame
        if max_frames == 1:
            return [0]
        step = (total_frames - 1) / (max_frames - 1)
        return [int(i * step) for i in range(max_frames)]

    async def after_execution(self, response: Response, **kwargs):
        """Add extracted frames to agent's context."""
        content = []

        if self.frames_data:
            # Add frames with timestamps (simplified format like vision_load)
            for frame in self.frames_data:
                content.append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{frame['image_b64']}"
                        },
                    }
                )

            msg = history.RawMessage(
                raw_content=content,
                preview=f"<Video: {len(self.frames_data)} frames extracted>",
            )
            self.agent.hist_add_message(
                False, content=msg, tokens=TOKENS_PER_FRAME * len(self.frames_data)
            )

        # Build result message
        if self.errors:
            error_msg = "\n".join(self.errors)
            if self.frames_data:
                message = (
                    f"{len(self.frames_data)} frames extracted. Errors:\n{error_msg}"
                )
            else:
                message = f"No frames extracted. Errors:\n{error_msg}"
        else:
            info_str = ", ".join(
                f"{i['path']} ({i['duration']}s)" for i in self.video_info
            )
            message = f"{len(self.frames_data)} frames extracted from: {info_str}"

        PrintStyle(
            font_color="#1B4F72", background_color="white", padding=True, bold=True
        ).print(f"{self.agent.agent_name}: Response from tool '{self.name}'")
        PrintStyle(font_color="#85C1E9").print(message)
        self.log.update(result=message)

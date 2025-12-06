from __future__ import annotations

import json
import time
import os
from typing import Any

import requests

# Seedream4 helpers centralise API config (endpoint, model, env flags).
from python.helpers import dotenv, files, seedream4
from python.helpers.tool import Tool, Response


class Seedream4ImageTool(Tool):
    """Tool for calling BytePlus Seedream 4.x image generation/edit API.

    Supports four modes:
      - generate:         text -> single image
      - generate_series:  text -> multi-image series
      - edit:             text + image_url -> edited image
      - expand:           text + image_url -> multi-image expansion
    """

    async def execute(
        self,
        prompt: str | None = None,
        mode: str | None = None,
        image_url: str | None = None,
        image_path: str | None = None,
        max_images: int | None = None,
        size: str | None = None,
        watermark: bool | None = None,
        stream: bool | None = None,
        **kwargs: Any,
    ) -> Response:
        # Global on/off switch for Seedream integration.
        if not seedream4.is_enabled():
            return Response(message="Seedream4 image tool is disabled (set SEEDREAM4_ENABLED=true to enable).", break_loop=False)

        # API key for Seedream 4.0 backend.
        api_key = seedream4.get_api_key()
        if not api_key:
            return Response(message="Seedream4 API key missing (set SEEDREAM4_API_KEY in env).", break_loop=False)

        if not prompt or not isinstance(prompt, str):
            return Response(message="prompt argument missing", break_loop=False)

        mode = (mode or "generate").lower()
        if mode not in ("generate", "generate_series", "edit", "expand"):
            return Response(message="invalid mode, expected one of: generate, generate_series, edit, expand", break_loop=False)

        # Base endpoint for Seedream 4.x image generation.
        endpoint = seedream4.SEEDREAM4_ENDPOINT

        payload: dict[str, Any] = {
            "model": seedream4.SEEDREAM4_MODEL,
            "prompt": prompt,
            "response_format": "url",
            "size": size or "2K",
            "watermark": True if watermark is None else bool(watermark),
            "stream": False if stream is None else bool(stream),
        }

        if mode in ("edit", "expand"):
            if not image_url and image_path:
                base = dotenv.get_dotenv_value("SEEDREAM4_FILE_BASE_URL", "").rstrip("/")
                if base:
                    rel = image_path.lstrip("/")
                    image_url = f"{base}/{rel}"

            if not image_url:
                msg = "Seedream4 edit/expand requires a publicly accessible image_url. "
                if image_path:
                    msg += (
                        f"Received local image_path='{image_path}', which Seedream cannot fetch from BytePlus servers. "
                        "Either provide a public image_url directly, or configure SEEDREAM4_FILE_BASE_URL "
                        "to map local paths to a public host that serves your images."
                    )
                else:
                    msg += "Provide image_url pointing to an image Seedream can download."
                return Response(message=msg, break_loop=False)

            payload["image"] = image_url

        if mode == "generate":
            payload["sequential_image_generation"] = "disabled"
        elif mode == "generate_series":
            payload["sequential_image_generation"] = "auto"
            payload["sequential_image_generation_options"] = {
                "max_images": int(max_images or 4),
            }
        elif mode == "edit":
            payload["sequential_image_generation"] = "disabled"
        elif mode == "expand":
            payload["sequential_image_generation"] = "auto"
            payload["sequential_image_generation_options"] = {
                "max_images": int(max_images or 5),
            }

        try:
            resp = requests.post(
                endpoint,
                headers=seedream4.build_headers(api_key),
                data=json.dumps(payload),
                timeout=120,
            )
        except Exception as e:
            return Response(message=f"Seedream4 HTTP error: {e}", break_loop=False)

        if resp.status_code >= 400:
            return Response(message=f"Seedream4 API error {resp.status_code}: {resp.text}", break_loop=False)

        try:
            data = resp.json()
        except Exception:
            return Response(message=f"Seedream4 returned non-JSON response: {resp.text[:500]}", break_loop=False)

        urls: list[str] = []
        if isinstance(data, dict):
            if isinstance(data.get("data"), list):
                for item in data["data"]:
                    url = item.get("url") if isinstance(item, dict) else None
                    if isinstance(url, str):
                        urls.append(url)
            url = data.get("url")
            if isinstance(url, str):
                urls.append(url)

        urls = list(dict.fromkeys(urls))

        stored: list[dict[str, Any]] = []
        # Save under ./export_zone relative to the base dir so files are
        # visible in the repo as export_zone/seedream4_*.png.
        rel_dir = "export_zone"
        abs_dir = files.get_abs_path(rel_dir)
        os.makedirs(abs_dir, exist_ok=True)
        ts = int(time.time())
        for idx, url in enumerate(urls):
            path: str | None = None
            filename = f"seedream4_{ts}_{idx}.png"
            abs_path = os.path.join(abs_dir, filename)
            try:
                img_resp = requests.get(url, timeout=120)
                if img_resp.status_code < 400:
                    with open(abs_path, "wb") as f:
                        f.write(img_resp.content)
                    rel_path = f"{rel_dir}/{filename}"
                    path = rel_path
            except Exception:
                path = None
            # Prefer exposing the locally saved path to the rest of the system.
            # The remote Seedream URL is time-limited and should be used only
            # internally (it's still available under result["raw"]).
            if path:
                web_path = files.normalize_a0_path(abs_path)
                stored.append({"path": path, "web_path": web_path})
            else:
                stored.append({"remote_url": url})

        result = {
            "mode": mode,
            "prompt": prompt,
            "images": stored,
            "raw": data,
        }

        summary = "Seedream4: no images returned"
        if stored:
            paths = [str(img["path"]) for img in stored if img.get("path")]
            count = len(stored)
            if paths:
                summary = f"Seedream4: {count} image(s) saved to export_zone: " + ", ".join(paths)
            else:
                # Images exist but were not saved locally.
                # Remote URLs are short-lived and only available in raw.
                summary = f"Seedream4: {count} image(s) generated (remote URLs available in raw, not logged here)."

        return Response(message=summary, break_loop=False, additional={"seedream4_result": result})

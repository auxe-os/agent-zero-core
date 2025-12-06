# Tool: seedream4_image (Seedream‑4.5)

This tool calls the **Seedream‑4.5** image API hosted on BytePlus Model Ark (`https://ark.ap-southeast.bytepluses.com/api/v3/images/generations`). It is pre-configured with the `"seedream-4-5-251128"` model but can be overridden via the `SEEDREAM4_MODEL` env var.

## When to use
- When the user asks you to **generate** a new image from a text description.
- When the user asks you to **generate a series** of coherent images from a text prompt.
- When the user asks you to **edit** or **expand** an existing image, and provides a public image URL (or a path that can be mapped to a URL externally).

## Seedream‑4.5 prompt craft (master level)

Structure prompts using the recommendations from the Seedream docs:

1. **Subject lock** – describe the character/object precisely. For edits, explicitly state what must remain unchanged (face, skin tone, pose, proportions).
2. **Wardrobe / props / environment** – list concrete elements using bullet-style phrases or comma-separated descriptors.
3. **Camera + composition** – include framing, lens, angle, depth of field, motion cues.
4. **Lighting + atmosphere** – specify time of day, light quality, shadows, color temperature.
5. **Finish & style** – mention materials, rendering style (photography, cinematic, anime, illustration), any art movements.
6. **Quality tags** – request “4K”, “8K”, “ray traced”, etc. (Seedream accepts `"size": "2K"` or `"size": "4K"`, default is `2K`.)
7. **Negative guardrails** – end with “Avoid: …” to block distortions (extra limbs, face changes, background changes, etc.).

Keep prompts concise but information-dense (2–4 sentences or a short list).
Avoid conflicting instructions; Seedream 4.5 responds best to confident, declarative language.

**Subject reference phrase (highly recommended):**  
> “Strictly preserve the subject’s facial identity and body structure from the reference image, while adapting the outfit and background as described.”

Seedream 4.5’s “Subject Reference” and “Advanced Consistency Preservation” features respond best when you **explicitly lock identity** (face + proportions) and **separately describe what may change** (wardrobe, scene, mood). Include the phrase above (or equivalent wording) whenever likeness matters.

## Arguments
- `prompt` (string, required)
  - Natural language description of the desired image(s).
- `mode` (string, optional)
  - One of:
    - `"generate"` – single image from text (default).
    - `"generate_series"` – multiple coherent images from text.
    - `"edit"` – edit an existing image using a reference image.
    - `"expand"` – create multiple variations from a reference image.
- `image_url` (string, optional)
  - Publicly accessible URL of the reference image. Required for `edit` and `expand` unless `image_path` is provided and can be mapped to a URL.
- `image_path` (string, optional)
  - Local/project-relative path to an image file. Use only if it can be converted to a public URL via external configuration.
- `max_images` (integer, optional)
  - Maximum number of images to generate for `generate_series` or `expand`.
- `size` (string, optional)
  - Target image size: `"2K"` (default) or `"4K"`. Use `"4K"` only when the user requests ultra-high resolution.
- `watermark` (boolean, optional)
  - Whether to include a watermark in generated images. Defaults to `true`.
- `stream` (boolean, optional)
  - Streaming flag for the Seedream API. Defaults to `false`.

## Output
The tool returns a JSON object with:
- `mode` – the mode that was used.
- `prompt` – the original prompt.
- `images` – a list of objects, each containing:
  - `path` – project-relative path where the image was saved (`export_zone/seedream4_…png`).
  - `web_path` – web-safe path (e.g., `/a0/export_zone/seedream4_…png`) **for embedding in chat UIs**.
  - `remote_url` – only present if the image could not be saved locally (short-lived Seedream URL).
- `raw` – raw response payload from the Seedream API for advanced use.

Always embed images with `web_path` so they render reliably in the UI, and mention `path` when referencing files inside the repo.

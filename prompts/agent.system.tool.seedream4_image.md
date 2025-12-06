# Tool: seedream4_image (Seedream‑4.5) - Photorealism Optimized

This tool calls the **Seedream‑4.5** image API hosted on BytePlus Model Ark (`https://ark.ap-southeast.bytepluses.com/api/v3/images/generations`). It is pre-configured with the `"seedream-4-5-251128"` model (optimized for photorealism) and defaults to **4K resolution** for ultra-high definition outputs.

## When to use
- When the user asks for **photorealistic** or **hyper-realistic** images.
- When the user asks to **generate** a new image from a text description.
- When the user asks to **generate a series** of coherent images from a text prompt.
- When the user asks to **edit** or **expand** an existing image, and provides a public image URL (or a path that can be mapped to a URL externally).

## Seedream‑4.5 prompt craft (photorealism master level)

### Core Structure
Structure prompts using this **photorealism-optimized** template:
```
[Subject] + [Action] + [Environment] + [Lighting] + [Style] + [Quality] + [Negative Guardrails]
```

### Key Components
1. **Subject lock** – Describe the character/object with **precise, photorealistic details**. For edits, explicitly state what must remain unchanged (e.g., "preserve facial identity, skin texture, and body proportions").
2. **Wardrobe / props / environment** – Use **photorealistic descriptors** (e.g., "worn leather jacket with scuff marks", "dewy morning grass").
3. **Camera + composition** – Specify **realistic framing** (e.g., "35mm lens, shallow depth of field, rule of thirds").
4. **Lighting + atmosphere** – Use **cinematic lighting terms** (e.g., "golden hour, volumetric fog, rim lighting").
5. **Finish & style** – Always include **photorealism keywords** (e.g., "photorealistic, cinematic, 8K, HDR, depth of field").
6. **Quality tags** – Request **ultra-high definition** (e.g., "4K, 8K, ray-traced, hyper-detailed"). Default is `2K` (use `4K` for maximum detail).
7. **Negative guardrails** – Block **unrealistic artifacts** (e.g., "Avoid: plastic skin, blurry details, cartoonish proportions, low resolution").

### Photorealism-Specific Tips
- **Lighting is critical**: Always specify time of day and light quality (e.g., "soft diffused light, late afternoon").
- **Textures matter**: Describe materials with realistic properties (e.g., "rough concrete, glossy ceramic").
- **Depth of field**: Use terms like "shallow DOF" or "deep focus" to control realism.
- **Color grading**: Specify color tones (e.g., "teal and orange color grading, high contrast").

### Subject Reference (for edits/expansions)
> “Strictly preserve the subject’s **facial identity, skin texture, and body structure** from the reference image, while adapting the outfit and background as described. Use **advanced consistency preservation** to maintain lighting and color tone.”

### Photorealism Examples
#### Example 1: Portrait
```
A weathered fisherman with sun-leathered skin and deep wrinkles, smoking a pipe on a wooden dock at sunset. 35mm lens, shallow depth of field, golden hour lighting with lens flares, cinematic color grading, hyper-detailed skin texture, photorealistic, 8K, HDR. Avoid: plastic skin, blurry details, cartoonish proportions.
```

#### Example 2: Product Photography
```
A luxury wristwatch with a sapphire crystal face and rose gold casing, resting on black marble. High-end product photography, studio lighting with softboxes, shallow depth of field, hyper-detailed metal textures, 8K, HDR. Avoid: reflections on non-reflective surfaces, blurry details, unrealistic shadows.
```

#### Example 3: Landscape
```
A misty mountain valley at dawn, with a crystal-clear alpine lake reflecting the pink sky. Wide-angle lens, deep focus, volumetric fog in the distance, hyper-detailed rock textures, cinematic color grading, 8K, HDR. Avoid: oversaturated colors, cartoonish clouds, unrealistic water reflections.
```

### Default Settings (Automatically Applied)
- **Resolution**: 2K (default, use 4K for maximum detail)
- **Style**: Photorealistic (cinematic lighting, HDR, depth of field)
- **Negative Prompt**: "plastic skin, blurry details, cartoonish proportions, low resolution, unrealistic shadows, oversaturated colors"

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

---
# METADATA
template_version: "1.0"
template_category: "docs"
editable: true
marketplace_eligible: true
id: "format-social-micro"
entity_type: "pack-doc"
created_date: "2026-08-21"
last_updated: "2026-08-21"
---

# Format: Social Micro

A **format** is a pack, not a new file class. It bundles existing catalog
workflows and providers around one output shape — here, short-form vertical
clips for social platforms.

## What's inside

| Workflow | Graph | Output |
|---|---|---|
| `broll-from-location` | location description -> still (comfyui) -> clip (kling) | `entity.location.broll_video` |
| `lyric-to-shots` | optional UVR vocal stem, looped stills (fal) -> clips (kling) | `entity.item.music_video` |
| `score-under-track` | brief -> score (stable-audio) -> ffmpeg amix under video audio | `entity.item.scored_video` |

Providers referenced: `comfyui`, `kling`, `fal`, `uvr`, `stable-audio`, `ffmpeg`.

## Runtime requirements

- **Desktop run required.** `uvr` and `ffmpeg` are `wire: process`, and
  `comfyui` is localhost — the workflows aggregate this as
  `requires.platforms: [desktop]`. Cloud workers must 501 those steps.
- **Keys:** `FAL_KEY` (fal, kling, stable-audio).
- **Binaries on PATH:** `uvr`, `ffmpeg`.

## Swapping backends

The graphs are shareable: point `comfyui` / `fal` / `kling` / `stable-audio`
at your own URLs and keys by dropping edited `*.provider.yaml` files into your
project's `_Providers/`. The workflow files do not change.

---
name: burned-captions
description: Use when adding on-screen captions to a short vertical video: karaoke-style, word-timed, burned into the video rather than a sidecar file.
---


# Burned-in captions

1. Convert audio to WAV; transcribe with word-level timestamps (e.g. faster-whisper `medium.en`).
2. Group words into short phrases of ~2–5 words.
3. Style per `references/caption-style.md`.
4. Place low, but above the platform UI band.
5. Burn in. **Do not export a `.srt`.**
6. Fix misrecognized names by hand. Never silently change what was said; report misspoken words instead.

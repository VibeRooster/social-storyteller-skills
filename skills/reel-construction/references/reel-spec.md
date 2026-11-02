# Reel tech spec
- 1080x1920, 30fps, H.264 (crf 18).
- Loudness −14 LUFS integrated, true peak ≤ −1.5 dBTP (ffmpeg `loudnorm`).
- Trim silences to under ~1.5s.
- Never speed up the voice (screen footage may be sped up).
- No music by default. If used: ~8 LU under voice, sidechain-ducked.
- Captions burned in; never export `.srt` (see `burned-captions`).

# Code — the Audiocast player builders

MIT (see [../LICENSE-MIT.md](../LICENSE-MIT.md)). The scripts
that render the animated player clips: canon medallion,
waveform and playhead driven by the narration audio,
procedural lip-sync from the audio RMS envelope (see
[../production-notes/METHOD.md](../production-notes/METHOD.md),
section 6).

- `build_player_design_v1.py` — the static player design
  of record (EP01).
- `animate_player_v1.py` — EP01 clip builder.
- `animate_player_ep2.py` — EP02 clip builder.
- `animate_player_ep3.py` — EP03 clip builder.
- `animate_player_ep4.py` — EP04 clip builder.

Each episode builder is a fork of the EP01 builder with
that episode's strings (title, subtitle, caption, timings).
They are published as history and as a reusable starting
point, paths and all; adapt the constants at the top.

~C4Chaos / Fluffy (A Centaur Production)

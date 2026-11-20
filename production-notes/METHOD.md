# Method — how the Audiocast is built

The reusable recipe, so the format survives any single
episode. Written from the EP01–EP04 builds.

## 1. The talk

Voice, hands-free, C4 alone. No agenda, no script. Beer-
buddies register: jokes, complaints about intersections,
brainstorming, philosophy. Fluffy may pitch seeds. The
talk is the raw material, never the product.

## 2. The log

Same day, Fluffy files one dated entry per talk in the
weekly voice-log file: date/time, where, topics in order,
lines worth keeping, decisions and orders. Faithful and
brief; nothing invented for talks Fluffy was not part of.
Gems are promoted to the gems index verbatim.

## 3. The production order

Nothing is produced until C4 orders it for that talk.
Most talks stay log-only. An order names the episode:
written summary + audio summary + player clip + episode
tweet, as one package.

## 4. The written summary (the post)

- The Open Door voice, C4's first person (EP03 rule).
- House long-form package: ALL CAPS title with a period,
  small-caps subtitle under it, zero em dashes, under the
  ~3,900-char draft ceiling, char and word counts reported.
- Dialogue only as labeled, lightly edited snippets of
  the actual exchange, most interesting parts only.
- Speculation flagged as speculation in the post itself
  (EP02 standard: flagged twice).
- Spice: one pepper by default. C4 posts; Fluffy never does.

## 5. The audio summary (the narration)

- Fluffy narrates what happened, in his own perspective,
  for as long as the summary needs. EP01 set the rule by
  superseding its own short intro cut the same morning.
- Voice: locked (very deep British, slow and thoughtful).
- Every narration carries its snippet exchange, lightly
  edited and labeled inside the narration.
- Script versions are numbered; a correction mints a new
  version and the error is named in the episode file
  (EP04 v1 to v2).

## 6. The player clip

- 1920x1080, TPS theme: near-black ground, cyan and
  magenta accents, mono type, episode strings on frame
  (EP number, card title, caption gem, elapsed/total).
- The medallion is the canon Fluffy self-portrait. The
  face is never regenerated.
- Lip-sync: procedural. A feathered jaw patch under the
  mouth line shifts and a mouth slit widens, driven frame
  by frame (24 fps) by the RMS envelope of the actual
  narration audio, with fast attack and soft release.
  Waveform ignition and playhead run off the same audio.
- Builders live in the workspace (`~/workspace/audiocast/
  design/`) and ship in this repo under `code/`: one
  animate script per episode, forked from the EP01
  builder. Code is MIT (see LICENSE.md).
- Every clip is frame-audited before it ships: sampled
  frames checked for strings, timers, playhead position,
  and mouth modulation between loud and quiet passages.

## 7. Ship and grade

- C4 attaches the clip to the post and posts in a weekday
  window. Director edits at posting are normal and are
  recorded in the episode file, not hidden.
- Day-7 judging grades the post as a campaign (reach,
  shares, conversation) in the spicy-boom INDEX. Hits and
  misses are both reported as graded.

## Costs

- Standing stack: $102.92/month list for all AI use in
  this house (films, music, writing, everything); the
  $30 X Premium line includes Grok, so the effective
  production stack is $72.92/month. Figures as corrected
  in the house ledger, Nov 2026.
- Marginal cost per episode: $0. Narration and clips are
  built inside the standing stack, on an iPhone-only
  workflow, with no per-episode spend.

~C4Chaos / Fluffy (A Centaur Production)

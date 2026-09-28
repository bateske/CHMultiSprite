# CHMultiSprite

A stress test that measures how many animated characters can walk around the
CHGame screen at once when every frame is streamed from microSD. It uses the
same board, SPI bus and SD transport as [CHSpriteView](../CHSpriteView).

Two characters, **Moog** and **Mushboom**, are seen 3/4 from above. Each has a
3-frame walk cycle for each direction. Every walker follows a random path
around the screen, turning at the edges and every 8 to 48 pixels. It plays
the walk loop for the direction it faces. Walkers are drawn back to front by
where their feet are, so one standing lower on screen covers one behind it.

---

## How to use it

### What you see when it starts

1. The screen says **mounting SD...** for a moment.
2. Then **16 characters** appear and start walking. The mode is **SD-BATCH**.
3. The top of the screen is the **HUD**: two lines of text. The walkers use
   everything below it.
4. The HUD shows its first numbers after **1 second**.

If something is wrong with the card, you get an error screen instead. See
[Error screens](#error-screens).

### The buttons

| Button | What it does |
|---|---|
| **A** | Adds **1** walker. |
| **B** | Removes **1** walker. |
| **UP** | Adds **8** walkers. |
| **DOWN** | Removes **8** walkers. |
| **SELECT** | Switches to the **next draw mode**. The order is SD-EACH → SD-BATCH → SD-SHEET → FLASH → back to SD-EACH. |
| **START** | Starts the **automatic test** (the sweep). Press START again to stop it. |
| LEFT, RIGHT | Do nothing. |

- **Hold A, B, UP or DOWN** to keep adding or removing, about 5 times a
  second.
- The walker count is always between **0 and 64**. Pressing past either end
  does nothing.
- A new walker appears at a random spot. Removing one takes away the one
  added last.
- Walkers alternate: the 1st is Moog, the 2nd is Mushboom, the 3rd is Moog,
  and so on.

### The HUD (the two lines at the top)

It looks like this:

```
SD-BATCH        n16 L2 R3
143fps d5.2 l3.1
```

**Line 1, left: the draw mode.** Which of the four ways of drawing is running
(see [The four draw modes](#the-four-draw-modes)).

**Line 1, right: counts.**

| Shows | Means | Shown in |
|---|---|---|
| `n16` | **16 walkers** on screen right now. | every mode |
| `L2` | The walkers were split into **2 depth layers** each frame, on average. More walkers stacked on top of each other means more layers. | SD-BATCH and SD-SHEET only (always `L1` in SD-SHEET) |
| `R3` | **3 read commands** were sent to the SD card each frame, on average. Fewer is faster: every command costs about 0.6 ms of waiting for the card. | every mode except FLASH (FLASH does not read the card) |

**Line 2: speed.** Every number is an average over the last second.

| Shows | Means |
|---|---|
| `143fps` | **Frames per second.** How many times the whole screen was redrawn in the last second. Higher is better. 60 and 30 are the usual game targets. |
| `d5.2` | **Draw time: 5.2 ms per frame.** The time to erase the walkers and draw all of them again, including reading them from the SD card. This is the number the modes change. |
| `l3.1` | **LCD time: 3.1 ms per frame.** The time spent sending the picture to the screen. It grows with how much of the screen changed, not with the mode. |
| `E3` | **3 SD read errors** since power-on. Only appears if there were errors. It should never appear. |

**When the HUD updates:**

- It updates **once a second**. It is not live.
- After you press a button, the numbers are for the old setting until the
  next update, up to 1 second later.

### How the walkers behave

- **They walk at a fixed speed: 25 pixels a second.** The speed does not
  change with the frame rate. At a low fps the motion gets choppier, but no
  slower. Below about 3 fps they do slow down.
- **They walk in straight lines.** Each one walks 8 to 48 pixels, then picks
  a new random direction: up, down, left or right. Sometimes the new
  direction is the same as the old one.
- **They turn at the edges.** If the next step would go off screen or into
  the HUD, the walker picks a new direction instead.
- **They face where they walk.** Each direction has its own 3-frame walk
  loop. The loop moves on one frame every 4 pixels walked, so feet do not
  slide.
- **They walk through each other.** There is no collision.
- **The one lower on the screen is in front.** Walkers are drawn from the top
  of the screen down, using the bottom of each sprite (the feet). The only
  exception is SD-SHEET, which does not keep this order, so overlaps can look
  wrong there. That is on purpose: SD-SHEET shows the speed you would get if
  order did not matter.
- **Left/right moves look like 2-pixel steps.** Sprites are drawn at even x
  positions because that draws twice as fast.

### The automatic test (START)

The sweep answers "**how many walkers can each mode keep at 60 fps and at 30
fps?**" on its own. You don't need to press anything while it runs.

1. Press **START**.
2. It picks the first mode, **SD-EACH**, and puts **2 walkers** on screen.
3. It waits 0.25 s for things to settle, then measures for **1 second**.
4. It adds **2 more walkers** and measures again: 4, 6, 8, and so on.
5. It moves on to the next mode when the frame rate drops **below 20 fps**,
   or when it reaches **64 walkers**.
6. It does that for all 4 modes in order: SD-EACH, SD-BATCH, SD-SHEET, FLASH.
7. At the end it shows a **results screen**:

```
MOST WALKERS AT
mode      @60  @30
SD-EACH   ...  ...
SD-BATCH  ...  ...
SD-SHEET  ...  ...
FLASH     ...  ...
(64 = the cap)
any button: continue
```

   - **@60** is the most walkers that mode held at 60 fps or more.
   - **@30** is the most walkers it held at 30 fps or more.
   - **64** means it never slowed down enough: the real limit is higher than
     the test goes.
   - **0** means that mode never reached that frame rate, even with 2 walkers.
8. Press **any button**. It goes back to normal: 16 walkers, SD-BATCH.

Things to know while it runs:

- The HUD updates after each step, so you can watch the count climb.
- **All buttons except START are ignored.**
- **Press START to stop early.** It stays on whatever mode and walker count
  it had reached, and you're back in control.
- Every step uses the **same random start**, so each mode is tested on
  exactly the same crowd.
- A full run takes about **1 to 3 minutes**.

### Error screens

If the card can't be used, one of these errors appears. Fix the problem, then
press **START** to try again.

| Screen says | What is wrong | Fix |
|---|---|---|
| `SD mount failed` | No card, or the card can't be read. | Check the card is in and is FAT16 or FAT32. |
| `No /WALK.BIN` | The card has no `WALK.BIN` in its root folder. | Copy `sample/WALK.BIN` to the top level of the card, not into a folder. |
| `WALK.BIN fragmented` | The file is stored in pieces on the card, which the fast reader can't use. | Copy it onto a freshly formatted card. |
| `WALK.BIN mismatch` | The card file and the sketch come from different builds of the assets. | Run `tools/build_walkers.py`, rebuild the sketch, and copy the new `WALK.BIN`. |

### Serial output (optional)

With the USB cable plugged in and a serial monitor open at any baud rate:

- **At power-on:** the card type, SPI speed, and where `WALK.BIN` was found.
- **Once a second:** the same numbers as the HUD, in full, for example:
  `SD-BATCH  walkers 16  fps 143  draw 5200us  lcd 3100us  layers 2.0  reads 3.1  blocks 30  err 0`
- **During the sweep:** one CSV line per step,
  `mode,walkers,fps,draw_us,lcd_us,layers,reads,blocks,err`, then the results
  table. Paste it into a spreadsheet to graph it.

---

## What goes on the SD card

Copy `sample/WALK.BIN` to the **root** of the card:

```
/WALK.BIN      12,288 bytes: 24 frames, one per 512-byte block
```

It holds Moog frames 0-11 in blocks 0-11 and Mushboom frames 0-11 in blocks
12-23. Each frame is 23×27 or 23×26 pixels in Simon's sprite format, padded to
a whole block. All 24 frames are in one file on purpose, so consecutive frames
sit in consecutive card blocks and one read command can fetch many of them.

The card needs to be FAT16 or FAT32. A 12 KB file always fits in one cluster,
so it is always contiguous.

## Rebuilding the assets

```
python tools/build_walkers.py
```

The tool reads `../SpriteSource/` (`MOOG.ZIP`, `MUSHBOOM.ZIP`, `Moog.h`,
`Mushboom.h`) and writes three files:

- `sample/WALK.BIN`: the card file.
- `src/WalkerData.h`: the shared palette, and the same frames in flash for
  the FLASH mode.
- `sample/preview.png`: original frames above the re-quantised ones, to check
  the colours.

**Why re-quantise?** Each character was made with its own 16-colour palette,
and only two colours are common to both. The 4 bpp framebuffer has one
palette. The tool merges the 26 source colours into 15 shared ones, using
weighted Ward merging in CIELAB (mean error about 4.5 ΔE). Palette index 0 is
the grass background. A sprite's index 0 is also its transparent colour, so a
cleared framebuffer is already background.

The original files are named `MUSHBOOM_00.BIN`, which is too long for the SD
library (8.3 names only). The sheet avoids the problem.

## Build

Use **Tools ▸ Optimize ▸ Faster (-O2)**, as for CHSpriteView.

```
arduino-cli compile -b CHGame:ch32v:CHGame:opt=o2std,rtlib=nano .
arduino-cli upload  -b CHGame:ch32v:CHGame -p COMx .
```

| | Flash | Static RAM |
|---|---:|---:|
| `-O2`, 64 walkers max | 43,664 B (85%) | 16,740 B (81%) |

About 7.5 KB of the flash is the frame copy used by the FLASH mode.

`python bench.py sweep 300 -DSWEEP_ON_BOOT=1` builds the sketch, uploads it,
runs the full sweep and prints the CSV and summary. Edit the port with
`--port`.

## The four draw modes

The cost of reading one small sprite from the card is almost entirely
waiting for the card:

```
one read command + card access latency    ~0.6 ms   <- per command
one 512-byte block by DMA at 24 MHz      ~0.17 ms   <- per block
```

The modes differ in how many commands they spend per frame.

| Mode | How | Commands / frame | Overlap order |
|---|---|---|---|
| **SD-EACH** | `spriteDraw()` for each walker: the CHSpriteView API used naively | one per walker | correct |
| **SD-BATCH** | `SpriteBatch` with depth layers | one per layer (and per distant block group) | correct |
| **SD-SHEET** | `SpriteBatch`, `SPRITE_BATCH_IGNORE_DEPTH` | usually 1–2 | **wrong** where walkers overlap |
| **FLASH** | `gfx_blit()` from flash | none | correct |

### How SpriteBatch works (`src/SpriteBatch.h`)

1. You queue sprites back to front with `spriteBatchAdd()`.
2. **Depth layers.** Each sprite's layer is one more than the deepest earlier
   sprite it overlaps. Sprites that share a layer never overlap, so within a
   layer the drawing order doesn't matter.
3. **Read plan.** Inside each layer, the needed blocks are sorted and merged
   into runs. A run reads through gaps of up to 3 unneeded blocks, because
   that is cheaper than issuing a new command.
4. **Read and draw.** Each run is one `readBlocksPipelined()` (CMD18). As each
   block arrives, every sprite of that layer that uses it is blitted straight
   out of the DMA buffer, while the next block is still on the wire.

Walkers that don't touch each other share one read, however many there are.
A stack of walkers that all overlap costs one read each, which is no worse
than SD-EACH.

### Using it in a game

- **Pack small sprites into a sheet** with `spriteLoadSheet()`, one frame per
  block. Separate files land in separate clusters, often 64 blocks apart, and
  can never share a read.
- **Draw many small SD sprites with `SpriteBatch`, back to front.** Keep a
  single large sprite (a background, a boss) on `spriteDraw()`. Batch
  sprites must fit in one block: 2 + ⌈w/2⌉·h ≤ 512 bytes, which is up to
  about 32×30.
- **Use `SPRITE_BATCH_IGNORE_DEPTH`** for anything whose overlap order
  doesn't matter: particles, bullets, pickups, or sprites that never overlap.
- **Draw at even x.** `gfx_blit`'s transparent fast path handles 2 pixels per
  byte only at even x. The walkers are snapped to even x for that reason.
- **Keep everything in flash if you can.** The FLASH mode shows the cost
  with no SD at all.

## Results (measured on the device)

Same board and card (SDHC) as CHSpriteView, 12 bpp, uncapped, SPI at 24 MHz.

_Filled in from `bench.py sweep`; see below._

## Files

| File | What |
|---|---|
| `CHMultiSprite.ino` | walkers, the four modes, HUD, the sweep |
| `src/SpriteBatch.{h,cpp}` | the batched, depth-layered SD sprite drawer (new) |
| `src/CHSpriteView.{h,cpp}` | from CHSpriteView, with `spriteLoadSheet()` and `spriteDirtyAddRect()` added |
| `src/SD/**`, `src/CHGame.*` | from CHSpriteView, unchanged |
| `src/WalkerData.h` | generated: palette and flash frames |
| `tools/build_walkers.py` | generates `WALK.BIN`, `WalkerData.h`, `preview.png` |
| `bench.py` | build, upload and capture the serial report |

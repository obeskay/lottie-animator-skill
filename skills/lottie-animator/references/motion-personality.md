# Motion Personality & Brand Archetypes in Lottie JSON

This reference defines the four primary motion personality archetypes and outlines how to implement their timing, curves, and characteristics inside Lottie JSON animations. Enforce exactly **one** archetype per animation composition to maintain brand cohesion.

---

## The Four Motion Archetypes

### 1. Playful

- **Feel**: Whimsical, warm, bouncy, friendly, high-character.
- **Duration**: `150-300ms` (9 to 18 frames at 60fps).
- **Overshoot / Bounce**: High (`10-25%`).
- **Paths**: Fluid, organic arcs and bezier trajectories.
- **Squash & Stretch**: Enabled (Volume-preserving X/Y scaling on impacts).
- **Signature Curve**: Snappy ease-out with dramatic rebound.
  - **Out/In Tangents**: `o: {"x": [0.34], "y": [1.56]}, i: {"x": [0.64], "y": [1.0]}`

#### Playful Settle Scale Keyframes
```json
"s": {
  "a": 1,
  "k": [
    { "t": 0, "s": [0, 0], "o": { "x": [0.34], "y": [1.56] }, "i": { "x": [0.64], "y": [1] } },
    { "t": 12, "s": [115, 87] }, // Overshoot & Volume Squash
    { "t": 20, "s": [93, 107.5] }, // Rebound Settle
    { "t": 28, "s": [100, 100] }
  ]
}
```

---

### 2. Premium / Luxury

- **Feel**: Sophisticated, minimal, elegant, high-end, smooth.
- **Duration**: `350-650ms` (21 to 39 frames at 60fps).
- **Overshoot / Bounce**: Strictly `0%`.
- **Paths**: Smooth straight lines, soft curves, subtle parallel shifts.
- **Squash & Stretch**: Never.
- **Signature Curve**: Elegant, slow ease-in-out with long, delicate settle.
  - **Out/In Tangents**: `o: {"x": [0.4], "y": [0.0]}, i: {"x": [0.2], "y": [1.0]}`

#### Premium Scale & Fade Entrance
```json
"ks": {
  "s": {
    "a": 1,
    "k": [
      { "t": 0, "s": [96, 96], "o": { "x": [0.4], "y": [0] }, "i": { "x": [0.2], "y": [1] } },
      { "t": 30, "s": [100, 100] }
    ]
  },
  "o": {
    "a": 1,
    "k": [
      { "t": 0, "s": [0], "o": { "x": [0.4], "y": [0] }, "i": { "x": [0.2], "y": [1] } },
      { "t": 20, "s": [100] }
    ]
  }
}
```

---

### 3. Corporate / Professional

- **Feel**: Highly efficient, organized, safe, precise, dashboard-friendly.
- **Duration**: `200-400ms` (12 to 24 frames at 60fps).
- **Overshoot / Bounce**: Minimal (`0-3%`).
- **Paths**: Clean straight lines, uniform spatial offsets.
- **Squash & Stretch**: Disabled.
- **Signature Curve**: Rapid ease-out for immediate functional responsiveness.
  - **Out/In Tangents**: `o: {"x": [0.2], "y": [0.0]}, i: {"x": [0.0], "y": [1.0]}`

#### Corporate Quick Position Entrance
```json
"p": {
  "a": 1,
  "k": [
    { "t": 0, "s": [256, 300, 0], "o": { "x": [0.2], "y": [0] }, "i": { "x": [0], "y": [1] } },
    { "t": 15, "s": [256, 256, 0] }
  ]
}
```

---

### 4. Energetic

- **Feel**: Dynamic, punchy, exciting, immediate, bold.
- **Duration**: `100-250ms` (6 to 15 frames at 60fps).
- **Overshoot / Bounce**: High snap back (`15-30%`).
- **Paths**: Direct straight routes, sharp shifts.
- **Squash & Stretch**: Permitted for impact emphasis.
- **Signature Curve**: Explosive exponential ease-out.
  - **Out/In Tangents**: `o: {"x": [0.15], "y": [1.0]}, i: {"x": [0.15], "y": [1.0]}`

#### Energetic Snap Position & Scale
```json
"ks": {
  "p": {
    "a": 1,
    "k": [
      { "t": 0, "s": [256, 400], "o": { "x": [0.15], "y": [1] }, "i": { "x": [0.15], "y": [1] } },
      { "t": 10, "s": [256, 256] }
    ]
  },
  "s": {
    "a": 1,
    "k": [
      { "t": 0, "s": [50, 150], "o": { "x": [0.15], "y": [1] }, "i": { "x": [0.15], "y": [1] } },
      { "t": 10, "s": [100, 100] }
    ]
  }
}
```

---

## Establishing Brand Motion Identity

Every brand composition requires setting three constants to guide the animation pipeline:

### 1. Signature Easing Curve
Select one curve that governs 80% of all transitions. This creates visual muscle memory for the user.
- **Playful Signature**: Spring / Elastic Out
- **Premium Signature**: Smooth Custom Cubic Bezier `(0.4, 0, 0.2, 1)`
- **Corporate Signature**: Snappy Deceleration `(0.2, 0, 0, 1)`

### 2. Duration Palette (The Triad)
Define three duration constants that all elements must use. Do not introduce arbitrary intermediate timings.
- **Quick**: Micro-feedback, toggles, button presses (`80-150ms`).
- **Standard**: Card entrances, icon transitions, dialog slide-ins (`200-350ms`).
- **Slow**: Page context shifts, full illustration loops, reveals (`400-800ms`).

### 3. Unified Entrance Pattern
Standardize how objects appear. A cohesive interface uses the same spatial path direction for entrances.
- **Luxury Brand Standard**: Fade + soft upward lift (`y+15px -> y`).
- **Playful Brand Standard**: Scale-up pop from center anchor point with spring overshoot (`0% -> 115% -> 100%`).
- **Corporate Brand Standard**: Clean slide in from the right edge with absolute linear margins.

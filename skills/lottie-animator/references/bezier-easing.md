# Bezier Curves, Easing & Timing Physics in Lottie

This reference provides a mathematical guide to implementing bezier easing curves, time scales, and distance physics within Lottie JSON keyframe variables.

---

## Easing Fundamentals in Lottie

In Lottie JSON, easing controls the speed of value interpolation over time between two keyframes.
- **X coordinates (`x`)**: Map to Time (0.0 to 1.0).
- **Y coordinates (`y`)**: Map to Interpolated Value (0.0 to 1.0).

### Keyframe Object Anatomy
```json
{
  "t": 0,           // Start frame number
  "s": [0],         // Start value
  "o": {            // OUT: departure tangent from current keyframe
    "x": [0.33],
    "y": [0.0]
  },
  "i": {            // IN: arrival tangent to next keyframe
    "x": [0.67],
    "y": [1.0]
  }
}
```

---

## Archetype-Mapped Easing Curves

Align easing curves with the selected brand archetype. Do not mix curves from different archetypes in a single composition.

| Archetype | Curve Name | Cubic Bezier Points | Lottie OUT Tangents (`o`) | Lottie IN Tangents (`i`) | Rationale |
|---|---|---|---|---|---|
| **Playful** | Back Out | `(0.175, 0.885, 0.32, 1.275)` | `{"x": [0.175], "y": [0.885]}` | `{"x": [0.32], "y": [1.275]}` | Reaches destination, overshoots by 27.5%, and settles back |
| **Premium** | Luxurious Ease | `(0.4, 0, 0.2, 1)` | `{"x": [0.4], "y": [0.0]}` | `{"x": [0.2], "y": [1.0]}` | Decelerates extremely smoothly with a long, slow settle phase |
| **Corporate** | Precise Fast | `(0.2, 0, 0, 1)` | `{"x": [0.2], "y": [0.0]}` | `{"x": [0.0], "y": [1.0]}` | Immediate snap response with almost instant deceleration |
| **Energetic** | Expo Out | `(0.16, 1, 0.3, 1)` | `{"x": [0.16], "y": [1.0]}` | `{"x": [0.3], "y": [1.0]}` | Explosive initial acceleration with quick stabilization |

---

## Timing and the 1/3 Rule of Spatial Distance

Motion duration must scale proportionally with the distance an element travels. A slide of 400px feels incredibly violent and jarring if compressed into the same duration as a subtle 50px hover shift.

### Distance Scaling Formula
Let $D$ be the path distance in pixels. Let $T_{\text{base}}$ be the base duration for $100\text{px}$ travel.
- **Base Distance**: $100\text{px} \rightarrow 1.0\times$ base duration.
- **Medium Distance**: $200\text{px} \rightarrow 1.3\times$ base duration.
- **Long Distance**: $400\text{px} \rightarrow 1.6\times$ base duration.

### Mathematical Scale Equation

$$T_{\text{scale}} = T_{\text{base}} \times \left(\frac{D}{100}\right)^{0.38}$$

### Rationale Table for UI timing
Use these durations as absolute parameters for elements in your composition:

| Element Type | Target Distance | Corporate Timing | Premium Timing | Easing Family |
|---|---|---|---|---|
| **Tooltip / Popover** | 0-10px (Fade only) | 80-120ms | 150-250ms | Decelerate / Ease Out |
| **Button Feedback** | 0px (Scale only) | 120-180ms | 200-300ms | Decelerate on release |
| **Icon Transition** | 10-30px | 150-250ms | 300-400ms | Decelerate / Spring |
| **Card Entrance** | 50-150px | 200-350ms | 400-550ms | Custom Bezier Out |
| **Modal / Dialog** | 100-300px | 300-400ms | 500-650ms | Ease Out Back / Cubic |
| **Page Shift** | 400px+ (Full viewport) | 400-600ms | 700-1000ms | Decelerate / Parallax |

---

## Interactive Easing Curves

Interactive user actions require split-timing:

### Hover Entrances
- **Constraint**: Must feel responsive.
- **Duration**: `<100ms`.
- **Curve**: Smooth deceleration.
- **Tangents**: `o: {"x": [0.25], "y": [0.0]}, i: {"x": [0.25], "y": [1.0]}`

### Mouse Presses (Active State)
- **Constraint**: Must feel solid and instantaneous.
- **Duration**: `<150ms`.
- **Curve**: Sharp acceleration into flat contraction.
- **Tangents**: `o: {"x": [0.0], "y": [0.0]}, i: {"x": [0.58], "y": [1.0]}`

---

## Multi-Keyframe Spring Formula

To code organic spring dynamics without a real physics engine, chain **three keyframes** using decaying overshoot amplitudes:

```json
// Spring decay loop: 100% -> 120% -> 92% -> 100%
"s": {
  "a": 1,
  "k": [
    { "t": 0, "s": [0, 0], "o": { "x": [0.34], "y": [1.56] }, "i": { "x": [0.64], "y": [1] } },
    { "t": 12, "s": [120, 120], "o": { "x": [0.33], "y": [0] }, "i": { "x": [0.67], "y": [1] } },
    { "t": 22, "s": [92, 92], "o": { "x": [0.33], "y": [0] }, "i": { "x": [0.67], "y": [1] } },
    { "t": 32, "s": [100, 100] }
  ]
}
```

---

## Common Mistakes & Quality Rules
1. **Never use Linear (`[0,0], [1,1]`)** for positional shifts. This looks robotic and cold. Use symmetric curves for loops, and snappy ease-outs for entrances.
2. **Matching start/end curves for loops**: Ensure your loop starting frame tangents match the exit curves of the terminal frame to prevent sharp "hiccups" at the loop boundary.
3. **Clamping overshoots**: Keep overshoot targets between `105%` and `125%` max. Values above `130%` look sloppy and unstable.

# Disney's 12 Animation Principles — Adapted for Lottie JSON

This reference guides AI agents in applying Disney's classical 12 animation principles directly within Lottie JSON schemas. It maps qualitative design rules to concrete Lottie properties (`ks`, `s`, `p`, `r`, `o`, `ti`, `to`).

---

## 1. Squash and Stretch (Volume Preservation)

Used to convey weight, speed, and flexibility. When a shape squashes horizontally, it must stretch vertically to preserve volume.

### Mathematical Volume Rule
To keep volume looking constant, the product of X and Y scale coordinates must equal approximately `10,000` (representing 100% * 100%).

$$\text{Scale}_X \times \text{Scale}_Y \approx 10,000$$

### Playful Scale Keyframes (lub-dub impact)
```json
"s": {
  "a": 1,
  "k": [
    { "t": 0, "s": [100, 100], "o": { "x": [0.34], "y": [1.56] }, "i": { "x": [0.64], "y": [1] } },
    { "t": 10, "s": [120, 83.3] },  // Stretch: 120 * 83.33 = 10,000
    { "t": 20, "s": [85, 117.6] },  // Squash: 85 * 117.6 = 10,000
    { "t": 30, "s": [100, 100] }
  ]
}
```

> [!WARNING]
> **Premium Brands**: Skip Squash and Stretch entirely for luxury, premium, or editorial products. Keep scaling uniform (e.g., `[100, 100] -> [98, 98] -> [100, 100]`).

---

## 2. Anticipation

Prepares the audience for an action by moving in the opposite direction first. This builds tension and makes the final motion feel far more satisfying.

### Lottie Mechanics
- **Properties**: Scale (`s`) or Position (`p`).
- **Timing**: 100-200ms before the main action.
- **Magnitude**: 5-15% of the main transition range.

### Button Pop Anticipation (Position & Scale)
Before expanding upwards, the button shifts slightly downwards and squishes down.
```json
"p": {
  "a": 1,
  "k": [
    { "t": 0, "s": [256, 256], "o": { "x": [0.5], "y": [-0.1] }, "i": { "x": [0.5], "y": [1] } },
    { "t": 10, "s": [256, 266] },   // Anticipation: moves 10px down first
    { "t": 35, "s": [256, 120] }    // Main Action: shoots up to target y=120
  ]
}
```

---

## 3. Staging

Directs the viewer's attention to the most important element in the scene.

### Lottie Staging Techniques
1. **Focus Dimming**: Dim non-hero layers to 40-60% opacity (`o`) or shift them slightly away using anchor offsets.
2. **Hero Stagger**: Keep supporting elements subtle, and let the main hero element enter **100-200ms (6-12 frames at 60fps)** after them.
3. **Anchor Positioning**: Set the anchor point (`a`) of the hero element precisely at the center of attention to keep scaling/rotation clean.

---

## 4. Straight Ahead vs. Pose to Pose

- **Straight Ahead**: Drawing frame-by-frame. Best for organic wiggles, particle bursts, and liquid drips.
- **Pose to Pose**: Creating start/end keyframes and interpolating. Best for structured UI transitions, icons, and menus.

For premium wiggles or loaders, use **Straight Ahead** keyframing by calculating coordinates mathematically frame-by-frame (e.g., standard sine/cosine curves spaced out every 1-2 frames).

---

## 5. Follow Through and Overlapping Action

Follow through means parts of the body continue moving after the main character stops. Overlapping action means different parts move at different rates.

### Lottie Stagger (Sibling Delay)
Offset the Start Time (`st`) or In Point (`ip`) of sibling layers to create a flowing entrance.
```json
// Layer 1: Parent
{ "ind": 1, "nm": "Base Card", "st": 0, "ip": 0 }
// Layer 2: Hero Title (Staggered by 4 frames)
{ "ind": 2, "nm": "Title Text", "parent": 1, "st": 4, "ip": 4 }
// Layer 3: Accent Button (Staggered by 8 frames)
{ "ind": 3, "nm": "Call To Action", "parent": 1, "st": 8, "ip": 8 }
```

### Spring Easing (Simulated Physics)
To simulate overlapping drag, apply easing curves with high exit speed and a soft settle (Overshoot):
- **Overshoot Out Easing**: `o: {"x": [0.34], "y": [1.56]}, i: {"x": [0.64], "y": [1.0]}`

---

## 6. Slow In and Slow Out (Easing)

Movement is rarely linear in the real world. Elements must accelerate smoothly (Slow Out) and decelerate smoothly (Slow In).

### The Easing Golden Rule
- **Entrances (Coming on-screen)**: Fast start, slow end (**Decelerate / Ease Out**).
- **Exits (Leaving the screen)**: Slow start, fast end (**Accelerate / Ease In**).
- **On-Screen loops/paths**: Slow at both ends (**Symmetric / Ease In Out**).

> [!IMPORTANT]
> **NEVER** use linear easing for physical coordinate changes. Linear interpolation is strictly reserved for: rotation loops, timers, progress bars, and track mattes.

---

## 7. Arcs

Natural movements follow curved trajectories (arcs), never mechanical straight lines.

### Spatial Bezier Tangents in Lottie
When animating Position (`p`), Lottie keyframes support **spatial tangents** `ti` (tangent in) and `to` (tangent out). These define a cubic bezier curve path for the spatial motion.

```json
"p": {
  "a": 1,
  "k": [
    {
      "t": 0,
      "s": [100, 300, 0],
      "o": { "x": [0.33], "y": [0] },
      "i": { "x": [0.67], "y": [1] },
      "to": [50, -100, 0],  // Pushes trajectory upward/right at departure
      "ti": [-50, 100, 0]   // Arrives from bottom-left at target
    },
    {
      "t": 45,
      "s": [400, 300, 0]
    }
  ]
}
```
*In this example, the element travels from `[100, 300]` to `[400, 300]` in a beautiful, natural upward arc rather than a flat horizontal line.*

---

## 8. Secondary Action

A secondary action supports and enriches the primary motion without stealing the spotlight.

### UI Secondary Combinations
- **Primary**: Modal slides in (`p` change).
- **Secondary**: Shadow layer expands and darkens (`s` + `o` change) to establish spatial depth.
- **Ambient**: Subtle particle spark wiggles or background gradients glowing in loop.

---

## 9. Timing

Timing defines the duration of the action. Spacing defines the speed variation within that duration.

- **Responsive Timing**: Quick feedbacks (`80-150ms`) to make the interface feel alive and reactive.
- **Emotional Spacing**: Adjust tangents `o` and `i` to distribute speed. Steep bezier curves feel snappy; flat curves feel luxurious.

---

## 10. Exaggeration

Exaggerating motion prevents it from looking flat or lifeless.

- **Playful/Energetic Archetypes**: Double the overshoot amplitudes and add rotation wiggles on stop (`5-15 degrees` swing settle).
- **Corporate/Premium Archetypes**: Clamp exaggeration. Keep overshoots under `3%` or eliminate entirely to look highly precise.

---

## 11. Solid Drawing & 3D Depth

Vector animations are inherently 2D, but we can fake 3D depth to make them feel heavy and grounded.

- **Parallax**: Move background layers at `30-50%` of the speed of the foreground layers using parenting hierarchies or separate keys.
- **Isometric Shadows**: Shift shadow position coordinates diagonally relative to scale contraction to simulate a 3D floor plane.

---

## 12. Appeal

Animations must have an elegant flow, satisfying timings, and absolute clarity.

- Avoid clutter. Keep the **Simplicity Threshold**: animate at most **two** concurrent properties per layer (e.g. Position + Scale, or Position + Opacity).
- Ensure color palettes match premium standards: clamp RGB color vectors to balanced, soft pastel or HSL-matched palettes.

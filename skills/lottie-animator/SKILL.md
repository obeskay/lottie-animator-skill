---
name: lottie-animator
description: |
  Generates professional Lottie animations from static SVGs. Replaces After Effects for motion graphics.
  Use when the user asks to: animate logo, create lottie, svg animation, motion graphics, wiggle animation,
  bounce effect, rotate animation, pulse effect, entrance animation, loading animation, loop animation.
  Supports advanced bezier curves, professional easing functions, and export to JSON/GIF/MP4.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Lottie Animator - SVG to Motion Graphics

Professional skill to create advanced Lottie animations from SVGs, eliminating the need for After Effects.

## When to Activate

Activate this skill when the user requests:
- Animate a logo or SVG icon
- Create motion graphics or animations
- Generate Lottie JSON files
- Effects: wiggle, bounce, rotate, pulse, fade, scale, morph
- Entrance, loop, loading animations, or transitions
- Replace After Effects workflow

## Main Workflow

### Phase 1: Philosophy of Motion (30 seconds)

**MANDATORY** before any code. Define:

1. **Brand Personality**: Professional, playful, elegant, energetic
2. **Emotional Response**: Trust, excitement, calm, urgency
3. **Motion Metaphor**: Fluid like water, solid like rock, light like air

```
Example: "Fintech Logo → professional + trust → precise and controlled movement"
Example: "Music App → creative + energy → organic with rhythmic pulses"
```

### Phase 2: SVG Analysis (30 seconds)

Before animating, analyze:

1. **Structure**: How many elements? Groups? Paths?
2. **Hierarchy**: Which elements are primary vs secondary?
3. **Opportunities**: Which parts can be animated independently?

```bash
# Analyze SVG
cat logo.svg | grep -E '<(path|g|rect|circle|ellipse)' | head -20
```

### Phase 3: Selection of Motion Type

| Type | Keyframes | FPS | Duration | Use Case |
|------|-----------|-----|----------|-----|
| Corporate | 8-12 | 30 | 1.5-2s | B2B, finance, legal |
| Organic | 25-45 | 60 | 2-3s | Audio, music, creatives |
| Bold/Attention | 15-25 | 60 | 0.8-1.5s | Startups, marketing |
| Cinematic | 50-120 | 60 | 3-5s | Luxury, entertainment |

### Phase 4: Create Lottie JSON

See: [references/lottie-structure.md](references/lottie-structure.md)

**Base Structure:**
```json
{
  "v": "5.12.1",
  "fr": 60,
  "ip": 0,
  "op": 120,
  "w": 512,
  "h": 512,
  "nm": "Animation Name",
  "ddd": 0,
  "assets": [],
  "layers": []
}
```

### Phase 5: Apply Easing with Bezier Curves

See: [references/bezier-easing.md](references/bezier-easing.md)

**Professional Easings:**
```json
// Ease Out Cubic - Soft Entrance
"o": {"x": [0.33], "y": [0]},
"i": {"x": [0.67], "y": [1]}

// Ease In Out Quart - Professional/Sharp
"o": {"x": [0.76], "y": [0]},
"i": {"x": [0.24], "y": [1]}

// Bounce - Playful
"o": {"x": [0.34], "y": [1.56]},
"i": {"x": [0.64], "y": [1]}
```

### Phase 6: Validate and Export

```bash
# Validate structure
python3 -c "import json; json.load(open('animation.json'))"

# Preview in browser
echo "Open in: https://lottiefiles.com/preview"
```

## Animation Types

### 1. Fade In
```json
{
  "ty": "tr",
  "o": {
    "a": 1,
    "k": [
      {"t": 0, "s": [0], "o": {"x": [0.33], "y": [0]}, "i": {"x": [0.67], "y": [1]}},
      {"t": 30, "s": [100]}
    ]
  }
}
```

### 2. Scale Bounce
```json
{
  "ty": "tr",
  "s": {
    "a": 1,
    "k": [
      {"t": 0, "s": [0, 0], "o": {"x": [0.34], "y": [1.56]}, "i": {"x": [0.64], "y": [1]}},
      {"t": 20, "s": [110, 110], "o": {"x": [0.33], "y": [0]}, "i": {"x": [0.67], "y": [1]}},
      {"t": 35, "s": [100, 100]}
    ]
  }
}
```

### 3. Rotate Continuous
```json
{
  "ty": "tr",
  "r": {
    "a": 1,
    "k": [
      {"t": 0, "s": [0]},
      {"t": 120, "s": [360]}
    ]
  }
}
```

### 4. Position Slide
```json
{
  "ty": "tr",
  "p": {
    "a": 1,
    "k": [
      {"t": 0, "s": [-100, 256], "o": {"x": [0.25], "y": [0.1]}, "i": {"x": [0.25], "y": [1]}},
      {"t": 45, "s": [256, 256]}
    ]
  }
}
```

## Animatable Properties

| Property | Code | Type | Description |
|-----------|--------|------|-------------|
| Position | `p` | [x, y] | Movement in space |
| Scale | `s` | [x, y] | Relative size (100 = original) |
| Rotation | `r` | degrees | Rotation on Z axis |
| Opacity | `o` | 0-100 | Transparency |
| Anchor | `a` | [x, y] | Transformation point |
| Skew | `sk` | degrees | Slant/Shear |

## Advanced Human-Like Motion Patterns

To achieve "wow" results, layer these principles:

1.  **Anticipation**: Before a major move, move slightly in the opposite direction (e.g., crouch before jumping).
2.  **Follow-through**: The movement shouldn't stop abruptly. Elements should overshoot slightly and settle back.
3.  **Squash & Stretch**: Deform the object (scale X up, Y down) to indicate speed or weight. **Maintain volume** (X * Y should roughly constant).
4.  **Staggering**: Do not animate all elements at once. Offset start times (`st`) by 2-5 frames for a cascading effect.

### Specific Patterns

#### ❤️ Heart Beat (Advanced)
A real heartbeat has a "lub-dub" rhythm.
1.  **Systole (Lub)**: Rapid expansion (Frame 0-8) to 115%. Sharp ease out.
2.  **Diastole Start (Dub)**: Quick retraction (Frame 8-12) to 90%.
3.  **Refill**: Smaller expansion (Frame 12-18) to 105%.
4.  **Rest**: Slow return to normal (Frame 18-45) to 100%.
5.  *Tip*: Add a slight rotation or position wiggle for organic feel.

#### ⚡ Lightning Bolt
Needs impact and chaos.
1.  **Flash**: Frame 0 (Opacity 0->100).
2.  **Strike**: Use "Trim Path" (`tm`) to draw the bolt from top to bottom instantly (0-2 frames).
3.  **Afterglow**: Duplicate the layer, blur it (or reduce opacity), and fade it out slower than the main bolt.
4.  **Jitter**: Wiggle the path vertices or position between frames 2-6 to simulate electrical instability.

#### 🔔 Bell Ringing
Physics-based pendular motion with decay.
1.  **Anchor Point**: MUST be at the top center of the bell handle.
2.  **Initial Hit**: Rotate +25 deg (fast impact).
3.  **Overshoot**: Rotate -20 deg.
4.  **Decay**: Swing back and forth with reducing amplitude (+15, -10, +5, -2, 0).
5.  **Clapper**: The clapper (ball inside) should "drag" behind the bell body or swing with a larger amplitude to show weight.

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Non-looping animation | `ip` != 0 or last keyframe != `op` | Ensure start/end keyframes match |
| Stiff movement | No easing | Add bezier curves to `i`/`o` |
| Jerky jumps | Keyframes too far apart | Add intermediate keyframes |
| Large file size | Embedded assets | Use external references or shapes |

## References

- [Lottie JSON Structure](references/lottie-structure.md)
- [Bezier Curves and Easing](references/bezier-easing.md)
- [Animation Examples](references/examples.md)
- [Official Lottie Documentation](https://lottiefiles.github.io/lottie-docs/)

## Final Checklist

- [ ] Motion philosophy defined
- [ ] SVG analyzed and optimized
- [ ] Animation type selected
- [ ] Keyframes with appropriate easing
- [ ] Seamless loop (if applicable)
- [ ] Specific patterns applied (Heart, Bell, etc.)
- [ ] JSON validated
- [ ] Preview verified

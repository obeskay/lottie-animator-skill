---
name: lottie-animator
description: |
  Generates professional Lottie animations from static SVGs. Replaces After Effects for motion graphics.
  Use when the user asks to: animate logo, create lottie, svg animation, motion graphics, wiggle animation,
  bounce effect, rotate animation, pulse effect, entrance animation, loading animation, loop animation,
  icon animation, character animation, morphing, path drawing, trim path, walking animation, run cycle,
  walk cycle, frame-by-frame animation, sprite animation.
  Supports advanced bezier curves, shape modifiers, parenting, mattes, morphing, character rigs,
  and professional frame-by-frame animation techniques.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Lottie Animator - SVG to Motion Graphics

Professional skill to create advanced Lottie animations from SVGs, eliminating the After Effects workflow entirely by using intelligent motion design.

---

## Quick Reference: 8-Step Animation Checklist

Before creating or writing any animation keyframes, you **MUST** align on the following checklist:

1. **Emotional target?** — What should the viewer feel? (joy, calm, trust, excitement, urgency)
2. **Motion Personality?** — Select exactly one archetype: Playful, Premium, Corporate, or Energetic.
3. **Primary property?** — Focus on the hero transition first: position (`p`), scale (`s`), rotation (`r`), or opacity (`o`).
4. **Distance and Timing?** — Calculate target frames based on the 1/3 spatial scaling rule.
5. **Easing family?** — Map curve constants: entrance = ease-out, exit = ease-in, loop = ease-in-out.
6. **Hero elements?** — Plan staging offsets (hero enters 100-200ms after background).
7. **Secondary & ambient layers?** — Plan secondary accents (shadow shifts, spark wiggles).
8. **Volume Preservation?** — Keep X/Y scale multiplication constant (`~10,000`) for wiggles and squashes (skip for premium).

---

## When to Activate

Activate this skill when the user requests:
- Animate a logo, icon, or SVG graphic
- Create motion graphics or vector animations
- Generate Lottie JSON files
- Effects: wiggle, bounce, rotate, pulse, fade, scale, morph
- Entrance, loop, loading animations, or transitions
- Path drawing/reveal animations (Trim Path)
- Character animation, walking cycles, run cycles
- Shape morphing (icon transitions)
- Replace After Effects workflow

**Decision tree:**
1. Does it serve a functional purpose (feedback, guidance)? → Apply strict responsive timing rules (<150ms).
2. Does it express brand personality? → Select and stick to a single Motion Personality archetype.
3. Does it tell a story or guide attention? → Apply adapted Disney principles (anticipation, arcs, staging).
4. Is this a complex multi-element scene? → Plan layers, parenting bone systems, and stagger offsets.

---

## Critical: SVG Understanding

Before animating ANY SVG, you MUST understand its path structure.

See: [references/svg-to-lottie.md](references/svg-to-lottie.md)

### SVG Path Command Quick Reference

| Command | Description | Lottie Conversion |
|---------|-------------|-------------------|
| M x,y | Move to | Starting vertex |
| L x,y | Line to | Vertex with zero tangents |
| C cp1 cp2 end | Cubic bezier | Native support |
| Q ctrl end | Quadratic bezier | Convert to cubic |
| A rx ry ... | Arc | Split into cubic segments |
| Z | Close path | Set `c: true` |

### Path to Lottie Vertex Formula

```
For C x1,y1 x2,y2 x,y from point (px, py):
- Previous vertex outTangent: [x1-px, y1-py]
- Current vertex: [x, y]
- Current vertex inTangent: [x2-x, y2-y]
```

---

## Main Workflow

### Phase 1: Motion Philosophy (30 seconds)

**MANDATORY** before any code. Define:

1. **Brand Personality**: Professional, playful, elegant, energetic (see [references/motion-personality.md](references/motion-personality.md))
2. **Emotional Response**: Trust, excitement, calm, urgency
3. **Motion Metaphor**: Fluid like water, solid like rock, light like air

```
Example: "Fintech Logo → professional + trust → precise and controlled movement"
Example: "Music App → creative + energy → organic with rhythmic pulses"
Example: "Healthcare → calm + reliable → smooth, slow easings"
```

### Phase 2: SVG Deep Analysis

Before animating, thoroughly analyze:
1. **Structure**: Elements, groups, paths, viewBox dimensions
2. **Path Complexity**: Vertex count, curve types (C, Q, A commands)
3. **Hierarchy**: Primary elements vs. secondary details
4. **Animation Opportunities**: Independent parts, stroke-based vs fill-based

```bash
# Analyze SVG structure
cat icon.svg | grep -E '<(path|g|rect|circle|ellipse|line|polyline)' | head -30
```

**Key Questions**:
- Is it stroke-based? → Consider Trim Path animation.
- Multiple paths? → Consider staggered entrance.
- Complex shape? → Consider scale/rotate instead of morph.
- Icon library (Phosphor/Lucide)? → Clean, minimal vertices.

### Phase 3: Animation Strategy Selection

| Strategy | Best For | Technique | Reference |
|---|---|---|---|
| **Draw On** | Stroke icons, signatures | Trim Path | [references/shape-modifiers.md](references/shape-modifiers.md) |
| **Pop In** | Logos, buttons | Scale + Opacity | [references/disney-principles.md](references/disney-principles.md) |
| **Morph** | Icon transitions (hamburger→X) | Path keyframes | [references/professional-techniques.md](references/professional-techniques.md) |
| **Stagger** | Multiple elements | Delayed start times | [references/disney-principles.md](references/disney-principles.md) |
| **Character** | People, mascots | Parenting + bone hierarchy | [references/professional-techniques.md](references/professional-techniques.md) |
| **Loader** | Progress, spinners | Rotation + Trim Path | [references/shape-modifiers.md](references/shape-modifiers.md) |
| **Frame-by-Frame** | Walk/run cycles, complex characters | `ip`/`op` layer switching | [references/professional-techniques.md](references/professional-techniques.md) |

---

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

---

### Phase 5: Apply Professional Easing and Timing

Map bezier curves and frame durations strictly using your selected archetype.

See: [references/bezier-easing.md](references/bezier-easing.md)

| Use Case | Out Tangent (`o`) | In Tangent (`i`) | Rationale |
|----------|-------------|------------|---|
| **Entrance (Ease Out)** | `[0.33, 0]` | `[0.67, 1]` | Fast start, gentle settle |
| **Exit (Ease In)** | `[0.55, 0.055]` | `[0.675, 0.19]` | Gentle start, explosive departure |
| **Loop (Ease In Out)** | `[0.645, 0.045]` | `[0.355, 1]` | Seamless symmetrical timing |
| **Bounce (Playful)** | `[0.34, 1.56]` | `[0.64, 1]` | Bouncy overshoot, soft settle |
| **Spring (Elastic)** | `[0.5, 1.5]` | `[0.5, 0.9]` | High responsiveness, dynamic tension |

---

### Phase 6: Validate and Export

```bash
# Validate JSON structure
python3 -c "import json; json.load(open('animation.json'))"

# Preview
echo "Open in: https://lottiefiles.com/preview"
```

---

## Shape Modifiers

See: [references/shape-modifiers.md](references/shape-modifiers.md)

### Trim Path (Icon Drawing Animation)

```json
{
  "ty": "tm",
  "s": {"a": 0, "k": 0},
  "e": {
    "a": 1,
    "k": [
      {"t": 0, "s": [0], "o": {"x": [0.33], "y": [0]}, "i": {"x": [0.67], "y": [1]}},
      {"t": 45, "s": [100]}
    ]
  },
  "o": {"a": 0, "k": 0},
  "m": 1
}
```

### Repeater (Radial/Linear Patterns)

```json
{
  "ty": "rp",
  "c": {"a": 0, "k": 8},
  "tr": {
    "r": {"a": 0, "k": 45},
    "so": {"a": 0, "k": 100},
    "eo": {"a": 0, "k": 30}
  }
}
```

### Offset Path (Glow/Outline Effects)

```json
{
  "ty": "op",
  "a": {"a": 1, "k": [{"t": 0, "s": [0]}, {"t": 30, "s": [8]}]},
  "lj": 2
}
```

---

## Advanced Techniques & Reference Links

Ensure you consult specific reference documents for complex animation behaviors:

- **Disney Principles**: Apply squash/stretch, anticipation, and arcs correctly.
  - [references/disney-principles.md](references/disney-principles.md)
- **Brand Personalities**: Select Playful, Premium, Corporate, or Energetic.
  - [references/motion-personality.md](references/motion-personality.md)
- **Bone Parenting & Rigs**: Rig layers using parenting offsets.
  - [references/professional-techniques.md](references/professional-techniques.md)
- **Frame-by-Frame Switching**: Implement walk cycles using layered `ip`/`op` sprite frames.
  - [references/professional-techniques.md](references/professional-techniques.md)
- **GSAP & ScrollTrigger Integration**: Bind Lottie scrub parameters, canvas pools, and 3D spring deflections to mouse/scroll events.
  - [references/lottie-gsap-integration.md](references/lottie-gsap-integration.md)
- **Lottie Tools & Ecosystem**: Select editing workflows, leverage dotLottie (.lottie) compression packaging, and audit run-time rendering.
  - [references/lottie-tools-ecosystem.md](references/lottie-tools-ecosystem.md)
- **Bezier Easing Reference**: Map snappiness using custom cubic bezier coordinates.
  - [references/bezier-easing.md](references/bezier-easing.md)

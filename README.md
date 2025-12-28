# Lottie Animator Skill

<div align="center">

![Lottie Animator](https://img.shields.io/badge/Lottie-Animator-6366f1?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0tMiAxNWwtNS01IDEuNDEtMS40MUwxMCAxNC4xN2w3LjU5LTcuNTlMMTkgOGwtOSA5eiIvPjwvc3ZnPg==)
![Claude Code](https://img.shields.io/badge/Claude-Code-ff6b35?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)

**Generate professional Lottie animations from SVGs using AI**

*Replace After Effects with intelligent motion design*

[Installation](#installation) • [Usage](#usage) • [Features](#features) • [Examples](#examples)

</div>

---

## Why Lottie Animator?

Traditional animation workflow requires:
- **After Effects** ($22.99/mo) + **Bodymovin plugin**
- **Hours of manual keyframing**
- **Motion design expertise**

With Lottie Animator:
- **Zero cost** - Open source
- **Seconds, not hours** - AI-powered generation
- **No expertise needed** - Natural language instructions

## Installation

### From Marketplace (Recommended)

```bash
# Add the marketplace
/plugin marketplace add obedvargas/lottie-animator-skill

# Install the plugin
/plugin install lottie-animator
```

### Local Installation

```bash
# Clone the repository
git clone https://github.com/obedvargas/lottie-animator-skill.git

# Use with Claude Code
claude --plugin-dir ./lottie-animator-skill
```

## Usage

The skill activates automatically when you request:

```
"Animate this SVG logo"
"Create a Lottie animation"
"Generate motion graphics for my icon"
"Make a bounce/wiggle/pulse effect"
"Create an entrance/loading/loop animation"
```

### Quick Example

```
You: Animate my logo with a smooth entrance effect

Claude: [Activates lottie-animator skill]

1. Motion Philosophy: Professional brand → confident, controlled movement
2. SVG Analysis: Single element, circular shape
3. Animation Type: Corporate entrance (30fps, 1.5s)
4. Applying: Fade + Scale with ease-out-cubic bezier
5. Generated: logo-animation.json (ready to use)
```

## Features

### Professional Bezier Curves

Pre-configured easing presets matching industry standards:

| Preset | Use Case |
|--------|----------|
| `ease-out-cubic` | Smooth entrances |
| `ease-in-out-quart` | Professional transitions |
| `bounce` | Playful interactions |
| `elastic` | Dynamic feedback |
| `spring` | Natural motion |

### Animation Types

| Type | FPS | Duration | Best For |
|------|-----|----------|----------|
| Corporate | 30 | 1.5-2s | B2B, Finance |
| Organic | 60 | 2-3s | Audio, Creative |
| Bold | 60 | 0.8-1.5s | Startups, Marketing |
| Cinematic | 60 | 3-5s | Luxury, Entertainment |

### Supported Effects

- **Entrance**: Fade, Scale, Slide, Reveal
- **Loop**: Pulse, Wiggle, Float, Rotate
- **Attention**: Bounce, Shake, Flash
- **Advanced**: Morph, Stagger, Draw-on

## Documentation

The skill includes comprehensive references:

- **[Bezier Easing](skills/lottie-animator/references/bezier-easing.md)** - 20+ professional easing presets
- **[Lottie Structure](skills/lottie-animator/references/lottie-structure.md)** - Complete JSON specification
- **[Examples](skills/lottie-animator/references/examples.md)** - 8 ready-to-use animations
- **[SVG to Lottie](skills/lottie-animator/references/svg-to-lottie.md)** - Conversion guide

## Workflow

```
┌─────────────────────────────────────────────────────────┐
│  1. MOTION PHILOSOPHY (30s)                             │
│     Define brand personality and emotional response     │
├─────────────────────────────────────────────────────────┤
│  2. SVG ANALYSIS (30s)                                  │
│     Identify structure, hierarchy, opportunities        │
├─────────────────────────────────────────────────────────┤
│  3. TYPE SELECTION                                      │
│     Corporate → Organic → Bold → Cinematic              │
├─────────────────────────────────────────────────────────┤
│  4. LOTTIE GENERATION                                   │
│     Keyframes + Bezier curves + Transforms              │
├─────────────────────────────────────────────────────────┤
│  5. VALIDATION                                          │
│     Structure check + Loop verification                 │
├─────────────────────────────────────────────────────────┤
│  6. DELIVERY                                            │
│     JSON ready for web/mobile/desktop                   │
└─────────────────────────────────────────────────────────┘
```

## Examples

### Bounce Entrance
```json
{
  "s": {
    "a": 1,
    "k": [
      {"t": 0, "s": [0, 0], "o": {"x": [0.34], "y": [1.56]}, "i": {"x": [0.64], "y": [1]}},
      {"t": 20, "s": [110, 110]},
      {"t": 35, "s": [100, 100]}
    ]
  }
}
```

### Continuous Pulse
```json
{
  "s": {
    "a": 1,
    "k": [
      {"t": 0, "s": [100, 100], "o": {"x": [0.645], "y": [0.045]}, "i": {"x": [0.355], "y": [1]}},
      {"t": 30, "s": [110, 110]},
      {"t": 60, "s": [100, 100]}
    ]
  }
}
```

## Resources

- [Lottie Documentation](https://lottiefiles.github.io/lottie-docs/)
- [LottieFiles Preview](https://lottiefiles.com/preview)
- [Cubic Bezier Editor](https://cubic-bezier.com/)
- [Easings.net](https://easings.net/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

**Obed Vargas**

- GitHub: [@obedvargas](https://github.com/obedvargas)

---

<div align="center">

**Made with AI for designers and developers**

*No After Effects required*

</div>

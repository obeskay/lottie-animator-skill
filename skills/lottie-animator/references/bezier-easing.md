# Bezier Curves and Easing Functions

Complete reference of bezier curves for professional Lottie animations.

## Fundamentals

Bezier curves in Lottie control the interpolation between keyframes:
- **X Axis**: Time (0 = current keyframe, 1 = next keyframe)
- **Y Axis**: Interpolated Value (0 = current value, 1 = next value)

### JSON Structure

```json
{
  "t": 0,           // Keyframe frame
  "s": [0],         // Start value
  "o": {            // OUT - exit from current keyframe
    "x": [0.33],
    "y": [0]
  },
  "i": {            // IN - entry to next keyframe
    "x": [0.67],
    "y": [1]
  }
}
```

## Easing Presets

### Ease Out (Deceleration)
Starts fast, ends slow. Ideal for **entrances**.

```json
// Ease Out Quad
"o": {"x": [0.25], "y": [0.46]},
"i": {"x": [0.45], "y": [0.94]}

// Ease Out Cubic (Recommended)
"o": {"x": [0.33], "y": [0]},
"i": {"x": [0.67], "y": [1]}

// Ease Out Quart
"o": {"x": [0.165], "y": [0.84]},
"i": {"x": [0.44], "y": [1]}

// Ease Out Expo
"o": {"x": [0.19], "y": [1]},
"i": {"x": [0.22], "y": [1]}
```

### Ease In (Acceleration)
Starts slow, ends fast. Ideal for **exits**.

```json
// Ease In Quad
"o": {"x": [0.55], "y": [0.085]},
"i": {"x": [0.68], "y": [0.53]}

// Ease In Cubic
"o": {"x": [0.55], "y": [0.055]},
"i": {"x": [0.675], "y": [0.19]}

// Ease In Quart
"o": {"x": [0.895], "y": [0.03]},
"i": {"x": [0.685], "y": [0.22]}
```

### Ease In Out (Symmetric)
Smooth at both ends. Ideal for **loops** and **transitions**.

```json
// Ease In Out Quad
"o": {"x": [0.455], "y": [0.03]},
"i": {"x": [0.515], "y": [0.955]}

// Ease In Out Cubic (Professional)
"o": {"x": [0.645], "y": [0.045]},
"i": {"x": [0.355], "y": [1]}

// Ease In Out Quart
"o": {"x": [0.76], "y": [0]},
"i": {"x": [0.24], "y": [1]}

// Ease In Out Expo
"o": {"x": [1], "y": [0]},
"i": {"x": [0], "y": [1]}
```

### Bounce and Elastic
Movements with rebound. Ideal for **attention** and **playfulness**.

```json
// Bounce Out
"o": {"x": [0.34], "y": [1.56]},
"i": {"x": [0.64], "y": [1]}

// Elastic Out
"o": {"x": [0.5], "y": [1.5]},
"i": {"x": [0.5], "y": [1]}

// Back Out (Overshoot)
"o": {"x": [0.175], "y": [0.885]},
"i": {"x": [0.32], "y": [1.275]}
```

### Spring
Organic spring-like motion.

```json
// Spring Light
"o": {"x": [0.5], "y": [1.2]},
"i": {"x": [0.5], "y": [0.9]}

// Spring Heavy
"o": {"x": [0.35], "y": [1.7]},
"i": {"x": [0.65], "y": [0.8]}
```

## Visual Guide

```
LINEAR:        ____________________
               /
              /
             /
            /

EASE OUT:      ____________________
               /
              |
              |
             /

EASE IN:       ____________________
                               /
                              |
                              |
                             /

EASE IN OUT:   ____________________
                    _____
                   /     \
                  |       |
                 /         \

BOUNCE:        ____________________
                    ___
                   /   \_/\
                  |
                 /
```

## By Use Case

### Modern UI/UX
```json
// Material Design Standard
"o": {"x": [0.4], "y": [0]},
"i": {"x": [0.2], "y": [1]}

// iOS Spring
"o": {"x": [0.5], "y": [1.8]},
"i": {"x": [0.5], "y": [0.7]}
```

### Motion Graphics
```json
// Smooth Cinematic
"o": {"x": [0.7], "y": [0]},
"i": {"x": [0.3], "y": [1]}

// Dramatic
"o": {"x": [0.9], "y": [0]},
"i": {"x": [0.1], "y": [1]}
```

### Corporate Logos
```json
// Professional Controlled
"o": {"x": [0.25], "y": [0.1]},
"i": {"x": [0.25], "y": [1]}

// Elegant
"o": {"x": [0.42], "y": [0]},
"i": {"x": [0.58], "y": [1]}
```

### Icons and Micro-interactions
```json
// Fast and Snappy
"o": {"x": [0.2], "y": [0]},
"i": {"x": [0], "y": [1]}

// Subtle Bounce
"o": {"x": [0.34], "y": [1.2]},
"i": {"x": [0.64], "y": [1]}
```

## Extreme Values

### Overshoot
When `y > 1`, the value goes past the destination before settling:

```json
// Overshoot 20%
"o": {"x": [0.2], "y": [0]},
"i": {"x": [0.5], "y": [1.2]}

// Dramatic Overshoot 50%
"o": {"x": [0.1], "y": [0]},
"i": {"x": [0.4], "y": [1.5]}
```

### Undershoot
When `y < 0` at the start, it moves backward before moving forward:

```json
// Anticipation
"o": {"x": [0.5], "y": [-0.1]},
"i": {"x": [0.5], "y": [1]}
```

## Multi-Keyframe Combinations

### Realistic Bounce (3 keyframes)
```json
[
  {"t": 0, "s": [0], "o": {"x": [0.33], "y": [0]}, "i": {"x": [0.67], "y": [1]}},
  {"t": 15, "s": [115], "o": {"x": [0.33], "y": [0]}, "i": {"x": [0.67], "y": [1]}},
  {"t": 25, "s": [95], "o": {"x": [0.33], "y": [0]}, "i": {"x": [0.67], "y": [1]}},
  {"t": 35, "s": [100]}
]
```

### Elastic Settle (4 keyframes)
```json
[
  {"t": 0, "s": [0], "o": {"x": [0.22], "y": [1]}, "i": {"x": [0.36], "y": [1]}},
  {"t": 12, "s": [120], "o": {"x": [0.22], "y": [1]}, "i": {"x": [0.36], "y": [1]}},
  {"t": 22, "s": [92], "o": {"x": [0.22], "y": [1]}, "i": {"x": [0.36], "y": [1]}},
  {"t": 30, "s": [104], "o": {"x": [0.22], "y": [1]}, "i": {"x": [0.36], "y": [1]}},
  {"t": 38, "s": [100]}
]
```

## Tools

- [Cubic Bezier Editor](https://cubic-bezier.com/)
- [Easings.net](https://easings.net/)
- [Lottie Preview](https://lottiefiles.com/preview)

## Tips

1. **Consistency**: Use the same easing for related animations.
2. **Duration**: Smooth easings need more frames to be appreciated.
3. **Overshoots**: Use sparingly, max 20-30% for professional looks.
4. **Loops**: Always use symmetric ease in-out for seamless loops.
5. **Testing**: Test at 0.5x and 2x speed to validate smoothness.

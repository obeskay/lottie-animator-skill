# Complete Lottie JSON Structure

Full reference of the Lottie specification for professional animation generation.

## Root Structure

```json
{
  "v": "5.12.1",      // Lottie Version
  "fr": 60,           // Frame rate (FPS)
  "ip": 0,            // In point (start frame)
  "op": 120,          // Out point (end frame)
  "w": 512,           // Width in pixels
  "h": 512,           // Height in pixels
  "nm": "Animation",  // Name
  "ddd": 0,           // 3D disabled
  "assets": [],       // Assets (images, precomps)
  "layers": [],       // Animation layers
  "meta": {}          // Optional metadata
}
```

## Layer Types (ty)

| ty | Type | Description |
|----|------|-------------|
| 0 | Precomp | Nested composition |
| 1 | Solid | Solid color layer |
| 2 | Image | Image layer |
| 3 | Null | Null layer (controller) |
| 4 | Shape | Shape layer (SVG) |
| 5 | Text | Text layer |

## Shape Layer (ty: 4) - Most Used

```json
{
  "ddd": 0,
  "ty": 4,
  "ind": 1,           // Layer index
  "nm": "Shape Layer",
  "sr": 1,            // Time stretch
  "st": 0,            // Start time
  "ip": 0,            // In point
  "op": 120,          // Out point
  "ks": {},           // Transform properties
  "ao": 0,            // Auto-orient (0 or 1)
  "shapes": []        // Array of shapes
}
```

## Transform Properties (ks)

```json
{
  "ks": {
    "a": {"a": 0, "k": [256, 256]},     // Anchor point
    "p": {"a": 0, "k": [256, 256]},     // Position
    "s": {"a": 0, "k": [100, 100]},     // Scale (%)
    "r": {"a": 0, "k": 0},              // Rotation (degrees)
    "o": {"a": 0, "k": 100},            // Opacity (0-100)
    "sk": {"a": 0, "k": 0},             // Skew
    "sa": {"a": 0, "k": 0}              // Skew axis
  }
}
```

## Animated vs Static Property

```json
// Static (a: 0)
{"a": 0, "k": [256, 256]}

// Animated (a: 1)
{
  "a": 1,
  "k": [
    {
      "t": 0,                           // Frame
      "s": [0, 256],                    // Start value
      "o": {"x": [0.33], "y": [0]},     // Out tangent
      "i": {"x": [0.67], "y": [1]}      // In tangent
    },
    {
      "t": 60,
      "s": [256, 256]                   // End value (no easing needed at end)
    }
  ]
}
```

## Shape Types

### Group (ty: "gr")
```json
{
  "ty": "gr",
  "nm": "Group",
  "it": [
    // Child shapes
    // Transform at the end
  ]
}
```

### Rectangle (ty: "rc")
```json
{
  "ty": "rc",
  "nm": "Rectangle",
  "p": {"a": 0, "k": [0, 0]},      // Position
  "s": {"a": 0, "k": [100, 100]},  // Size
  "r": {"a": 0, "k": 0}            // Corner radius
}
```

### Ellipse (ty: "el")
```json
{
  "ty": "el",
  "nm": "Ellipse",
  "p": {"a": 0, "k": [0, 0]},      // Position
  "s": {"a": 0, "k": [100, 100]}   // Size
}
```

### Path (ty: "sh") - For SVGs
```json
{
  "ty": "sh",
  "nm": "Path",
  "ks": {
    "a": 0,
    "k": {
      "c": true,                    // Closed path
      "v": [[0,0], [100,0], [100,100], [0,100]],   // Vertices
      "i": [[0,0], [0,0], [0,0], [0,0]],           // In tangents
      "o": [[0,0], [0,0], [0,0], [0,0]]            // Out tangents
    }
  }
}
```

### Fill (ty: "fl")
```json
{
  "ty": "fl",
  "nm": "Fill",
  "c": {"a": 0, "k": [1, 0, 0, 1]},  // Color RGBA (0-1)
  "o": {"a": 0, "k": 100}            // Opacity
}
```

### Stroke (ty: "st")
```json
{
  "ty": "st",
  "nm": "Stroke",
  "c": {"a": 0, "k": [0, 0, 0, 1]},  // Color RGBA
  "o": {"a": 0, "k": 100},           // Opacity
  "w": {"a": 0, "k": 2},             // Width
  "lc": 2,                           // Line cap (1=butt, 2=round, 3=square)
  "lj": 2                            // Line join (1=miter, 2=round, 3=bevel)
}
```

### Transform within Group (ty: "tr")
```json
{
  "ty": "tr",
  "a": {"a": 0, "k": [0, 0]},        // Anchor
  "p": {"a": 0, "k": [256, 256]},    // Position
  "s": {"a": 0, "k": [100, 100]},    // Scale
  "r": {"a": 0, "k": 0},             // Rotation
  "o": {"a": 0, "k": 100}            // Opacity
}
```

## Keyframe Structure

```json
{
  "t": 0,                    // Frame number
  "s": [0],                  // Start value (array)
  "h": 0,                    // Hold (0=interpolate, 1=hold)
  "o": {                     // Out tangent (outgoing curve)
    "x": [0.33],
    "y": [0]
  },
  "i": {                     // In tangent (incoming curve)
    "x": [0.67],
    "y": [1]
  }
}
```

## Transition Presets

Based on standard motion graphics principles:

```json
// Linear
"o": {"x": [0.33], "y": [0.33]},
"i": {"x": [0.67], "y": [0.67]}

// Ease (smooth)
"o": {"x": [0.33], "y": [0]},
"i": {"x": [0.67], "y": [1]}

// Fast (snappy)
"o": {"x": [0.17], "y": [0.33]},
"i": {"x": [0.83], "y": [0.67]}

// Overshoot (springy)
"o": {"x": [0.67], "y": [-0.33]},
"i": {"x": [0.33], "y": [1.33]}
```

# SVG to Lottie Conversion

Guide to convert static SVGs into Lottie animations.

## Conversion Process

### Step 1: Analyze the SVG

```xml
<svg viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="#3498db"/>
  <rect x="20" y="20" width="60" height="60" fill="#e74c3c"/>
  <path d="M10,10 L50,90 L90,10 Z" fill="#2ecc71"/>
</svg>
```

Extract:
- **viewBox**: 0 0 100 100 → `w: 100, h: 100`
- **Elements**: circle, rect, path
- **Attributes**: positions, colors, transforms

### Step 2: Map Elements

| SVG | Lottie Shape Type |
|-----|-------------------|
| `<circle>` | `el` (ellipse) |
| `<ellipse>` | `el` |
| `<rect>` | `rc` (rectangle) |
| `<path>` | `sh` (shape/path) |
| `<polygon>` | `sh` |
| `<polyline>` | `sh` |
| `<line>` | `sh` |
| `<g>` | `gr` (group) |

### Step 3: Convert Colors

```javascript
// SVG: fill="#3498db" or fill="rgb(52,152,219)"
// Lottie: [R, G, B, A] where each value is 0-1

"#3498db" → [0.204, 0.596, 0.859, 1]

// Formula: hex_value / 255
// 0x34 = 52 → 52/255 = 0.204
// 0x98 = 152 → 152/255 = 0.596
// 0xdb = 219 → 219/255 = 0.859
```

## Shape Conversion

### Circle → Ellipse

```xml
<!-- SVG -->
<circle cx="50" cy="50" r="40" fill="#3498db"/>
```

```json
// Lottie
{
  "ty": "gr",
  "it": [
    {
      "ty": "el",
      "p": {"a": 0, "k": [0, 0]},
      "s": {"a": 0, "k": [80, 80]}  // diameter = r * 2
    },
    {
      "ty": "fl",
      "c": {"a": 0, "k": [0.204, 0.596, 0.859, 1]},
      "o": {"a": 0, "k": 100}
    },
    {
      "ty": "tr",
      "p": {"a": 0, "k": [50, 50]},  // cx, cy
      "s": {"a": 0, "k": [100, 100]},
      "r": {"a": 0, "k": 0},
      "o": {"a": 0, "k": 100}
    }
  ]
}
```

### Rect → Rectangle

```xml
<!-- SVG -->
<rect x="20" y="20" width="60" height="60" rx="5" fill="#e74c3c"/>
```

```json
// Lottie
{
  "ty": "gr",
  "it": [
    {
      "ty": "rc",
      "p": {"a": 0, "k": [0, 0]},
      "s": {"a": 0, "k": [60, 60]},     // width, height
      "r": {"a": 0, "k": 5}              // rx (corner radius)
    },
    {
      "ty": "fl",
      "c": {"a": 0, "k": [0.906, 0.298, 0.235, 1]},
      "o": {"a": 0, "k": 100}
    },
    {
      "ty": "tr",
      "p": {"a": 0, "k": [50, 50]},      // x + width/2, y + height/2
      "s": {"a": 0, "k": [100, 100]},
      "r": {"a": 0, "k": 0},
      "o": {"a": 0, "k": 100}
    }
  ]
}
```

### Path → Shape

```xml
<!-- SVG -->
<path d="M10,10 L50,90 L90,10 Z" fill="#2ecc71"/>
```

```json
// Lottie
{
  "ty": "gr",
  "it": [
    {
      "ty": "sh",
      "ks": {
        "a": 0,
        "k": {
          "c": true,                      // Z = closed
          "v": [[10, 10], [50, 90], [90, 10]],  // Vertices (M, L, L)
          "i": [[0, 0], [0, 0], [0, 0]],        // In tangents (lines = 0)
          "o": [[0, 0], [0, 0], [0, 0]]         // Out tangents
        }
      }
    },
    {
      "ty": "fl",
      "c": {"a": 0, "k": [0.18, 0.8, 0.443, 1]},
      "o": {"a": 0, "k": 100}
    },
    {
      "ty": "tr",
      "p": {"a": 0, "k": [0, 0]},
      "s": {"a": 0, "k": [100, 100]},
      "r": {"a": 0, "k": 0},
      "o": {"a": 0, "k": 100}
    }
  ]
}
```

## Bezier Path Conversion

### SVG Path Commands

```
M x,y     = Move to (absolute)
m dx,dy   = Move to (relative)
L x,y     = Line to
l dx,dy   = Line to relative
H x       = Horizontal line to
V y       = Vertical line to
C x1,y1 x2,y2 x,y = Cubic bezier
c         = Cubic bezier relative
S x2,y2 x,y = Smooth cubic
Q x1,y1 x,y = Quadratic bezier
T x,y     = Smooth quadratic
A rx ry angle large-arc sweep x,y = Arc
Z         = Close path
```

### Example: Cubic Bezier

```xml
<path d="M0,50 C25,0 75,100 100,50"/>
```

Points:
- P0: (0, 50) - start
- C1: (25, 0) - control 1
- C2: (75, 100) - control 2
- P1: (100, 50) - end

```json
{
  "ty": "sh",
  "ks": {
    "a": 0,
    "k": {
      "c": false,
      "v": [[0, 50], [100, 50]],
      "i": [[0, 0], [-25, 50]],     // C2 - P1 = (75-100, 100-50)
      "o": [[25, -50], [0, 0]]       // C1 - P0 = (25-0, 0-50)
    }
  }
}
```

## Helper Script: Parse SVG Path

```javascript
// Extract vertices from path d
function parsePathD(d) {
  // Simplified logic
  // 1. Split commands
  // 2. Track current point
  // 3. For C (cubic):
  //    outTangents[last] = [c1.x - current.x, c1.y - current.y]
  //    inTangents[next] = [c2.x - end.x, c2.y - end.y]
  // 4. Update current point
}
```

## Checklist for Conversion

- [ ] Extract viewBox for dimensions
- [ ] Convert each SVG element to corresponding shape
- [ ] Map hex colors to [R, G, B, A] arrays
- [ ] Apply transforms to groups
- [ ] Convert bezier paths with correct tangents
- [ ] Handle gradients if they exist
- [ ] Verify strokes and fills
- [ ] Validate final JSON structure

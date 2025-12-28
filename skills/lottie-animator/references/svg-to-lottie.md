# Conversion SVG a Lottie

Guia para convertir SVGs estaticos en animaciones Lottie.

## Proceso de Conversion

### Paso 1: Analizar el SVG

```xml
<svg viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="#3498db"/>
  <rect x="20" y="20" width="60" height="60" fill="#e74c3c"/>
  <path d="M10,10 L50,90 L90,10 Z" fill="#2ecc71"/>
</svg>
```

Extraer:
- **viewBox**: 0 0 100 100 → `w: 100, h: 100`
- **Elementos**: circle, rect, path
- **Atributos**: posiciones, colores, transformaciones

### Paso 2: Mapear Elementos

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

### Paso 3: Convertir Colores

```javascript
// SVG: fill="#3498db" o fill="rgb(52,152,219)"
// Lottie: [R, G, B, A] donde cada valor es 0-1

"#3498db" → [0.204, 0.596, 0.859, 1]

// Formula: hex_value / 255
// 0x34 = 52 → 52/255 = 0.204
// 0x98 = 152 → 152/255 = 0.596
// 0xdb = 219 → 219/255 = 0.859
```

## Conversion de Formas

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
          "i": [[0, 0], [0, 0], [0, 0]],        // In tangents (lineas = 0)
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

## Conversion de Paths Bezier

### SVG Path Commands

```
M x,y     = Move to (absoluto)
m dx,dy   = Move to (relativo)
L x,y     = Line to
l dx,dy   = Line to relativo
H x       = Horizontal line to
V y       = Vertical line to
C x1,y1 x2,y2 x,y = Cubic bezier
c         = Cubic bezier relativo
S x2,y2 x,y = Smooth cubic
Q x1,y1 x,y = Quadratic bezier
T x,y     = Smooth quadratic
A rx ry angle large-arc sweep x,y = Arc
Z         = Close path
```

### Ejemplo: Cubic Bezier

```xml
<path d="M0,50 C25,0 75,100 100,50"/>
```

Puntos:
- P0: (0, 50) - inicio
- C1: (25, 0) - control 1
- C2: (75, 100) - control 2
- P1: (100, 50) - fin

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

### Formulas de Tangentes

```
// Para cada segmento bezier:
// P0 → (C1, C2) → P1

out_tangent[i] = C1 - P0   // Tangente de salida
in_tangent[i+1] = C2 - P1  // Tangente de entrada al siguiente punto
```

## Transformaciones SVG

### Transform: translate

```xml
<g transform="translate(50, 30)">
```

```json
{
  "ty": "tr",
  "p": {"a": 0, "k": [50, 30]}
}
```

### Transform: scale

```xml
<g transform="scale(2, 1.5)">
```

```json
{
  "ty": "tr",
  "s": {"a": 0, "k": [200, 150]}  // * 100
}
```

### Transform: rotate

```xml
<g transform="rotate(45, 50, 50)">
```

```json
{
  "ty": "tr",
  "a": {"a": 0, "k": [50, 50]},   // Centro de rotacion
  "r": {"a": 0, "k": 45}          // Grados
}
```

### Transform combinado

```xml
<g transform="translate(100, 50) rotate(30) scale(0.5)">
```

```json
{
  "ty": "tr",
  "p": {"a": 0, "k": [100, 50]},
  "r": {"a": 0, "k": 30},
  "s": {"a": 0, "k": [50, 50]}
}
```

## Gradientes

### Linear Gradient

```xml
<linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
  <stop offset="0%" style="stop-color:#ff0000"/>
  <stop offset="100%" style="stop-color:#0000ff"/>
</linearGradient>
```

```json
{
  "ty": "gf",
  "t": 1,                              // 1 = linear
  "s": {"a": 0, "k": [0, 50]},         // Start point
  "e": {"a": 0, "k": [100, 50]},       // End point
  "g": {
    "p": 2,                            // Numero de stops
    "k": {
      "a": 0,
      "k": [
        0, 1, 0, 0,                    // offset 0%, R, G, B
        1, 0, 0, 1                     // offset 100%, R, G, B
      ]
    }
  },
  "o": {"a": 0, "k": 100}
}
```

### Radial Gradient

```xml
<radialGradient id="grad" cx="50%" cy="50%" r="50%">
```

```json
{
  "ty": "gf",
  "t": 2,                              // 2 = radial
  "s": {"a": 0, "k": [50, 50]},        // Center
  "e": {"a": 0, "k": [100, 50]},       // Edge point
  "h": {"a": 0, "k": 0},               // Highlight angle
  "a": {"a": 0, "k": 0},               // Highlight length
  "g": {
    "p": 2,
    "k": {"a": 0, "k": [0, 1, 0, 0, 1, 0, 0, 1]}
  }
}
```

## Stroke Properties

```xml
<path stroke="#000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
```

```json
{
  "ty": "st",
  "c": {"a": 0, "k": [0, 0, 0, 1]},
  "o": {"a": 0, "k": 100},
  "w": {"a": 0, "k": 2},
  "lc": 2,                             // 1=butt, 2=round, 3=square
  "lj": 2                              // 1=miter, 2=round, 3=bevel
}
```

## Opacity

```xml
<rect fill-opacity="0.5" opacity="0.8"/>
```

```json
// fill-opacity se aplica al fill
{
  "ty": "fl",
  "o": {"a": 0, "k": 50}
}

// opacity general se aplica al grupo
{
  "ty": "tr",
  "o": {"a": 0, "k": 80}
}
```

## Script de Ayuda: Parsear SVG

```javascript
// Extraer vertices de un path d
function parsePathD(d) {
  const commands = d.match(/[MLHVCSQTAZmlhvcsqtaz][^MLHVCSQTAZmlhvcsqtaz]*/g);
  const vertices = [];
  const inTangents = [];
  const outTangents = [];
  let current = [0, 0];

  commands.forEach(cmd => {
    const type = cmd[0];
    const args = cmd.slice(1).trim().split(/[\s,]+/).map(Number);

    switch(type) {
      case 'M':
        current = [args[0], args[1]];
        vertices.push(current);
        inTangents.push([0, 0]);
        outTangents.push([0, 0]);
        break;
      case 'L':
        current = [args[0], args[1]];
        vertices.push(current);
        inTangents.push([0, 0]);
        outTangents.push([0, 0]);
        break;
      case 'C':
        // Cubic bezier
        const c1 = [args[0], args[1]];
        const c2 = [args[2], args[3]];
        const end = [args[4], args[5]];

        // Out tangent del punto anterior
        outTangents[outTangents.length - 1] = [
          c1[0] - current[0],
          c1[1] - current[1]
        ];

        vertices.push(end);
        inTangents.push([
          c2[0] - end[0],
          c2[1] - end[1]
        ]);
        outTangents.push([0, 0]);

        current = end;
        break;
      case 'Z':
        // Mark as closed
        break;
    }
  });

  return {
    c: d.toUpperCase().includes('Z'),
    v: vertices,
    i: inTangents,
    o: outTangents
  };
}
```

## Checklist de Conversion

- [ ] Extraer viewBox para dimensiones
- [ ] Convertir cada elemento SVG a shape correspondiente
- [ ] Mapear colores hex a arrays [R, G, B, A]
- [ ] Aplicar transformaciones a grupos
- [ ] Convertir paths bezier con tangentes correctas
- [ ] Manejar gradientes si existen
- [ ] Verificar strokes y fills
- [ ] Validar estructura JSON final
- [ ] Probar en LottieFiles Preview

## Herramientas Utiles

- [SVGOMG](https://jakearchibald.github.io/svgomg/) - Optimizar SVG antes de convertir
- [SVG Path Editor](https://yqnn.github.io/svg-path-editor/) - Visualizar paths
- [LottieFiles](https://lottiefiles.com) - Previsualizar y validar

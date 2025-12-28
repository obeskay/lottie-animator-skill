# Estructura Lottie JSON Completa

Referencia completa de la especificacion Lottie para generacion de animaciones profesionales.

## Estructura Raiz

```json
{
  "v": "5.12.1",      // Version de Lottie
  "fr": 60,           // Frame rate (FPS)
  "ip": 0,            // In point (frame inicial)
  "op": 120,          // Out point (frame final)
  "w": 512,           // Ancho en pixels
  "h": 512,           // Alto en pixels
  "nm": "Animation",  // Nombre
  "ddd": 0,           // 3D deshabilitado
  "assets": [],       // Assets (imagenes, precomps)
  "layers": [],       // Capas de animacion
  "meta": {}          // Metadata opcional
}
```

## Tipos de Capas (ty)

| ty | Tipo | Descripcion |
|----|------|-------------|
| 0 | Precomp | Composicion anidada |
| 1 | Solid | Capa de color solido |
| 2 | Image | Capa de imagen |
| 3 | Null | Capa nula (control) |
| 4 | Shape | Capa de formas (SVG) |
| 5 | Text | Capa de texto |

## Capa Shape (ty: 4) - La mas usada

```json
{
  "ddd": 0,
  "ty": 4,
  "ind": 1,           // Indice de capa
  "nm": "Shape Layer",
  "sr": 1,            // Time stretch
  "st": 0,            // Start time
  "ip": 0,            // In point
  "op": 120,          // Out point
  "ks": {},           // Transform properties
  "ao": 0,            // Auto-orient (0 o 1)
  "shapes": []        // Array de shapes
}
```

## Transform Properties (ks)

```json
{
  "ks": {
    "a": {"a": 0, "k": [256, 256]},     // Anchor point
    "p": {"a": 0, "k": [256, 256]},     // Position
    "s": {"a": 0, "k": [100, 100]},     // Scale (%)
    "r": {"a": 0, "k": 0},              // Rotation (grados)
    "o": {"a": 0, "k": 100},            // Opacity (0-100)
    "sk": {"a": 0, "k": 0},             // Skew
    "sa": {"a": 0, "k": 0}              // Skew axis
  }
}
```

## Propiedad Animada vs Estatica

```json
// Estatica (a: 0)
{"a": 0, "k": [256, 256]}

// Animada (a: 1)
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
      "s": [256, 256]                   // End value (sin easing)
    }
  ]
}
```

## Tipos de Shapes

### Group (ty: "gr")
```json
{
  "ty": "gr",
  "nm": "Group",
  "it": [
    // Shapes hijos
    // Transform al final
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

### Path (ty: "sh") - Para SVGs
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

### Transform dentro de Group (ty: "tr")
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

## Conversion SVG Path a Lottie

### SVG Path Commands
```
M = moveto (absoluto)
m = moveto (relativo)
L = lineto
l = lineto relativo
C = cubic bezier
c = cubic bezier relativo
Q = quadratic bezier
Z = close path
```

### Mapeo a Lottie
```json
// SVG: <path d="M 0,0 C 25,0 75,100 100,100 Z"/>

{
  "ty": "sh",
  "ks": {
    "a": 0,
    "k": {
      "c": true,
      "v": [[0, 0], [100, 100]],
      "i": [[0, 0], [-25, 0]],      // In tangents (relativos a vertex)
      "o": [[25, 0], [0, 0]]        // Out tangents (relativos a vertex)
    }
  }
}
```

### Tangentes Bezier
- **v**: Vertices (puntos del path)
- **i**: In tangent = punto_control - vertex (relativo)
- **o**: Out tangent = punto_control - vertex (relativo)

Para lineas rectas, tangentes son `[0, 0]`.

## Estructura de Keyframe Completa

```json
{
  "t": 0,                    // Frame number
  "s": [0],                  // Start value (array)
  "h": 0,                    // Hold (0=interpolate, 1=hold)
  "o": {                     // Out tangent (salida)
    "x": [0.33],
    "y": [0]
  },
  "i": {                     // In tangent (entrada)
    "x": [0.67],
    "y": [1]
  }
}
```

### Valores Especiales
- **h: 1**: Hold keyframe (sin interpolacion)
- Sin `o`/`i`: Ultimo keyframe (no necesita easing)

## Presets de Transicion

Basado en Advanced Effects:

```json
// Linear
"o": {"x": [0.33], "y": [0.33]},
"i": {"x": [0.67], "y": [0.67]}

// Ease (suave)
"o": {"x": [0.33], "y": [0]},
"i": {"x": [0.67], "y": [1]}

// Fast (rapido)
"o": {"x": [0.17], "y": [0.33]},
"i": {"x": [0.83], "y": [0.67]}

// Overshoot (rebasa)
"o": {"x": [0.67], "y": [-0.33]},
"i": {"x": [0.33], "y": [1.33]}
```

## Assets

### Imagen Embebida
```json
{
  "assets": [
    {
      "id": "image_0",
      "w": 512,
      "h": 512,
      "e": 1,                        // Embedded (1=si, 0=no)
      "u": "",                       // Path vacio si embedded
      "p": "data:image/png;base64,..." // Base64 data
    }
  ]
}
```

### Imagen Externa
```json
{
  "assets": [
    {
      "id": "image_0",
      "w": 512,
      "h": 512,
      "e": 0,
      "u": "images/",               // Directorio
      "p": "logo.png"               // Nombre archivo
    }
  ]
}
```

### Precomposicion
```json
{
  "assets": [
    {
      "id": "comp_0",
      "nm": "Precomp",
      "layers": []                  // Capas de la precomp
    }
  ]
}
```

## Efectos Comunes

### Trim Path
```json
{
  "ty": "tm",
  "nm": "Trim Path",
  "s": {"a": 0, "k": 0},    // Start (%)
  "e": {"a": 0, "k": 100},  // End (%)
  "o": {"a": 0, "k": 0}     // Offset (grados)
}
```

### Repeater
```json
{
  "ty": "rp",
  "nm": "Repeater",
  "c": {"a": 0, "k": 3},    // Copies
  "o": {"a": 0, "k": 0},    // Offset
  "tr": {                    // Transform per copy
    "a": {"a": 0, "k": [0, 0]},
    "p": {"a": 0, "k": [50, 0]},
    "s": {"a": 0, "k": [100, 100]},
    "r": {"a": 0, "k": 0},
    "so": {"a": 0, "k": 100},
    "eo": {"a": 0, "k": 100}
  }
}
```

## Gradientes

### Gradient Fill
```json
{
  "ty": "gf",
  "nm": "Gradient Fill",
  "t": 1,                           // Type (1=linear, 2=radial)
  "s": {"a": 0, "k": [0, 256]},     // Start point
  "e": {"a": 0, "k": [512, 256]},   // End point
  "g": {
    "p": 3,                          // Num color stops
    "k": {
      "a": 0,
      "k": [
        0, 1, 0, 0,                  // pos, R, G, B
        0.5, 0, 1, 0,
        1, 0, 0, 1
      ]
    }
  }
}
```

## Mascaras

```json
{
  "masksProperties": [
    {
      "nm": "Mask",
      "mode": "a",                   // a=add, s=subtract, i=intersect
      "pt": {                        // Path
        "a": 0,
        "k": {"c": true, "v": [], "i": [], "o": []}
      },
      "o": {"a": 0, "k": 100},       // Opacity
      "x": {"a": 0, "k": 0}          // Expansion
    }
  ]
}
```

## Validacion

### Checklist de Estructura
- [ ] `v` version presente
- [ ] `fr` framerate > 0
- [ ] `op` > `ip`
- [ ] `w` y `h` > 0
- [ ] `layers` es array
- [ ] Cada layer tiene `ty` valido
- [ ] Keyframes ordenados por `t` ascendente
- [ ] Ultimo keyframe no tiene `o`/`i`

### Errores Comunes
1. **Tangentes fuera de rango**: x debe estar entre 0-1
2. **Assets faltantes**: Verificar `refId` existe
3. **Keyframes desordenados**: Ordenar por `t`
4. **Path sin cerrar**: `c: false` si es abierto

## Referencias
- [Lottie Docs](https://lottiefiles.github.io/lottie-docs/)
- [Lottie Spec](https://lottie.github.io/lottie-spec/)
- [LottieFiles Viewer](https://lottiefiles.com/preview)

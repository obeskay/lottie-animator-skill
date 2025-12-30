# Professional Lottie Animation Techniques

Técnicas avanzadas extraídas del análisis de animaciones profesionales (Running Cat, etc.).

## 1. Frame-by-Frame Animation (Sprite Sheet Style)

La técnica más profesional para animaciones de personajes complejos.

### Concepto

En lugar de animar propiedades continuamente, creas **múltiples "poses"** que aparecen/desaparecen en secuencia.

```
Frame 0-6:   Pose 1 (visible)
Frame 6-12:  Pose 2 (visible)
Frame 12-18: Pose 3 (visible)
...
```

### Estructura JSON

```json
{
  "layers": [
    {
      "nm": "Cat Pose 1",
      "ip": 0,    // In Point: aparece frame 0
      "op": 6,    // Out Point: desaparece frame 6
      "shapes": [/* Gato en pose 1 */]
    },
    {
      "nm": "Cat Pose 2",
      "ip": 6,    // Aparece frame 6
      "op": 12,   // Desaparece frame 12
      "shapes": [/* Gato en pose 2 */]
    },
    {
      "nm": "Cat Pose 3",
      "ip": 12,
      "op": 18,
      "shapes": [/* Gato en pose 3 */]
    }
  ]
}
```

### Ventajas

- **Libertad total**: Cada pose puede tener formas completamente diferentes
- **No requiere mismo vertex count**: A diferencia del morphing
- **Más orgánico**: Mejor para animaciones de personajes complejos
- **Profesional**: Técnica usada en animaciones de alta calidad

### Cuándo Usarla

- Walk cycles de personajes
- Run cycles
- Animaciones con cambios drásticos de forma
- Cuando el morphing produce resultados feos

### Cálculo de Frames

```
Total Frames = (Número de Poses) × (Frames por Pose)
Duración (segundos) = Total Frames / Frame Rate

Ejemplo Running Cat:
- 6 poses × 6 frames = 36 frames total
- 36 frames / 60 fps = 0.6 segundos de loop
```

---

## 2. Parenting Hierarchy (Bone System)

Sistema de jerarquía padre-hijo para animaciones coordinadas.

### Concepto

Un layer "parent" controla la posición/rotación de múltiples "children".

```
Shadow (Parent Layer 14)
├── Head (child)
├── Body (child)
├── Ear Inner (child)
├── Eye (child)
├── Nose (child)
└── ...13 total children
```

### Estructura JSON

```json
{
  "layers": [
    {
      "ind": 14,
      "nm": "Shadow",
      "ty": 4,
      "ks": {
        "p": {"a": 0, "k": [340, 195, 0]}  // Posición del parent
      }
    },
    {
      "ind": 1,
      "nm": "Head",
      "parent": 14,  // <-- Referencia al parent
      "ty": 4,
      "ks": {
        "p": {"a": 0, "k": [88, -84, 0]}  // Posición RELATIVA al parent
      }
    },
    {
      "ind": 2,
      "nm": "Eye",
      "parent": 14,
      "ty": 4,
      "ks": {
        "p": {"a": 0, "k": [64, -86, 0]}
      }
    }
  ]
}
```

### Usos Prácticos

1. **Sombra como Parent**: Mueve la sombra = mueve todo el personaje
2. **Cuerpo como Parent**: Mueve el cuerpo = cabeza y extremidades siguen
3. **Brazo Upper como Parent**: Rota hombro = antebrazo y mano rotan

### Beneficios

- Mueve un layer → todos los children siguen
- Fácil de coordinar animaciones complejas
- Reduce keyframes necesarios

---

## 3. Stroke + Fill Combination (Outline Style)

Estilo visual con contornos definidos.

### Concepto

Cada shape tiene **fill (relleno) + stroke (contorno)**.

```json
{
  "shapes": [
    {
      "ty": "gr",
      "it": [
        {"ty": "sh", "ks": {...}},  // Path
        {"ty": "st",                  // Stroke (contorno)
          "c": {"a": 0, "k": [0.259, 0.153, 0.141, 1]},  // Dark brown
          "w": {"a": 0, "k": 1},      // 1px width
          "lc": 2,                     // Round line cap
          "lj": 2                      // Round line join
        },
        {"ty": "fl",                  // Fill (relleno)
          "c": {"a": 0, "k": [0.302, 0.604, 0.816, 1]}   // Blue
        },
        {"ty": "tr", ...}
      ]
    }
  ]
}
```

### Propiedades del Stroke

| Propiedad | Valor | Descripción |
|-----------|-------|-------------|
| `lc` (lineCap) | 1 | Butt (cortado) |
| `lc` | 2 | Round (redondeado) |
| `lc` | 3 | Square (cuadrado) |
| `lj` (lineJoin) | 1 | Miter (punta) |
| `lj` | 2 | Round (redondeado) |
| `lj` | 3 | Bevel (biselado) |

### Paleta de Colores Profesional (Running Cat)

```json
{
  "body_fill": [0.302, 0.604, 0.816, 1],       // RGB(77, 154, 208) - Blue
  "outline": [0.259, 0.153, 0.141, 1],          // RGB(66, 39, 36) - Dark brown
  "eye_white": [0.902, 0.976, 1.0, 1],          // RGB(230, 249, 255) - Near white
  "ear_inner": [0.941, 0.757, 0.686, 1],        // RGB(240, 193, 175) - Skin
  "shadow": [0.608, 0.706, 0.878, 1]            // RGB(155, 180, 224) - Light blue
}
```

---

## 4. Bezier Paths con Tangentes

Paths suaves usando curvas bezier.

### Estructura de Path

```json
{
  "ty": "sh",
  "ks": {
    "a": 0,
    "k": {
      "c": true,           // Closed path
      "v": [[0, 0], [100, 0], [100, 100], [0, 100]],  // Vertices
      "i": [[0, -10], [10, 0], [0, 10], [-10, 0]],    // In tangents
      "o": [[10, 0], [0, 10], [-10, 0], [0, -10]]     // Out tangents
    }
  }
}
```

### Tangentes

- `"i"` (in tangent): Control point ENTRANDO al vertex
- `"o"` (out tangent): Control point SALIENDO del vertex
- Valores son **RELATIVOS** al vertex
- `[0, 0]` = sin curva (línea recta)

---

## 5. Pre-compositions (Assets)

Agrupar animaciones complejas en composiciones reutilizables.

### Estructura

```json
{
  "assets": [
    {
      "id": "comp_0",
      "nm": "Cat Animation",
      "fr": 60,
      "layers": [/* 82 layers del gato */]
    }
  ],
  "layers": [
    {
      "ty": 0,           // Type 0 = Precomp reference
      "refId": "comp_0", // Reference to asset
      "nm": "Cat",
      "ip": 0,
      "op": 36
    }
  ]
}
```

### Beneficios

- Reutilizar animaciones
- Organizar layers complejos
- Aplicar transformaciones al grupo completo

---

## 6. Timing Profesional

### Frame Rate y Duración

| Tipo | FPS | Frames | Duración | Uso |
|------|-----|--------|----------|-----|
| Loop rápido | 60 | 36 | 0.6s | Run cycles |
| Loop normal | 30 | 24 | 0.8s | Walk cycles |
| Loop lento | 30 | 60 | 2.0s | Idle animations |
| Transición | 60 | 45 | 0.75s | Entrances |

### Estructura de Loop Perfecto

```
Frame 0: Estado A
...
Frame N-1: Estado A' (casi igual a A)
Frame N: [Vuelve a Frame 0]
```

**Clave**: El último frame (op) NO se renderiza, solo marca el punto de loop.

---

## 7. Layer Order = Z-Depth

El orden de los layers en el array determina la profundidad visual.

```json
{
  "layers": [
    {"ind": 1, "nm": "Background"},  // Más atrás (renderiza primero)
    {"ind": 2, "nm": "Character"},
    {"ind": 3, "nm": "Foreground"}   // Más adelante (renderiza último)
  ]
}
```

**Nota**: Layers con `ind` más alto se renderizan ENCIMA.

---

## Ejemplo Completo: Walk Cycle Profesional

```json
{
  "v": "5.12.1",
  "fr": 30,
  "ip": 0,
  "op": 24,
  "w": 200,
  "h": 200,
  "nm": "Character Walk",
  "ddd": 0,
  "assets": [],
  "layers": [
    // Shadow (Parent for all poses)
    {
      "ind": 1,
      "ty": 4,
      "nm": "Shadow",
      "ks": {
        "o": {"a": 0, "k": 30},
        "p": {"a": 0, "k": [100, 180, 0]},
        "s": {"a": 1, "k": [
          {"t": 0, "s": [100, 100, 100]},
          {"t": 6, "s": [95, 100, 100]},
          {"t": 12, "s": [100, 100, 100]},
          {"t": 18, "s": [95, 100, 100]},
          {"t": 24, "s": [100, 100, 100]}
        ]}
      },
      "shapes": [
        {
          "ty": "gr",
          "it": [
            {"ty": "el", "s": {"a": 0, "k": [60, 12]}, "p": {"a": 0, "k": [0, 0]}},
            {"ty": "fl", "c": {"a": 0, "k": [0.2, 0.2, 0.2, 1]}},
            {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [100, 100]}}
          ]
        }
      ],
      "ip": 0,
      "op": 24
    },
    // Pose 1 (frames 0-6)
    {
      "ind": 2,
      "ty": 4,
      "nm": "Pose 1",
      "parent": 1,
      "ip": 0,
      "op": 6,
      "shapes": [/* Character pose 1 shapes */]
    },
    // Pose 2 (frames 6-12)
    {
      "ind": 3,
      "ty": 4,
      "nm": "Pose 2",
      "parent": 1,
      "ip": 6,
      "op": 12,
      "shapes": [/* Character pose 2 shapes */]
    },
    // Pose 3 (frames 12-18)
    {
      "ind": 4,
      "ty": 4,
      "nm": "Pose 3",
      "parent": 1,
      "ip": 12,
      "op": 18,
      "shapes": [/* Character pose 3 shapes */]
    },
    // Pose 4 (frames 18-24)
    {
      "ind": 5,
      "ty": 4,
      "nm": "Pose 4",
      "parent": 1,
      "ip": 18,
      "op": 24,
      "shapes": [/* Character pose 4 shapes */]
    }
  ]
}
```

---

## Checklist de Animación Profesional

- [ ] Definir número de poses para frame-by-frame
- [ ] Calcular timing: poses × frames_por_pose / fps = duración
- [ ] Establecer jerarquía parent-child
- [ ] Usar stroke + fill para estilo outline
- [ ] Paleta de colores coherente (max 5-6 colores)
- [ ] Shadow pulsa con los pasos
- [ ] Loop seamless (frame 0 = estado similar a frame final)
- [ ] Testar en LottieFiles Preview

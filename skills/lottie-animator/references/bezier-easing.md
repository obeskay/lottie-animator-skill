# Curvas Bezier y Easing Functions

Referencia completa de curvas bezier para animaciones Lottie profesionales.

## Fundamentos

Las curvas bezier en Lottie controlan la interpolacion entre keyframes:
- **Eje X**: Tiempo (0 = keyframe actual, 1 = siguiente keyframe)
- **Eje Y**: Valor interpolado (0 = valor actual, 1 = valor siguiente)

### Estructura en JSON

```json
{
  "t": 0,           // Frame del keyframe
  "s": [0],         // Valor inicial
  "o": {            // OUT - salida del keyframe actual
    "x": [0.33],
    "y": [0]
  },
  "i": {            // IN - entrada al siguiente keyframe
    "x": [0.67],
    "y": [1]
  }
}
```

## Easing Presets

### Ease Out (Desaceleracion)
Comienza rapido, termina suave. Ideal para **entradas**.

```json
// Ease Out Quad
"o": {"x": [0.25], "y": [0.46]},
"i": {"x": [0.45], "y": [0.94]}

// Ease Out Cubic (Recomendado)
"o": {"x": [0.33], "y": [0]},
"i": {"x": [0.67], "y": [1]}

// Ease Out Quart
"o": {"x": [0.165], "y": [0.84]},
"i": {"x": [0.44], "y": [1]}

// Ease Out Expo
"o": {"x": [0.19], "y": [1]},
"i": {"x": [0.22], "y": [1]}
```

### Ease In (Aceleracion)
Comienza suave, termina rapido. Ideal para **salidas**.

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

### Ease In Out (Simetrico)
Suave en ambos extremos. Ideal para **loops** y **transiciones**.

```json
// Ease In Out Quad
"o": {"x": [0.455], "y": [0.03]},
"i": {"x": [0.515], "y": [0.955]}

// Ease In Out Cubic (Profesional)
"o": {"x": [0.645], "y": [0.045]},
"i": {"x": [0.355], "y": [1]}

// Ease In Out Quart
"o": {"x": [0.76], "y": [0]},
"i": {"x": [0.24], "y": [1]}

// Ease In Out Expo
"o": {"x": [1], "y": [0]},
"i": {"x": [0], "y": [1]}
```

### Bounce y Elastic
Movimientos con rebote. Ideal para **atencion** y **jugueton**.

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

### Spring (Resorte)
Movimiento organico tipo resorte.

```json
// Spring Light
"o": {"x": [0.5], "y": [1.2]},
"i": {"x": [0.5], "y": [0.9]}

// Spring Heavy
"o": {"x": [0.35], "y": [1.7]},
"i": {"x": [0.65], "y": [0.8]}
```

## Guia Visual

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

## Por Caso de Uso

### UI/UX Moderno
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
// Cinematico Suave
"o": {"x": [0.7], "y": [0]},
"i": {"x": [0.3], "y": [1]}

// Dramatico
"o": {"x": [0.9], "y": [0]},
"i": {"x": [0.1], "y": [1]}
```

### Logos Corporativos
```json
// Profesional Controlado
"o": {"x": [0.25], "y": [0.1]},
"i": {"x": [0.25], "y": [1]}

// Elegante
"o": {"x": [0.42], "y": [0]},
"i": {"x": [0.58], "y": [1]}
```

### Iconos y Micro-interacciones
```json
// Rapido y Snappy
"o": {"x": [0.2], "y": [0]},
"i": {"x": [0], "y": [1]}

// Rebote Sutil
"o": {"x": [0.34], "y": [1.2]},
"i": {"x": [0.64], "y": [1]}
```

## Valores Extremos

### Overshoot (Sobrepasar)
Cuando `y > 1`, el valor sobrepasa el destino antes de asentarse:

```json
// Overshoot 20%
"o": {"x": [0.2], "y": [0]},
"i": {"x": [0.5], "y": [1.2]}

// Overshoot Dramatico 50%
"o": {"x": [0.1], "y": [0]},
"i": {"x": [0.4], "y": [1.5]}
```

### Undershoot (Retroceso)
Cuando `y < 0` al inicio, retrocede antes de avanzar:

```json
// Anticipation (Preparacion)
"o": {"x": [0.5], "y": [-0.1]},
"i": {"x": [0.5], "y": [1]}
```

## Combinaciones Multi-Keyframe

### Bounce Realista (3 keyframes)
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

## Herramientas

- [Cubic Bezier Editor](https://cubic-bezier.com/)
- [Easings.net](https://easings.net/)
- [Lottie Preview](https://lottiefiles.com/preview)

## Tips

1. **Consistencia**: Usa el mismo easing en animaciones relacionadas
2. **Duracion**: Easings suaves necesitan mas frames para apreciarse
3. **Overshoots**: Usarlos con moderacion, max 20-30% para profesional
4. **Loops**: Siempre usar ease in-out simetrico para seamless loops
5. **Testing**: Probar a 0.5x y 2x velocidad para validar suavidad

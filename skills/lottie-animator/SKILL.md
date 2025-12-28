---
name: lottie-animator
description: |
  Genera animaciones Lottie profesionales desde SVGs estaticos. Reemplaza After Effects para motion graphics.
  Usa cuando el usuario pida: animar logo, crear lottie, animacion svg, motion graphics, wiggle animation,
  bounce effect, rotate animation, pulse effect, entrance animation, loading animation, loop animation.
  Soporta curvas bezier avanzadas, easing functions profesionales, y exportacion a JSON/GIF/MP4.
allowed-tools: Read, Write, Bash, Glob, Grep
---

# Lottie Animator - SVG to Motion Graphics

Skill profesional para crear animaciones Lottie avanzadas desde SVGs, eliminando la necesidad de After Effects.

## Cuando Activar

Activa este skill cuando el usuario solicite:
- Animar un logo o icono SVG
- Crear motion graphics o animaciones
- Generar archivos Lottie JSON
- Efectos: wiggle, bounce, rotate, pulse, fade, scale, morph
- Animaciones de entrada, loop, loading, o transiciones
- Reemplazar workflow de After Effects

## Workflow Principal

### Fase 1: Filosofia de Movimiento (30 segundos)

**OBLIGATORIO** antes de cualquier codigo. Define:

1. **Personalidad de marca**: Profesional, jugueton, elegante, energico
2. **Respuesta emocional**: Confianza, emocion, calma, urgencia
3. **Metafora de movimiento**: Fluido como agua, solido como roca, ligero como aire

```
Ejemplo: "Logo fintech → profesional + confianza → movimiento preciso y controlado"
Ejemplo: "App musica → creativo + energia → organico con pulsos ritmicos"
```

### Fase 2: Analisis del SVG (30 segundos)

Antes de animar, analiza:

1. **Estructura**: Cuantos elementos? Grupos? Paths?
2. **Jerarquia**: Que elementos son principales vs secundarios?
3. **Oportunidades**: Que partes pueden animarse independientemente?

```bash
# Analizar SVG
cat logo.svg | grep -E '<(path|g|rect|circle|ellipse)' | head -20
```

### Fase 3: Seleccion de Tipo de Movimiento

| Tipo | Keyframes | FPS | Duracion | Uso |
|------|-----------|-----|----------|-----|
| Corporativo | 8-12 | 30 | 1.5-2s | B2B, finanzas, legal |
| Organico | 25-45 | 60 | 2-3s | Audio, musica, creativos |
| Bold/Atencion | 15-25 | 60 | 0.8-1.5s | Startups, marketing |
| Cinematico | 50-120 | 60 | 3-5s | Lujo, entretenimiento |

### Fase 4: Crear Lottie JSON

Ver: [references/lottie-structure.md](references/lottie-structure.md)

**Estructura base:**
```json
{
  "v": "5.12.1",
  "fr": 60,
  "ip": 0,
  "op": 120,
  "w": 512,
  "h": 512,
  "nm": "Logo Animation",
  "ddd": 0,
  "assets": [],
  "layers": []
}
```

### Fase 5: Aplicar Easing con Curvas Bezier

Ver: [references/bezier-easing.md](references/bezier-easing.md)

**Easings profesionales:**
```json
// Ease Out Cubic - Entrada suave
"o": {"x": [0.33], "y": [0]},
"i": {"x": [0.67], "y": [1]}

// Ease In Out Quart - Profesional
"o": {"x": [0.76], "y": [0]},
"i": {"x": [0.24], "y": [1]}

// Bounce - Jugueton
"o": {"x": [0.34], "y": [1.56]},
"i": {"x": [0.64], "y": [1]}
```

### Fase 6: Validar y Exportar

```bash
# Validar estructura
python3 -c "import json; json.load(open('animation.json'))"

# Preview en navegador
echo "Abrir en: https://lottiefiles.com/preview"
```

## Tipos de Animacion

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

## Propiedades Animables

| Propiedad | Codigo | Tipo | Descripcion |
|-----------|--------|------|-------------|
| Posicion | `p` | [x, y] | Movimiento en espacio |
| Escala | `s` | [x, y] | Tamano relativo (100 = original) |
| Rotacion | `r` | grados | Rotacion en eje Z |
| Opacidad | `o` | 0-100 | Transparencia |
| Anchor | `a` | [x, y] | Punto de transformacion |
| Skew | `sk` | grados | Inclinacion |

## Patrones de Animacion Comunes

### Entrance (Entrada)
1. Fade + Scale desde 0
2. Slide desde fuera del viewport
3. Reveal con mascara

### Loop (Bucle)
1. Pulse (scale 100 → 105 → 100)
2. Wiggle (rotation -2 → 2 → -2)
3. Float (position Y offset ciclico)

### Attention (Atencion)
1. Bounce agresivo
2. Shake horizontal
3. Flash de opacidad

## Errores Comunes

| Error | Causa | Solucion |
|-------|-------|----------|
| Animacion no loop | `ip` != 0 o ultimo keyframe != `op` | Asegurar keyframe final = inicial |
| Movimiento rigido | Sin easing | Agregar curvas bezier `i`/`o` |
| Saltos bruscos | Keyframes muy separados | Agregar keyframes intermedios |
| Archivo muy grande | Assets embebidos | Usar referencias externas |

## Referencias

- [Estructura Lottie JSON](references/lottie-structure.md)
- [Curvas Bezier y Easing](references/bezier-easing.md)
- [Ejemplos de Animaciones](references/examples.md)
- [Documentacion Oficial Lottie](https://lottiefiles.github.io/lottie-docs/)

## Checklist Final

- [ ] Filosofia de movimiento definida
- [ ] SVG analizado y optimizado
- [ ] Tipo de animacion seleccionado
- [ ] Keyframes con easing apropiado
- [ ] Loop seamless (si aplica)
- [ ] JSON validado
- [ ] Preview verificado

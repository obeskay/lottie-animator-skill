# Lottie Tools, Platforms & Ecosystem Integration

This document defines the engineering standards for selecting creation tools, optimizing vector delivery using compressed formats, and integrating cross-platform Lottie players.

---

## 1. Creation & Motion Design Platforms

Creating standard-compliant Lotties requires choosing the correct environment and avoiding features that cause translation errors.

### The Creator Workflow Matrix

| Tool | Export Capability | Web Compliance | Best Use Case |
| :--- | :--- | :--- | :--- |
| **After Effects + Bodymovin** | Full JSON / `.lottie` | High (excluding expressions) | Complex multi-layer rigs, particle systems, cinematic paths. |
| **LottieLab / Lottie Creator** | Web Native JSON | $100\%$ Compliant | Collaborative vector animations, micro-interactions, edits. |
| **Keyshape (macOS)** | Clean JSON, SVG, CSS | High | Light vector wiggles, icon morphs, clean raw curves. |
| **Haiku Animator** | Direct Web Components | High | Programmatic state transitions and interactive UI loops. |

> [!WARNING]
> When exporting from After Effects, **NEVER** use After Effects Expressions or advanced effects (like Gaussian Blur or Drop Shadow). The `lottie-web` canvas and SVG renderers must parse these dynamically, causing heavy CPU bottlenecks and frame drops. Convert all expressions to baked keyframes before export.

---

## 2. DotLottie (.lottie) File Formats & Compression

For production web and mobile apps, shipping raw Lottie JSON files can lead to excessive bandwidth usage and multi-request roundtrips for animations containing image assets.

### DotLottie Structure

A `.lottie` file is an optimized, zipped container conforming to the DotLottie specification.

```
my-animation.lottie (ZIP Container)
├── manifest.json            # Defines IDs, loop properties, and settings
├── animations/
│   └── animation_id.json    # Standard compressed Lottie JSON
└── images/
    ├── img_0.png            # Inlined, optimized static images
    └── img_1.jpg
```

### Bandwidth & Performance Advantages

1. **ZIP Compression**: Reduces raw JSON size by **$70\%$ to $80\%$** automatically, outperforming gzip/brotli transport levels.
2. **Resource Consolidation**: Bundles standard assets (Lottie JSON, raster PNGs, sound files) into a single archive, eliminating CORS issues and multiple network requests.
3. **Multi-Animation Bundling**: Allows switching animations (e.g. state changes like `hover`, `active`, `success`) instantly without loading separate assets.

### Loading a `.lottie` File on Web

```javascript
import { DotLottie } from '@lottiefiles/dotlottie-web';

// High-performance canvas-based DotLottie instance
const dotLottie = new DotLottie({
  autoplay: true,
  loop: true,
  canvas: document.getElementById('lottie-canvas'),
  src: 'assets/hero-loop.lottie',
});
```

---

## 3. Cross-Platform Player Architectures

To ensure your web and mobile applications maintain consistent visual pacing and timing:

### 1. Web (`lottie-web` / `@lottiefiles/dotlottie-web`)
*   **Renderer**: SVG or Canvas (select Canvas for viewports larger than 500px).
*   **Best Practice**: Defer loading of non-visible animations. Use `IntersectionObserver` to trigger `play()` and `pause()`.

### 2. iOS (`lottie-ios`)
*   **Engine**: CoreAnimation engine (default in iOS 16+) or main-thread rendering.
*   **Best Practice**: Always set the rendering engine to `.coreAnimation` to offload work entirely to the GPU, keeping the main thread free.
    ```swift
    let animationView = LottieAnimationView(name: "panda-loader")
    animationView.configuration.renderingEngine = .coreAnimation
    ```

### 3. Android (`lottie-android`)
*   **Best Practice**: Enable hardware acceleration globally on the Lottie view.
    ```xml
    <com.airbnb.lottie.LottieAnimationView
        android:id="@+id/animation_view"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        app:lottie_rawRes="@raw/panda_loader"
        app:lottie_renderMode="hardware" />
    ```

---

## 4. Engineering Validation & Efficiency Audit

Before deploying a Lottie asset to staging or production, run this strict verification checklist to ensure it is effective and battery-efficient:

```
[ ] File Size: Is the modular JSON under 250KB? (Or .lottie under 80KB?)
[ ] Renderer Choice: If the animation is fullscreen or covers >50% viewport, is the Canvas engine selected?
[ ] GPU Layer: Is 'will-change: transform' or 'transform: translate3d(0,0,0)' forced on the CSS parent?
[ ] Mask Count: Are shapes with mattes/masks limited to under 3 per layer? (Excessive masking chokes GPU clip paths).
[ ] Keyframe Density: Are there only keyframes where spatial values change, or did After Effects bake every frame?
[ ] Idle Pausing: Are calculations fully paused when the container is scrolled off-screen?
```

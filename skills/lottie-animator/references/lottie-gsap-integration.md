# Lottie & GSAP ScrollTrigger Integration

This document defines the architecture and integration patterns for building native-quality, immersive web experiences using Lottie-Web combined with GSAP (GreenSock Animation Platform) and ScrollTrigger.

---

## 1. Core Integration Patterns (Scroll-Linked Playback)

Tying a Lottie animation's playhead directly to the user's scroll position creates an immersive, responsive feel. The most robust way to achieve this is by driving a virtual progress tween with GSAP and using its `onUpdate` callback to update the Lottie frame.

### Pinned Scroll-Scrub Pattern

This pattern pins the canvas or SVG container in the viewport for a set scroll distance, scrubbing the Lottie frame elastically.

```javascript
// Register the ScrollTrigger plugin once
gsap.registerPlugin(ScrollTrigger);

// Initialize the Lottie animation paused
const animation = lottie.loadAnimation({
  container: document.getElementById('lottie-fullscreen-container'),
  renderer: 'canvas', // Use canvas for large full-screen viewport rendering
  loop: false,
  autoplay: false,
  path: 'assets/hero-animation.json'
});

animation.addEventListener('DOMLoaded', () => {
  const totalFrames = animation.totalFrames - 1;

  // Create a virtual tween driving the frame index
  const playhead = { frame: 0 };

  gsap.to(playhead, {
    frame: totalFrames,
    ease: "none", // Must be none for linear 1:1 scroll mapping
    scrollTrigger: {
      trigger: ".scroll-story-section",
      start: "top top",      // Pin when top of section hits top of viewport
      end: "+=3000",         // Scrub for 3000px of scroll height
      pin: true,             // Pin the container
      scrub: 1.5,            // 1.5 seconds of elastic catch-up lag for smooth rendering
      onUpdate: (self) => {
        // Direct frame scrub based on tween progress
        animation.goToAndStop(playhead.frame, true);
      }
    }
  });
});
```

---

## 2. High-Performance Full-Screen Architectures

Rendering a Lottie animation full-screen requires strict memory and repaint optimization to maintain 60fps/120fps on desktop and mobile devices.

### SVG vs. Canvas Rendering Selection

| Metric | SVG Renderer (`renderer: 'svg'`) | Canvas Renderer (`renderer: 'canvas'`) |
| :--- | :--- | :--- |
| **Node Count** | Creates DOM nodes for every shape. High memory footprint. | Single `<canvas>` DOM node. Static memory footprint. |
| **CPU/GPU Load** | High CSS layout recalculations on reflows. | Pure GPU-accelerated pixel copying. |
| **Best For** | Small UI icons, loaders, vector sharp lines under 400px. | Full-screen backgrounds, complex character scenes, particles. |
| **Interactive** | Individual nodes can be styled/hovered with CSS. | Cannot style internal elements directly. |

> [!IMPORTANT]
> Always use `renderer: 'canvas'` for full-screen animations. An SVG with 200+ nodes scaling to 100vh will trigger massive layout recalculations, choking the main thread.

### Viewport and Off-Screen Optimization

If a full-screen animation scrolls out of view, the browser continues updating the canvas or SVG, causing unnecessary repaints. You must pause calculation cycles when off-screen.

```javascript
// Build a standalone ScrollTrigger to monitor viewport presence
ScrollTrigger.create({
  trigger: ".scroll-story-section",
  start: "top bottom", // Starts when top of section enters viewport bottom
  end: "bottom top",    // Ends when bottom of section exits viewport top
  onToggle: (self) => {
    if (self.isActive) {
      // Resume Lottie updates if the section is inside the active viewport
      animation.play();
    } else {
      // Pause Lottie completely when offscreen to free CPU cycles
      animation.pause();
    }
  }
});
```

---

## 3. Web Experiences That Feel Native (Micro-Physics)

To elevate standard scrolling into an experience that matches native macOS/iOS fluid feel, apply physical constraints, spring wiggles, and interactive magnetic forces.

### Spring-Deceleration Mouse Parallax

Instead of letting a Lottie layer tilt rigidly, apply a spring ease that interpolates coordinates toward mouse offsets, creating organic secondary action.

```javascript
const targetCoords = { x: 0, y: 0 };
const currentCoords = { x: 0, y: 0 };
const springStrength = 0.08; // Lower = looser/softer spring movement

document.addEventListener('mousemove', (e) => {
  const { clientX, clientY } = e;
  const { innerWidth, innerHeight } = window;
  
  // Normalize coordinates from -1 to 1
  targetCoords.x = (clientX - innerWidth / 2) / (innerWidth / 2);
  targetCoords.y = (clientY - innerHeight / 2) / (innerHeight / 2);
});

function animateParallaxLoop() {
  // Spring interpolation formula: current = current + (target - current) * strength
  currentCoords.x += (targetCoords.x - currentCoords.x) * springStrength;
  currentCoords.y += (targetCoords.y - currentCoords.y) * springStrength;
  
  // Bind interpolated coordinates to a Lottie Layer's transform or rotation property
  // Example: deflecting the head layer Y-axis or rotation slightly
  if (animation.isLoaded) {
    const headLayer = animation.renderer.elements[3]; // Head element index
    if (headLayer && headLayer.finalTransform) {
      // Manually deflect the Lottie element matrix
      headLayer.finalTransform.mProps.r.setValue(currentCoords.x * 8); // Rotate up to 8 deg
    }
  }
  
  requestAnimationFrame(animateParallaxLoop);
}

// Start the physics loop
animateParallaxLoop();
```

---

## 4. Architectural Rules for Cinematic Web Pages

To guarantee smooth performance on multi-section cinematic landing pages:

1. **Lazy Keyframe Compile**: Initialize Lottie-Web with `lazy: true` to defer path generation until the first render cycle.
2. **Asset Budgets**: Keep Lottie JSON files under `250KB`. If a file exceeds `500KB`, split it into multiple smaller modular loops or compress the vector paths.
3. **Hardware Acceleration**: Force GPU layer creation on containers using `transform: translate3d(0, 0, 0);` and `will-change: transform;` in CSS.
4. **Debounced Resizing**: Call `animation.resize()` within a debounced resize handler (at least `150ms`) to avoid blocking browser resizing reflows.
5. **Frame Pre-Caching**: Enable Lottie-Web's frame caching for scrubbed animations to prevent seek stuttering:
   ```javascript
   animation.setSubframe(true); // Enables subframe rendering for fluid intermediate curves
   ```

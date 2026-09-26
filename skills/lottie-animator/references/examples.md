# Recipes

Twenty-two generators live in `examples/` (linked beside this skill as `examples/`).
Each writes one finished animation, and each was rendered, read as a filmstrip and an
onion skin, and revised before it shipped. Start from the nearest one: the timing, the
easing and the structure are already right.

Each generator's docstring states its brief — the feeling, the register, the hero
property — and `build(c)` takes a palette by role, so any of them renders in any of the
nine palettes (`--palette NAME`). The table says what each one is worth stealing.

| Recipe | Palette | What it shows |
|---|---|---|
| [`success-check`](../../../examples/success-check.py) | `forest` | Disc settles, check writes itself, one quiet ripple. |
| [`error-shake`](../../../examples/error-shake.py) | `mono` | Disc settles, X writes itself, then one crisp decaying shake. |
| [`heart-like`](../../../examples/heart-like.py) | `berry` | Press, pop, burst: the one playful example, labelled as such. |
| [`notification-bell`](../../../examples/notification-bell.py) | `citrus` | One ring that swings itself still, the clapper a beat behind. |
| [`toggle-switch`](../../../examples/toggle-switch.py) | `night` | Off, on, off: the knob and both colours move on one curve. |
| [`lock-unlock`](../../../examples/lock-unlock.py) | `sky` | The shackle lifts free and the colour follows; then it locks again. |
| [`play-pause`](../../../examples/play-pause.py) | `dusk` | Each half of the play triangle squares off into a pause bar, and back. |
| [`shape-morph`](../../../examples/shape-morph.py) | `sky` | A squircle softens into a circle and back, a quarter turn per cycle. |
| [`spinner-arc`](../../../examples/spinner-arc.py) | `mono` | Head leads, tail follows, the ring turns: a seamless indeterminate spinner. |
| [`typing-dots`](../../../examples/typing-dots.py) | `harbor` | A three-dot wave with a rest, so it reads as typing. |
| [`panda-loader`](../../../examples/panda-loader.py) | `paper` | A panda chews bamboo inside a slow, breathing loading ring. |
| [`download-progress`](../../../examples/download-progress.py) | `harbor` | Arrow into tray, a ring that fills at an uneven pace, then a check. |
| [`battery-charge`](../../../examples/battery-charge.py) | `forest` | Charge climbs in eased steps, the bolt settles, then it drains. |
| [`equalizer`](../../../examples/equalizer.py) | `night` | Five bars, each on its own tempo, bass slow and treble quick. |
| [`location-ping`](../../../examples/location-ping.py) | `dusk` | A still pin; rings spread across the ground, thin and fade. |
| [`weather-sun`](../../../examples/weather-sun.py) | `sky` | Rays turn slowly while a cloud drifts across the sun and back. |
| [`paper-plane`](../../../examples/paper-plane.py) | `paper` | A paper plane cruises in on a curve, turning with it, and leaves a dashed trail. |
| [`confetti-burst`](../../../examples/confetti-burst.py) | `berry` | Playful but restrained: one pop, fourteen pieces on ballistic arcs. |
| [`card-stack`](../../../examples/card-stack.py) | `mono` | Three cards settle back to front; the content writes in; the chip lands last. |
| [`logo-draw-on`](../../../examples/logo-draw-on.py) | `paper` | An SVG mark writes its lines; the sun rises out of the horizon, last. |
| [`rocket-launch`](../../../examples/rocket-launch.py) | `paper` | An SVG icon, converted part by part, assembles and lifts off its own axis. |
| [`bouncing-ball`](../../../examples/bouncing-ball.py) | `citrus` | Playful: squash and stretch at constant volume, spaced by gravity. |

## Adapting a recipe

1. **Read the brief first.** The docstring names the one idea that makes it work; keep
   that idea when the geometry changes.
2. **Copy, then point `sys.path` at this skill's `scripts/`.** Change geometry and beats;
   keep the tokens (`track`, `delay`, the easing names) and the colour roles.
3. **Retime in frames.** `(op - ip) / fr` seconds. Loops close exactly: first and last
   values equal, cycle lengths that divide the loop.
4. **Verify, then judge.** `lottie_lint.py --strict`, `render.mjs`, then
   `render.mjs --onion` and the taste pass in [motion-taste.md](motion-taste.md), on
   your palette and on a dark one.

## Raw JSON, for reading and repair

Three complete compositions, as the builders emit them. Read them to learn the
structure of a file made elsewhere before repairing it; to make something new, start
from a recipe instead. Every keyframe except the last carries `o` and `i` handles, even
where the motion is linear: a keyframe without them freezes lottie-web mid-render
(`KF012`).

### Card entrance

The house entrance: a squircle card fades up from 94% scale with a strong ease-out and a small rise. Opacity finishes at half the duration, so the card is solid while it settles. No overshoot.

```json
{
  "v": "5.12.1",
  "fr": 60,
  "ip": 0,
  "op": 60,
  "w": 320,
  "h": 240,
  "nm": "Card Entrance",
  "ddd": 0,
  "assets": [],
  "layers": [
    {
      "ddd": 0,
      "ty": 4,
      "ind": 1,
      "nm": "Card",
      "sr": 1,
      "ks": {
        "a": {"a": 0, "k": [0, 0, 0]},
        "p": {
          "a": 1,
          "k": [
            {"t": 0, "s": [160, 128, 0], "o": {"x": [0.23], "y": [1.0]}, "i": {"x": [0.32], "y": [1.0]}},
            {"t": 28, "s": [160, 120, 0]}
          ]
        },
        "s": {
          "a": 1,
          "k": [
            {"t": 0, "s": [94, 94, 100], "o": {"x": [0.23], "y": [1.0]}, "i": {"x": [0.32], "y": [1.0]}},
            {"t": 28, "s": [100, 100, 100]}
          ]
        },
        "r": {"a": 0, "k": 0},
        "o": {
          "a": 1,
          "k": [
            {"t": 0, "s": [0], "o": {"x": [0.23], "y": [1.0]}, "i": {"x": [0.32], "y": [1.0]}},
            {"t": 14, "s": [100]}
          ]
        }
      },
      "ao": 0,
      "shapes": [
        {
          "ty": "gr",
          "nm": "Card",
          "it": [
            {
              "ty": "sh",
              "nm": "Path",
              "ks": {
                "a": 0,
                "k": {
                  "c": true,
                  "v": [
                    [53.14, -66.0],
                    [100.0, -19.14],
                    [100.0, 19.14],
                    [53.14, 66.0],
                    [-53.14, 66.0],
                    [-100.0, 19.14],
                    [-100.0, -19.14],
                    [-53.14, -66.0]
                  ],
                  "i": [[0, 0], [0.0, -46.86], [0, 0], [46.86, 0.0], [0, 0], [0.0, 46.86], [0, 0], [-46.86, 0.0]],
                  "o": [[46.86, 0.0], [0, 0], [0.0, 46.86], [0, 0], [-46.86, 0.0], [0, 0], [0.0, -46.86], [0, 0]]
                }
              }
            },
            {
              "ty": "fl",
              "nm": "Fill",
              "c": {"a": 0, "k": [0.7843, 0.3216, 0.1686, 1.0]},
              "o": {"a": 0, "k": 100}
            },
            {
              "ty": "tr",
              "a": {"a": 0, "k": [0, 0]},
              "p": {"a": 0, "k": [0, 0]},
              "s": {"a": 0, "k": [100, 100]},
              "r": {"a": 0, "k": 0},
              "o": {"a": 0, "k": 100}
            }
          ]
        }
      ],
      "ip": 0,
      "op": 60,
      "st": 0
    }
  ]
}
```

### Progress fill with a track matte

A level rising inside a squircle matte on a `glide` ease. The matte layer (`td: 1`) sits directly above the layer it masks (`tt: 1`); Lottie pairs them by adjacency.

```json
{
  "v": "5.12.1",
  "fr": 60,
  "ip": 0,
  "op": 90,
  "w": 200,
  "h": 200,
  "nm": "Progress Fill",
  "ddd": 0,
  "assets": [],
  "layers": [
    {
      "ddd": 0,
      "ty": 4,
      "ind": 1,
      "nm": "Matte",
      "sr": 1,
      "ks": {
        "a": {"a": 0, "k": [0, 0, 0]},
        "p": {"a": 0, "k": [100, 100, 0]},
        "s": {"a": 0, "k": [100, 100, 100]},
        "r": {"a": 0, "k": 0},
        "o": {"a": 0, "k": 100}
      },
      "ao": 0,
      "shapes": [
        {
          "ty": "gr",
          "nm": "Plate",
          "it": [
            {
              "ty": "sh",
              "nm": "Path",
              "ks": {
                "a": 0,
                "k": {
                  "c": true,
                  "v": [
                    [4.71, -75.0],
                    [75.0, -4.71],
                    [75.0, 4.71],
                    [4.71, 75.0],
                    [-4.71, 75.0],
                    [-75.0, 4.71],
                    [-75.0, -4.71],
                    [-4.71, -75.0]
                  ],
                  "i": [[0, 0], [0.0, -70.29], [0, 0], [70.29, 0.0], [0, 0], [0.0, 70.29], [0, 0], [-70.29, 0.0]],
                  "o": [[70.29, 0.0], [0, 0], [0.0, 70.29], [0, 0], [-70.29, 0.0], [0, 0], [0.0, -70.29], [0, 0]]
                }
              }
            },
            {
              "ty": "fl",
              "nm": "Fill",
              "c": {"a": 0, "k": [0.9529, 0.9333, 0.902, 1.0]},
              "o": {"a": 0, "k": 100}
            },
            {
              "ty": "tr",
              "a": {"a": 0, "k": [0, 0]},
              "p": {"a": 0, "k": [0, 0]},
              "s": {"a": 0, "k": [100, 100]},
              "r": {"a": 0, "k": 0},
              "o": {"a": 0, "k": 100}
            }
          ]
        }
      ],
      "ip": 0,
      "op": 90,
      "st": 0,
      "td": 1
    },
    {
      "ddd": 0,
      "ty": 4,
      "ind": 2,
      "nm": "Level",
      "sr": 1,
      "ks": {
        "a": {"a": 0, "k": [0, 0, 0]},
        "p": {
          "a": 1,
          "k": [
            {"t": 0, "s": [100, 290, 0], "o": {"x": [0.32], "y": [0.72]}, "i": {"x": [0.0], "y": [1.0]}},
            {"t": 60, "s": [100, 140, 0]}
          ]
        },
        "s": {"a": 0, "k": [100, 100, 100]},
        "r": {"a": 0, "k": 0},
        "o": {"a": 0, "k": 100}
      },
      "ao": 0,
      "shapes": [
        {
          "ty": "gr",
          "nm": "Level",
          "it": [
            {
              "ty": "rc",
              "nm": "Rectangle",
              "p": {"a": 0, "k": [0, 0]},
              "s": {"a": 0, "k": [220, 200]},
              "r": {"a": 0, "k": 0}
            },
            {
              "ty": "fl",
              "nm": "Fill",
              "c": {"a": 0, "k": [0.4353, 0.5059, 0.3882, 1.0]},
              "o": {"a": 0, "k": 100}
            },
            {
              "ty": "tr",
              "a": {"a": 0, "k": [0, 0]},
              "p": {"a": 0, "k": [0, 0]},
              "s": {"a": 0, "k": [100, 100]},
              "r": {"a": 0, "k": 0},
              "o": {"a": 0, "k": 100}
            }
          ]
        }
      ],
      "ip": 0,
      "op": 90,
      "st": 0,
      "tt": 1
    },
    {
      "ddd": 0,
      "ty": 4,
      "ind": 3,
      "nm": "Well",
      "sr": 1,
      "ks": {
        "a": {"a": 0, "k": [0, 0, 0]},
        "p": {"a": 0, "k": [100, 100, 0]},
        "s": {"a": 0, "k": [100, 100, 100]},
        "r": {"a": 0, "k": 0},
        "o": {"a": 0, "k": 100}
      },
      "ao": 0,
      "shapes": [
        {
          "ty": "gr",
          "nm": "Well",
          "it": [
            {
              "ty": "sh",
              "nm": "Path",
              "ks": {
                "a": 0,
                "k": {
                  "c": true,
                  "v": [
                    [4.71, -75.0],
                    [75.0, -4.71],
                    [75.0, 4.71],
                    [4.71, 75.0],
                    [-4.71, 75.0],
                    [-75.0, 4.71],
                    [-75.0, -4.71],
                    [-4.71, -75.0]
                  ],
                  "i": [[0, 0], [0.0, -70.29], [0, 0], [70.29, 0.0], [0, 0], [0.0, 70.29], [0, 0], [-70.29, 0.0]],
                  "o": [[70.29, 0.0], [0, 0], [0.0, 70.29], [0, 0], [-70.29, 0.0], [0, 0], [0.0, -70.29], [0, 0]]
                }
              }
            },
            {
              "ty": "fl",
              "nm": "Fill",
              "c": {"a": 0, "k": [0.8941, 0.851, 0.7765, 1.0]},
              "o": {"a": 0, "k": 100}
            },
            {
              "ty": "tr",
              "a": {"a": 0, "k": [0, 0]},
              "p": {"a": 0, "k": [0, 0]},
              "s": {"a": 0, "k": [100, 100]},
              "r": {"a": 0, "k": 0},
              "o": {"a": 0, "k": 100}
            }
          ]
        }
      ],
      "ip": 0,
      "op": 90,
      "st": 0
    }
  ]
}
```

### Arm wave (parenting)

Upper arm → forearm → hand, each parented to the one above and pivoting at its joint, all on `in-out`. The forearm and hand move a third as far as the shoulder and a few degrees behind it — overlap, not wobble. `parent` names the parent's `ind`.

```json
{
  "v": "5.12.1",
  "fr": 60,
  "ip": 0,
  "op": 90,
  "w": 400,
  "h": 400,
  "nm": "Arm Wave Loop",
  "ddd": 0,
  "assets": [],
  "layers": [
    {
      "ddd": 0,
      "ty": 4,
      "ind": 1,
      "nm": "Hand",
      "sr": 1,
      "ks": {
        "a": {"a": 0, "k": [0, 0, 0]},
        "p": {"a": 0, "k": [0, 100, 0]},
        "s": {"a": 0, "k": [100, 100, 100]},
        "r": {
          "a": 1,
          "k": [
            {"t": 0, "s": [-4], "o": {"x": [0.77], "y": [0.0]}, "i": {"x": [0.175], "y": [1.0]}},
            {"t": 45, "s": [4], "o": {"x": [0.77], "y": [0.0]}, "i": {"x": [0.175], "y": [1.0]}},
            {"t": 90, "s": [-4]}
          ]
        },
        "o": {"a": 0, "k": 100}
      },
      "ao": 0,
      "shapes": [
        {
          "ty": "gr",
          "nm": "Hand",
          "it": [
            {"ty": "el", "nm": "Ellipse", "p": {"a": 0, "k": [0, 12]}, "s": {"a": 0, "k": [34, 34]}},
            {
              "ty": "fl",
              "nm": "Fill",
              "c": {"a": 0, "k": [0.8941, 0.851, 0.7765, 1.0]},
              "o": {"a": 0, "k": 100}
            },
            {
              "ty": "tr",
              "a": {"a": 0, "k": [0, 0]},
              "p": {"a": 0, "k": [0, 0]},
              "s": {"a": 0, "k": [100, 100]},
              "r": {"a": 0, "k": 0},
              "o": {"a": 0, "k": 100}
            }
          ]
        }
      ],
      "ip": 0,
      "op": 90,
      "st": 0,
      "parent": 2
    },
    {
      "ddd": 0,
      "ty": 4,
      "ind": 2,
      "nm": "Forearm",
      "sr": 1,
      "ks": {
        "a": {"a": 0, "k": [0, 0, 0]},
        "p": {"a": 0, "k": [0, 110, 0]},
        "s": {"a": 0, "k": [100, 100, 100]},
        "r": {
          "a": 1,
          "k": [
            {"t": 0, "s": [3], "o": {"x": [0.77], "y": [0.0]}, "i": {"x": [0.175], "y": [1.0]}},
            {"t": 45, "s": [-3], "o": {"x": [0.77], "y": [0.0]}, "i": {"x": [0.175], "y": [1.0]}},
            {"t": 90, "s": [3]}
          ]
        },
        "o": {"a": 0, "k": 100}
      },
      "ao": 0,
      "shapes": [
        {
          "ty": "gr",
          "nm": "Forearm",
          "it": [
            {
              "ty": "rc",
              "nm": "Rectangle",
              "p": {"a": 0, "k": [0, 50]},
              "s": {"a": 0, "k": [26, 100]},
              "r": {"a": 0, "k": 13}
            },
            {
              "ty": "fl",
              "nm": "Fill",
              "c": {"a": 0, "k": [0.4353, 0.5059, 0.3882, 1.0]},
              "o": {"a": 0, "k": 100}
            },
            {
              "ty": "tr",
              "a": {"a": 0, "k": [0, 0]},
              "p": {"a": 0, "k": [0, 0]},
              "s": {"a": 0, "k": [100, 100]},
              "r": {"a": 0, "k": 0},
              "o": {"a": 0, "k": 100}
            }
          ]
        }
      ],
      "ip": 0,
      "op": 90,
      "st": 0,
      "parent": 3
    },
    {
      "ddd": 0,
      "ty": 4,
      "ind": 3,
      "nm": "Upper Arm",
      "sr": 1,
      "ks": {
        "a": {"a": 0, "k": [0, 0, 0]},
        "p": {"a": 0, "k": [200, 110, 0]},
        "s": {"a": 0, "k": [100, 100, 100]},
        "r": {
          "a": 1,
          "k": [
            {"t": 0, "s": [0], "o": {"x": [0.77], "y": [0.0]}, "i": {"x": [0.175], "y": [1.0]}},
            {"t": 45, "s": [12], "o": {"x": [0.77], "y": [0.0]}, "i": {"x": [0.175], "y": [1.0]}},
            {"t": 90, "s": [0]}
          ]
        },
        "o": {"a": 0, "k": 100}
      },
      "ao": 0,
      "shapes": [
        {
          "ty": "gr",
          "nm": "Upper Arm",
          "it": [
            {
              "ty": "rc",
              "nm": "Rectangle",
              "p": {"a": 0, "k": [0, 60]},
              "s": {"a": 0, "k": [30, 120]},
              "r": {"a": 0, "k": 15}
            },
            {
              "ty": "fl",
              "nm": "Fill",
              "c": {"a": 0, "k": [0.1176, 0.1059, 0.0941, 1.0]},
              "o": {"a": 0, "k": 100}
            },
            {
              "ty": "tr",
              "a": {"a": 0, "k": [0, 0]},
              "p": {"a": 0, "k": [0, 0]},
              "s": {"a": 0, "k": [100, 100]},
              "r": {"a": 0, "k": 0},
              "o": {"a": 0, "k": 100}
            }
          ]
        }
      ],
      "ip": 0,
      "op": 90,
      "st": 0
    }
  ]
}
```

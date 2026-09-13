# Lottie Animation Examples

Eight complete compositions to start from. Every one of them is linted by the test suite and was rendered before it was written down, so what you copy is what plays.

Every keyframe except the last carries `o` and `i` handles, even where the motion is linear. That is not style: a keyframe without them freezes lottie-web mid-render (`KF012`).

## 1. Logo fade + scale entrance

The classic entrance: pop in with a small overshoot while fading up. The layer's anchor and position both sit at the centre, so the scale pivots there.

```json
{
  "v": "5.12.1",
  "fr": 60,
  "ip": 0,
  "op": 60,
  "w": 512,
  "h": 512,
  "nm": "Logo Entrance",
  "ddd": 0,
  "assets": [],
  "layers": [
    {
      "ddd": 0,
      "ty": 4,
      "ind": 1,
      "nm": "Logo",
      "sr": 1,
      "ks": {
        "a": {"a": 0, "k": [0, 0, 0]},
        "p": {"a": 0, "k": [256, 256, 0]},
        "s": {
          "a": 1,
          "k": [
            {"t": 0, "s": [0, 0, 100], "o": {"x": [0.34], "y": [1.56]}, "i": {"x": [0.64], "y": [1]}},
            {"t": 30, "s": [105, 105, 100], "o": {"x": [0.33], "y": [0]}, "i": {"x": [0.67], "y": [1]}},
            {"t": 45, "s": [100, 100, 100]}
          ]
        },
        "r": {"a": 0, "k": 0},
        "o": {
          "a": 1,
          "k": [
            {"t": 0, "s": [0], "o": {"x": [0.33], "y": [0]}, "i": {"x": [0.67], "y": [1]}},
            {"t": 30, "s": [100]}
          ]
        }
      },
      "ao": 0,
      "shapes": [
        {
          "ty": "gr",
          "nm": "Circle",
          "it": [
            {"ty": "el", "nm": "Ellipse", "p": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [200, 200]}},
            {"ty": "fl", "nm": "Fill", "c": {"a": 0, "k": [0.2, 0.4, 1, 1]}, "o": {"a": 0, "k": 100}},
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

## 2. Continuous pulse loop

A status dot that breathes. The last keyframe lands at `op` on the first keyframe's value, so the wrap is seamless.

```json
{
  "v": "5.12.1",
  "fr": 60,
  "ip": 0,
  "op": 60,
  "w": 200,
  "h": 200,
  "nm": "Pulse Loop",
  "ddd": 0,
  "assets": [],
  "layers": [
    {
      "ddd": 0,
      "ty": 4,
      "ind": 1,
      "nm": "Pulse",
      "sr": 1,
      "ks": {
        "a": {"a": 0, "k": [0, 0, 0]},
        "p": {"a": 0, "k": [100, 100, 0]},
        "s": {
          "a": 1,
          "k": [
            {"t": 0, "s": [100, 100, 100], "o": {"x": [0.645], "y": [0.045]}, "i": {"x": [0.355], "y": [1]}},
            {"t": 30, "s": [110, 110, 100], "o": {"x": [0.645], "y": [0.045]}, "i": {"x": [0.355], "y": [1]}},
            {"t": 60, "s": [100, 100, 100]}
          ]
        },
        "r": {"a": 0, "k": 0},
        "o": {"a": 0, "k": 100}
      },
      "ao": 0,
      "shapes": [
        {
          "ty": "gr",
          "nm": "Dot",
          "it": [
            {"ty": "el", "nm": "Ellipse", "p": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [50, 50]}},
            {"ty": "fl", "nm": "Fill", "c": {"a": 0, "k": [0.3, 0.8, 0.4, 1]}, "o": {"a": 0, "k": 100}},
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

## 3. Spinner

A trimmed stroke rotating a full turn. Linear handles are correct here: a spinner must not slow down. 0° and 360° are the same pose, so the loop closes.

```json
{
  "v": "5.12.1",
  "fr": 60,
  "ip": 0,
  "op": 120,
  "w": 100,
  "h": 100,
  "nm": "Spinner",
  "ddd": 0,
  "assets": [],
  "layers": [
    {
      "ddd": 0,
      "ty": 4,
      "ind": 1,
      "nm": "Spinner",
      "sr": 1,
      "ks": {
        "a": {"a": 0, "k": [0, 0, 0]},
        "p": {"a": 0, "k": [50, 50, 0]},
        "s": {"a": 0, "k": [100, 100, 100]},
        "r": {
          "a": 1,
          "k": [
            {"t": 0, "s": [0], "o": {"x": [0.333], "y": [0.333]}, "i": {"x": [0.667], "y": [0.667]}},
            {"t": 120, "s": [360]}
          ]
        },
        "o": {"a": 0, "k": 100}
      },
      "ao": 0,
      "shapes": [
        {
          "ty": "gr",
          "nm": "Arc",
          "it": [
            {"ty": "el", "nm": "Ellipse", "p": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [60, 60]}},
            {
              "ty": "st",
              "nm": "Stroke",
              "c": {"a": 0, "k": [0.2, 0.4, 1, 1]},
              "o": {"a": 0, "k": 100},
              "w": {"a": 0, "k": 4},
              "lc": 2,
              "lj": 2
            },
            {
              "ty": "tm",
              "nm": "Trim",
              "s": {"a": 0, "k": 0},
              "e": {"a": 0, "k": 75},
              "o": {"a": 0, "k": 0},
              "m": 1
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
      "op": 120,
      "st": 0
    }
  ]
}
```

## 4. Heartbeat

A lub-dub: two quick beats, a rest, and a small rotational wobble as secondary action. The path came out of `svg2lottie.py`, not from hand-typed tangents.

```json
{
  "v": "5.12.1",
  "fr": 60,
  "ip": 0,
  "op": 60,
  "w": 200,
  "h": 200,
  "nm": "Organic Heart",
  "ddd": 0,
  "assets": [],
  "layers": [
    {
      "ddd": 0,
      "ty": 4,
      "ind": 1,
      "nm": "Heart",
      "sr": 1,
      "ks": {
        "a": {"a": 0, "k": [100.0, 100.0, 0]},
        "p": {"a": 0, "k": [100.0, 100.0, 0]},
        "s": {
          "a": 1,
          "k": [
            {"t": 0, "s": [100, 100, 100], "o": {"x": [0.33], "y": [0]}, "i": {"x": [0.67], "y": [1]}},
            {"t": 8, "s": [115, 115, 100], "o": {"x": [0.55], "y": [0.055]}, "i": {"x": [0.675], "y": [0.19]}},
            {"t": 12, "s": [95, 95, 100], "o": {"x": [0.33], "y": [0]}, "i": {"x": [0.67], "y": [1]}},
            {"t": 18, "s": [105, 105, 100], "o": {"x": [0.645], "y": [0.045]}, "i": {"x": [0.355], "y": [1]}},
            {"t": 35, "s": [100, 100, 100]}
          ]
        },
        "r": {
          "a": 1,
          "k": [
            {"t": 0, "s": [0], "o": {"x": [0.645], "y": [0.045]}, "i": {"x": [0.355], "y": [1]}},
            {"t": 8, "s": [-2], "o": {"x": [0.645], "y": [0.045]}, "i": {"x": [0.355], "y": [1]}},
            {"t": 18, "s": [1], "o": {"x": [0.645], "y": [0.045]}, "i": {"x": [0.355], "y": [1]}},
            {"t": 35, "s": [0]}
          ]
        },
        "o": {"a": 0, "k": 100}
      },
      "ao": 0,
      "shapes": [
        {
          "ty": "gr",
          "nm": "path 1",
          "it": [
            {
              "ty": "sh",
              "nm": "Path",
              "ks": {
                "a": 0,
                "k": {
                  "i": [[42.0, -30.0], [0.0, 42.0], [-22.0, 0.0], [-7.0, -16.0], [-17.0, 0.0], [0.0, -26.0]],
                  "o": [[-42.0, -30.0], [0.0, -26.0], [17.0, 0.0], [7.0, -16.0], [22.0, 0.0], [0.0, 42.0]],
                  "v": [[100.0, 172.0], [18.0, 70.0], [62.0, 28.0], [100.0, 54.0], [138.0, 28.0], [182.0, 70.0]],
                  "c": true
                }
              }
            },
            {
              "ty": "fl",
              "nm": "Fill",
              "c": {"a": 0, "k": [0.902, 0.2235, 0.2745, 1]},
              "o": {"a": 0, "k": 100.0},
              "r": 1
            },
            {
              "ty": "tr",
              "p": {"a": 0, "k": [0, 0]},
              "a": {"a": 0, "k": [0, 0]},
              "s": {"a": 0, "k": [100, 100]},
              "r": {"a": 0, "k": 0},
              "o": {"a": 0, "k": 100},
              "sk": {"a": 0, "k": 0},
              "sa": {"a": 0, "k": 0}
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

## 5. Bounce with squash and stretch

Ease in on the way down (gravity), ease out on the way up. Scale squashes on contact and overshoots on the rebound; the products stay near 100 × 100 so the volume reads as constant.

```json
{
  "v": "5.12.1",
  "fr": 60,
  "ip": 0,
  "op": 60,
  "w": 200,
  "h": 300,
  "nm": "Bouncy Ball",
  "ddd": 0,
  "assets": [],
  "layers": [
    {
      "ddd": 0,
      "ty": 4,
      "ind": 1,
      "nm": "Ball",
      "sr": 1,
      "ks": {
        "a": {"a": 0, "k": [0, 0, 0]},
        "p": {
          "a": 1,
          "k": [
            {"t": 0, "s": [100, 50, 0], "o": {"x": [0.55], "y": [0.055]}, "i": {"x": [0.675], "y": [0.19]}},
            {"t": 20, "s": [100, 250, 0], "o": {"x": [0.33], "y": [0]}, "i": {"x": [0.67], "y": [1]}},
            {"t": 40, "s": [100, 100, 0], "o": {"x": [0.55], "y": [0.055]}, "i": {"x": [0.675], "y": [0.19]}},
            {"t": 60, "s": [100, 250, 0]}
          ]
        },
        "s": {
          "a": 1,
          "k": [
            {"t": 0, "s": [100, 100, 100], "o": {"x": [0.33], "y": [0]}, "i": {"x": [0.67], "y": [1]}},
            {"t": 18, "s": [90, 110, 100], "o": {"x": [0.33], "y": [0]}, "i": {"x": [0.67], "y": [1]}},
            {"t": 20, "s": [120, 80, 100], "o": {"x": [0.34], "y": [1.56]}, "i": {"x": [0.64], "y": [1]}},
            {"t": 28, "s": [100, 100, 100], "o": {"x": [0.33], "y": [0]}, "i": {"x": [0.67], "y": [1]}},
            {"t": 60, "s": [100, 100, 100]}
          ]
        },
        "r": {"a": 0, "k": 0},
        "o": {"a": 0, "k": 100}
      },
      "ao": 0,
      "shapes": [
        {
          "ty": "gr",
          "nm": "Ball",
          "it": [
            {"ty": "el", "nm": "Ellipse", "p": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [60, 60]}},
            {"ty": "fl", "nm": "Fill", "c": {"a": 0, "k": [1, 0.5, 0, 1]}, "o": {"a": 0, "k": 100}},
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

## 6. Staggered elements

Three dots arriving five frames apart. Keyframe times are composition frames, so the delay lives in the keyframes; each layer's `ip` and `st` move with its first keyframe so a dot is not on screen before its entrance begins.

```json
{
  "v": "5.12.1",
  "fr": 60,
  "ip": 0,
  "op": 90,
  "w": 400,
  "h": 100,
  "nm": "Stagger",
  "ddd": 0,
  "assets": [],
  "layers": [
    {
      "ddd": 0,
      "ty": 4,
      "ind": 1,
      "nm": "Dot 1",
      "sr": 1,
      "ks": {
        "a": {"a": 0, "k": [0, 0, 0]},
        "p": {"a": 0, "k": [100, 50, 0]},
        "s": {
          "a": 1,
          "k": [
            {"t": 0, "s": [0, 0, 100], "o": {"x": [0.34], "y": [1.56]}, "i": {"x": [0.64], "y": [1]}},
            {"t": 20, "s": [100, 100, 100]}
          ]
        },
        "r": {"a": 0, "k": 0},
        "o": {"a": 0, "k": 100}
      },
      "ao": 0,
      "shapes": [
        {
          "ty": "gr",
          "nm": "Dot",
          "it": [
            {"ty": "el", "nm": "Ellipse", "p": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [40, 40]}},
            {"ty": "fl", "nm": "Fill", "c": {"a": 0, "k": [0.55, 0.36, 0.96, 1]}, "o": {"a": 0, "k": 100}},
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
    },
    {
      "ddd": 0,
      "ty": 4,
      "ind": 2,
      "nm": "Dot 2",
      "sr": 1,
      "ks": {
        "a": {"a": 0, "k": [0, 0, 0]},
        "p": {"a": 0, "k": [200, 50, 0]},
        "s": {
          "a": 1,
          "k": [
            {"t": 5, "s": [0, 0, 100], "o": {"x": [0.34], "y": [1.56]}, "i": {"x": [0.64], "y": [1]}},
            {"t": 25, "s": [100, 100, 100]}
          ]
        },
        "r": {"a": 0, "k": 0},
        "o": {"a": 0, "k": 100}
      },
      "ao": 0,
      "shapes": [
        {
          "ty": "gr",
          "nm": "Dot",
          "it": [
            {"ty": "el", "nm": "Ellipse", "p": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [40, 40]}},
            {"ty": "fl", "nm": "Fill", "c": {"a": 0, "k": [0.55, 0.36, 0.96, 1]}, "o": {"a": 0, "k": 100}},
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
      "ip": 5,
      "op": 90,
      "st": 5
    },
    {
      "ddd": 0,
      "ty": 4,
      "ind": 3,
      "nm": "Dot 3",
      "sr": 1,
      "ks": {
        "a": {"a": 0, "k": [0, 0, 0]},
        "p": {"a": 0, "k": [300, 50, 0]},
        "s": {
          "a": 1,
          "k": [
            {"t": 10, "s": [0, 0, 100], "o": {"x": [0.34], "y": [1.56]}, "i": {"x": [0.64], "y": [1]}},
            {"t": 30, "s": [100, 100, 100]}
          ]
        },
        "r": {"a": 0, "k": 0},
        "o": {"a": 0, "k": 100}
      },
      "ao": 0,
      "shapes": [
        {
          "ty": "gr",
          "nm": "Dot",
          "it": [
            {"ty": "el", "nm": "Ellipse", "p": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [40, 40]}},
            {"ty": "fl", "nm": "Fill", "c": {"a": 0, "k": [0.55, 0.36, 0.96, 1]}, "o": {"a": 0, "k": 100}},
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
      "ip": 10,
      "op": 90,
      "st": 10
    }
  ]
}
```

## 7. Liquid fill with a track matte

A rising rectangle seen through a circular matte. The matte layer (`td: 1`) sits directly above the layer it masks (`tt: 1`); Lottie pairs them by adjacency.

```json
{
  "v": "5.12.1",
  "fr": 60,
  "ip": 0,
  "op": 120,
  "w": 200,
  "h": 200,
  "nm": "Liquid Fill",
  "ddd": 0,
  "assets": [],
  "layers": [
    {
      "ddd": 0,
      "ty": 4,
      "ind": 1,
      "nm": "Matte Circle",
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
          "nm": "Disc",
          "it": [
            {"ty": "el", "nm": "Ellipse", "p": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [180, 180]}},
            {"ty": "fl", "nm": "Fill", "c": {"a": 0, "k": [1, 1, 1, 1]}, "o": {"a": 0, "k": 100}},
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
      "op": 120,
      "st": 0,
      "td": 1
    },
    {
      "ddd": 0,
      "ty": 4,
      "ind": 2,
      "nm": "Liquid",
      "sr": 1,
      "ks": {
        "a": {"a": 0, "k": [0, 0, 0]},
        "p": {
          "a": 1,
          "k": [
            {"t": 0, "s": [100, 330, 0], "o": {"x": [0.33], "y": [0]}, "i": {"x": [0.67], "y": [1]}},
            {"t": 119, "s": [100, 140, 0]}
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
          "nm": "Wave",
          "it": [
            {
              "ty": "rc",
              "nm": "Rectangle",
              "p": {"a": 0, "k": [0, 0]},
              "s": {"a": 0, "k": [220, 260]},
              "r": {"a": 0, "k": 0}
            },
            {"ty": "fl", "nm": "Fill", "c": {"a": 0, "k": [0.2, 0.6, 1, 1]}, "o": {"a": 0, "k": 100}},
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
      "op": 120,
      "st": 0,
      "tt": 1
    }
  ]
}
```

## 8. Character arm wave (parenting)

Upper arm → forearm → hand, each parented to the one above and pivoting at its joint. Rotate the shoulder and the whole chain swings. `parent` names the parent's `ind`, not its array position.

```json
{
  "v": "5.12.1",
  "fr": 60,
  "ip": 0,
  "op": 60,
  "w": 500,
  "h": 500,
  "nm": "Arm Wave",
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
            {"t": 0, "s": [-10], "o": {"x": [0.645], "y": [0.045]}, "i": {"x": [0.355], "y": [1]}},
            {"t": 30, "s": [10], "o": {"x": [0.645], "y": [0.045]}, "i": {"x": [0.355], "y": [1]}},
            {"t": 60, "s": [-10]}
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
            {"ty": "fl", "nm": "Fill", "c": {"a": 0, "k": [0.96, 0.76, 0.6, 1]}, "o": {"a": 0, "k": 100}},
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
        "p": {"a": 0, "k": [0, 120, 0]},
        "s": {"a": 0, "k": [100, 100, 100]},
        "r": {
          "a": 1,
          "k": [
            {"t": 0, "s": [5], "o": {"x": [0.645], "y": [0.045]}, "i": {"x": [0.355], "y": [1]}},
            {"t": 30, "s": [-5], "o": {"x": [0.645], "y": [0.045]}, "i": {"x": [0.355], "y": [1]}},
            {"t": 60, "s": [5]}
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
            {"ty": "fl", "nm": "Fill", "c": {"a": 0, "k": [0.2, 0.55, 0.9, 1]}, "o": {"a": 0, "k": 100}},
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
        "p": {"a": 0, "k": [250, 200, 0]},
        "s": {"a": 0, "k": [100, 100, 100]},
        "r": {
          "a": 1,
          "k": [
            {"t": 0, "s": [0], "o": {"x": [0.645], "y": [0.045]}, "i": {"x": [0.355], "y": [1]}},
            {"t": 30, "s": [15], "o": {"x": [0.645], "y": [0.045]}, "i": {"x": [0.355], "y": [1]}},
            {"t": 60, "s": [0]}
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
            {"ty": "fl", "nm": "Fill", "c": {"a": 0, "k": [0.15, 0.45, 0.8, 1]}, "o": {"a": 0, "k": 100}},
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

## Using them

1. **Copy and modify.** Change colours, timings and sizes; keep the structure.
2. **Combine.** Stagger + bounce, matte + trim path.
3. **Scale.** Adjust `w`, `h` and every position proportionally.
4. **Retime.** `fr` and `op` set the duration: `(op - ip) / fr` seconds.
5. **Verify.** `lottie_lint.py`, then `render.mjs`, then look at the filmstrip. Nothing else counts as checked.

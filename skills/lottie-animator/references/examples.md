# Lottie Animation Examples

Complete examples ready to use as a base for professional animations.

## 1. Logo Fade + Scale Entrance

Classic entrance animation with fade and scale.

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
      "st": 0,
      "ip": 0,
      "op": 60,
      "ks": {
        "a": {"a": 0, "k": [256, 256]},
        "p": {"a": 0, "k": [256, 256]},
        "s": {
          "a": 1,
          "k": [
            {
              "t": 0,
              "s": [0, 0],
              "o": {"x": [0.34], "y": [1.56]},
              "i": {"x": [0.64], "y": [1]}
            },
            {
              "t": 30,
              "s": [105, 105],
              "o": {"x": [0.33], "y": [0]},
              "i": {"x": [0.67], "y": [1]}
            },
            {"t": 45, "s": [100, 100]}
          ]
        },
        "r": {"a": 0, "k": 0},
        "o": {
          "a": 1,
          "k": [
            {
              "t": 0,
              "s": [0],
              "o": {"x": [0.33], "y": [0]},
              "i": {"x": [0.67], "y": [1]}},
            {"t": 30, "s": [100]}
          ]
        }
      },
      "shapes": [
        {
          "ty": "gr",
          "nm": "Circle",
          "it": [
            {
              "ty": "el",
              "nm": "Ellipse",
              "p": {"a": 0, "k": [0, 0]},
              "s": {"a": 0, "k": [200, 200]}
            },
            {
              "ty": "fl",
              "nm": "Fill",
              "c": {"a": 0, "k": [0.2, 0.4, 1, 1]},
              "o": {"a": 0, "k": 100}
            },
            {
              "ty": "tr",
              "a": {"a": 0, "k": [0, 0]},
              "p": {"a": 0, "k": [256, 256]},
              "s": {"a": 0, "k": [100, 100]},
              "r": {"a": 0, "k": 0},
              "o": {"a": 0, "k": 100}
            }
          ]
        }
      ]
    }
  ]
}
```

## 2. Continuous Pulse Loop

Infinite pulse loop for indicators or status lights.

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
      "st": 0,
      "ip": 0,
      "op": 60,
      "ks": {
        "a": {"a": 0, "k": [100, 100]},
        "p": {"a": 0, "k": [100, 100]},
        "s": {
          "a": 1,
          "k": [
            {
              "t": 0,
              "s": [100, 100],
              "o": {"x": [0.645], "y": [0.045]},
              "i": {"x": [0.355], "y": [1]}
            },
            {
              "t": 30,
              "s": [110, 110],
              "o": {"x": [0.645], "y": [0.045]},
              "i": {"x": [0.355], "y": [1]}
            },
            {"t": 60, "s": [100, 100]}
          ]
        },
        "r": {"a": 0, "k": 0},
        "o": {"a": 0, "k": 100}
      },
      "shapes": [
        {
          "ty": "gr",
          "nm": "Dot",
          "it": [
            {
              "ty": "el",
              "p": {"a": 0, "k": [0, 0]},
              "s": {"a": 0, "k": [50, 50]}
            },
            {
              "ty": "fl",
              "c": {"a": 0, "k": [0.3, 0.8, 0.4, 1]},
              "o": {"a": 0, "k": 100}
            },
            {
              "ty": "tr",
              "p": {"a": 0, "k": [100, 100]},
              "s": {"a": 0, "k": [100, 100]},
              "r": {"a": 0, "k": 0},
              "o": {"a": 0, "k": 100}
            }
          ]
        }
      ]
    }
  ]
}
```

## 3. Continuous Rotation (Spinner)

Loading spinner with continuous rotation.

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
      "st": 0,
      "ip": 0,
      "op": 120,
      "ks": {
        "a": {"a": 0, "k": [50, 50]},
        "p": {"a": 0, "k": [50, 50]},
        "s": {"a": 0, "k": [100, 100]},
        "r": {
          "a": 1,
          "k": [
            {"t": 0, "s": [0]},
            {"t": 120, "s": [360]}
          ]
        },
        "o": {"a": 0, "k": 100}
      },
      "shapes": [
        {
          "ty": "gr",
          "nm": "Arc",
          "it": [
            {
              "ty": "el",
              "p": {"a": 0, "k": [0, 0]},
              "s": {"a": 0, "k": [60, 60]}
            },
            {
              "ty": "st",
              "c": {"a": 0, "k": [0.2, 0.4, 1, 1]},
              "o": {"a": 0, "k": 100},
              "w": {"a": 0, "k": 4},
              "lc": 2,
              "lj": 2
            },
            {
              "ty": "tm",
              "s": {"a": 0, "k": 0},
              "e": {"a": 0, "k": 75},
              "o": {"a": 0, "k": 0}
            },
            {
              "ty": "tr",
              "p": {"a": 0, "k": [50, 50]},
              "s": {"a": 0, "k": [100, 100]},
              "r": {"a": 0, "k": 0},
              "o": {"a": 0, "k": 100}
            }
          ]
        }
      ]
    }
  ]
}
```

## 4. Advance Heart Beat (Organic)

A realistic heart beat beat with "Lub-Dub" rhythm and secondary action.

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
      "nm": "HeartShape",
      "sr": 1,
      "st": 0,
      "ip": 0,
      "op": 60,
      "ks": {
        "a": {"a": 0, "k": [100, 100]},
        "p": {"a": 0, "k": [100, 100]},
        "s": {
          "a": 1,
          "k": [
            {"t": 0, "s": [100, 100], "o": {"x": [0.17], "y": [0.17]}, "i": {"x": [0.83], "y": [0.83]}},
            {"t": 8, "s": [115, 115], "o": {"x": [0.17], "y": [0.17]}, "i": {"x": [0.83], "y": [0.83]}}, 
            {"t": 12, "s": [95, 95], "o": {"x": [0.17], "y": [0.17]}, "i": {"x": [0.83], "y": [0.83]}},
            {"t": 18, "s": [105, 105], "o": {"x": [0.17], "y": [0.17]}, "i": {"x": [0.83], "y": [0.83]}},
            {"t": 35, "s": [100, 100]}
          ]
        },
        "r": {
           "a": 1, 
           "k": [
             {"t": 0, "s": [0]},
             {"t": 8, "s": [-2]},
             {"t": 18, "s": [1]},
             {"t": 35, "s": [0]}
           ]
        },
        "o": {"a": 0, "k": 100}
      },
      "shapes": [
        // ... (Path definition for Heart) ...
      ]
    }
  ]
}
```

## 5. Bounce with Squash & Stretch

Organic animation with deformation.

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
      "st": 0,
      "ip": 0,
      "op": 60,
      "ks": {
        "a": {"a": 0, "k": [100, 250]},
        "p": {
          "a": 1,
          "k": [
            {
              "t": 0,
              "s": [100, 50],
              "o": {"x": [0.55], "y": [0.055]},
              "i": {"x": [0.675], "y": [0.19]}
            },
            {
              "t": 20,
              "s": [100, 250],
              "o": {"x": [0.33], "y": [0]},
              "i": {"x": [0.67], "y": [1]}
            },
            {
              "t": 40,
              "s": [100, 100],
              "o": {"x": [0.55], "y": [0.055]},
              "i": {"x": [0.675], "y": [0.19]}
            },
            {"t": 60, "s": [100, 250]}
          ]
        },
        "s": {
          "a": 1,
          "k": [
            {
              "t": 0,
              "s": [100, 100],
              "o": {"x": [0.33], "y": [0]},
              "i": {"x": [0.67], "y": [1]}
            },
            {
              "t": 18,
              "s": [90, 110],
              "o": {"x": [0.33], "y": [0]},
              "i": {"x": [0.67], "y": [1]}
            },
            {
              "t": 20,
              "s": [120, 80],
              "o": {"x": [0.34], "y": [1.56]},
              "i": {"x": [0.64], "y": [1]}
            },
            {
              "t": 28,
              "s": [100, 100],
              "o": {"x": [0.33], "y": [0]},
              "i": {"x": [0.67], "y": [1]}
            },
            {"t": 60, "s": [100, 100]}
          ]
        },
        "r": {"a": 0, "k": 0},
        "o": {"a": 0, "k": 100}
      },
      "shapes": [
        {
          "ty": "gr",
          "it": [
            {
              "ty": "el",
              "p": {"a": 0, "k": [0, 0]},
              "s": {"a": 0, "k": [60, 60]}
            },
            {
              "ty": "fl",
              "c": {"a": 0, "k": [1, 0.5, 0, 1]},
              "o": {"a": 0, "k": 100}
            },
            {
              "ty": "tr",
              "p": {"a": 0, "k": [100, 250]},
              "s": {"a": 0, "k": [100, 100]},
              "r": {"a": 0, "k": 0},
              "o": {"a": 0, "k": 100}
            }
          ]
        }
      ]
    }
  ]
}
```

## 6. Staggered Elements

Multiple elements with staggered delays.

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
      "st": 0,
      "ip": 0,
      "op": 90,
      "ks": {
        "s": {
          "a": 1,
          "k": [
            {"t": 0, "s": [0, 0], "o": {"x": [0.34], "y": [1.56]}, "i": {"x": [0.64], "y": [1]}},
            {"t": 20, "s": [100, 100]}
          ]
        }
      },
      "shapes": [...]
    },
    {
      "ddd": 0,
      "ty": 4,
      "ind": 2,
      "nm": "Dot 2",
      "st": 5, // 5 frame offset
      "ip": 5,
      "op": 90,
      "ks": {
        "s": {
          "a": 1,
          "k": [
            {"t": 5, "s": [0, 0], "o": {"x": [0.34], "y": [1.56]}, "i": {"x": [0.64], "y": [1]}},
            {"t": 25, "s": [100, 100]}
          ]
        }
      },
      "shapes": [...]
    }
  ]
}
```

## 7. Organic Loader with Matte (Liquid Fill)

Simulates a liquid filling a circle using a Track Matte.

```json
{
  "v": "5.12.1",
  "fr": 60,
  "ip": 0,
  "op": 120,
  "w": 200,
  "h": 200,
  "nm": "Liquid Loader",
  "ddd": 0,
  "assets": [],
  "layers": [
    {
      "ind": 1,
      "ty": 4,
      "nm": "Matte_Circle",
      "td": 1,
      "ks": {
         "a": {"a":0, "k":[100,100]},
         "p": {"a":0, "k":[100,100]},
         "s": {"a":0, "k":[100,100]},
         "r": {"a":0, "k":0},
         "o": {"a":0, "k":100}
      },
      "shapes": [
        {
          "ty": "el",
          "p": {"a": 0, "k": [0, 0]},
          "s": {"a": 0, "k": [180, 180]}
        },
        {
          "ty": "fl",
          "c": {"a": 0, "k": [1, 1, 1, 1]},
          "o": {"a": 0, "k": 100}
        },
        {
           "ty": "tr",
           "p": {"a": 0, "k": [100, 100]}, 
           "s": {"a": 0, "k": [100, 100]},
           "r": {"a": 0, "k": 0},
           "o": {"a": 0, "k": 100}
        }
      ]
    },
    {
      "ind": 2,
      "ty": 4,
      "nm": "Liquid_Wave",
      "tt": 1,
      "ks": {
         "a": {"a":0, "k":[0,0]},
         "p": {
            "a":1, 
            "k": [
               {"t": 0, "s": [100, 220], "o": {"x":[0.33], "y":[0]}, "i": {"x":[0.67], "y":[1]}},
               {"t": 120, "s": [100, -20]}
            ]
         },
         "r": {"a":0, "k":0},
         "o": {"a":0, "k":100}
      },
      "shapes": [
         {
            "ty": "rc", 
            "p": {"a":0, "k":[0,0]},
            "s": {"a":0, "k":[300, 300]}, 
            "r": {"a":0, "k":20} 
         },
         {
             "ty": "fl", "c": {"a":0, "k":[0.2, 0.6, 1, 1]}, "o": {"a":0, "k":100}
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
  ]
}
```

## 8. Character Arm Wave (Parenting)

Hierarchical animation: Body -> Upper Arm -> Forearm -> Hand.

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
      "ind": 1,
      "nm": "Hand",
      "ty": 4,
      "parent": 2,
      "ks": {
        "a": {"a": 0, "k": [0, 0]},
        "p": {"a": 0, "k": [0, 100]}, 
        "r": {
           "a": 1,
           "k": [
              {"t": 0, "s": [-10]},
              {"t": 30, "s": [10]},
              {"t": 60, "s": [-10]}
           ]
        },
        "s": {"a": 0, "k": [100, 100]},
        "o": {"a": 0, "k": 100}
      },
      "shapes": []
    },
    {
      "ind": 2,
      "nm": "Forearm",
      "ty": 4,
      "parent": 3,
      "ks": {
        "a": {"a": 0, "k": [0, 0]},
        "p": {"a": 0, "k": [0, 120]}, 
        "r": {
           "a": 1,
           "k": [
              {"t": 0, "s": [5]},
              {"t": 30, "s": [-5]},
              {"t": 60, "s": [5]}
           ]
        },
        "s": {"a": 0, "k": [100, 100]},
        "o": {"a": 0, "k": 100}
      },
      "shapes": []
    },
    {
      "ind": 3,
      "nm": "UpperArm",
      "ty": 4,
      "ks": {
        "a": {"a": 0, "k": [0, 0]},
        "p": {"a": 0, "k": [250, 250]}, 
        "r": {
           "a": 1,
           "k": [
              {"t": 0, "s": [0]},
              {"t": 30, "s": [15]},
              {"t": 60, "s": [0]}
           ]
        },
        "s": {"a": 0, "k": [100, 100]},
        "o": {"a": 0, "k": 100}
      },
      "shapes": []
    }
  ]
}
```

## Tips for Using Examples

1. **Copy and Modify**: Use these as a base and adjust colors, timings, sizes.
2. **Combine**: Mix techniques (e.g., Stagger + Bounce).
3. **Scale**: Adjust `w`, `h` and positions proportionally.
4. **Timing**: Modify `fr` and `op` to change duration.
5. **Validate**: Always verify in [LottieFiles Preview](https://lottiefiles.com/preview).

## Duration Conversion

```
Duration (seconds) = (op - ip) / fr

Example:
- fr: 60, ip: 0, op: 120
- Duration = 120 / 60 = 2 seconds
```

# Contributing to Lottie Animator

First off, thank you for considering contributing to Lottie Animator! It's people like you that make this tool great for everyone.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (SVGs, expected output, actual output)
- **Include the Lottie JSON output** if relevant

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a step-by-step description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **Include examples** of how it would work

### Pull Requests

1. Fork the repo and create your branch from `main`
2. Make your changes
3. Run the checks below and make sure they pass
4. Submit a pull request

Every change must satisfy three gates, in this order:

```bash
python3 -m unittest discover -s tests   # unit tests
python3 scripts/lottie_lint.py examples/
npm install && node scripts/render.mjs examples/<your-file>.json
```

The third one is not optional and not automatable away: **open the filmstrip and look
at it.** A Lottie can lint clean and still paint nothing. If you are adding a lint
rule, add a test that fails without it.

## Project Structure

```
lottie-animator-skill/
├── .claude-plugin/       # Plugin configuration
├── .github/workflows/    # CI: tests, lint, and a real render
├── assets/               # preview.html, the README hero, and the example GIFs
├── docs/                 # Landing page
├── examples/             # Sample animations and their SVG sources
├── scripts/
│   ├── svg2lottie.py     # SVG -> Lottie shape layers
│   ├── svgpath.py        # Path grammar -> cubic beziers
│   ├── lottie_lint.py    # Structural and motion linting
│   ├── render.mjs        # Headless render + filmstrip
│   └── make-gifs.mjs     # README GIFs, built from the same renderer
├── skills/
│   └── lottie-animator/
│       ├── SKILL.md      # Main skill definition
│       └── references/   # Technical documentation
└── tests/                # Unit tests (stdlib only)
```

## Adding New Features

### New Animation Techniques

1. Document the technique in `references/professional-techniques.md`
2. Add an example to `examples/`
3. Update `SKILL.md` with usage instructions
4. Add to the examples reference

### New Easing Presets

1. Add to `references/bezier-easing.md`
2. Include visual representation
3. Document use cases

### New Examples

1. Prefer generating geometry with `svg2lottie.py` over hand-writing vertices
2. Create the Lottie JSON in `examples/`, keeping the SVG source alongside it
3. Confirm `lottie_lint.py` is clean and the filmstrip shows the intended motion
4. Document in `references/examples.md`

## Style Guidelines

### Lottie JSON

- Use 2-space indentation
- Include meaningful `nm` (name) properties on layers and shape groups
- Easing handles belong inside a keyframe, never on the property holding it
- Give every layer explicit `ip` and `op`
- Include every required property for a shape type; a missing one drops the layer

### Documentation

- Use clear, concise language
- Include code examples
- Add visual representations where helpful
- Keep tables formatted consistently

## Testing

The Python tools have no dependencies; rendering needs Node and a local Chrome
(`npm install`, then set `CHROME_PATH` if it is not in a standard location).

```bash
python3 -m unittest discover -s tests -v
python3 scripts/lottie_lint.py examples/ --strict
node scripts/render.mjs examples/panda-loader.json
```

For a browser preview, serve over HTTP — `file://` cannot fetch the JSON:

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/assets/preview.html`, or drop a file on
[LottieFiles Preview](https://lottiefiles.com/preview).

## Questions?

Feel free to open an issue for any questions about contributing!

---

Thank you for helping make Lottie Animator better!

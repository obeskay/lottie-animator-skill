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
3. Ensure your code follows the existing style
4. Test your changes with real SVG files
5. Submit a pull request

## Project Structure

```
lottie-animator-skill/
├── .claude-plugin/       # Plugin configuration
├── assets/               # Preview files
├── docs/                 # Landing page
├── examples/             # Sample animations
├── skills/
│   └── lottie-animator/
│       ├── SKILL.md      # Main skill definition
│       └── references/   # Technical documentation
└── test/                 # Test files
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

1. Create the Lottie JSON in `examples/`
2. Document in `references/examples.md`
3. Include SVG source if applicable

## Style Guidelines

### Lottie JSON

- Use 2-space indentation
- Include meaningful `nm` (name) properties
- Comment complex animations
- Follow existing keyframe structure

### Documentation

- Use clear, concise language
- Include code examples
- Add visual representations where helpful
- Keep tables formatted consistently

## Testing

Test your animations at:
- [LottieFiles Preview](https://lottiefiles.com/preview)
- Local preview: Open `assets/lottie-preview.html`

## Questions?

Feel free to open an issue for any questions about contributing!

---

Thank you for helping make Lottie Animator better!

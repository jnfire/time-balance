# Contributing to time-balance

First of all, thank you for considering contributing to `time-balance`! It's people like you that make the open-source community such an amazing place to learn, inspire, and create.

## How Can I Contribute?

### Reporting Bugs

- Check if the bug has already been reported in the Issues section.
- If not, open a new issue. Include a clear title, a description of the problem, and steps to reproduce it.

### Suggesting Enhancements

- Open an enhancement issue to discuss your idea before writing code.
- Explain why this feature would be useful and how it should work.

### Adding New Languages (i18n)

We want `time-balance` to be accessible to everyone. To add a new language:

1. Locate `time_balance/i18n.py`.
2. Find the `STRINGS` dictionary.
3. Copy the `"en"` dictionary as a template.
4. Add your language code (e.g., `"it"`, `"pt"`, `"de"`) and translate the values.
5. Submit a Pull Request with the title `feat(i18n): add [Language] support`.

### Improving Documentation

- Fix typos or grammatical errors.
- Clarify confusing sections.
- Translate documentation files to other languages.

## Development Process

1. **Fork the repo** and create your branch from `main`.
2. **Setup your environment** (Python 3.8+ recommended).
3. **Write your code** following the project's style (Clean Code, descriptive naming).
4. **Add tests** for any new functionality.
5. **Ensure all tests pass** with `python3 -m unittest discover tests`.
6. **Submit a Pull Request**.

## Pull Request Guidelines

- Use descriptive commit messages (e.g., `fix(core): improve balance calculation`).
- Update the `CHANGELOG.md` with your changes.
- Ensure the CI/CD pipeline passes.

## Style Guide

- Internal code (functions, variables, comments) MUST be in **English**.
- Use 4 spaces for indentation.
- Follow PEP 8 guidelines.
- Never use single-letter variable names (except in very obvious list comprehensions).

---

By contributing, you agree that your contributions will be licensed under its **GPL-3.0 License**.

# Contributing to time-balance

First of all, thank you for considering contributing to `time-balance`!

## How Can I Contribute?

### Reporting Bugs
- Check if the bug has already been reported.
- If not, open a new issue with a clear title and reproduction steps.

### Suggesting Enhancements
- Open an enhancement issue to discuss your idea before writing code.

### Adding New Languages (i18n)
We want `time-balance` to be accessible to everyone. Adding a new language is now easier than ever:

1. Navigate to `time_balance/i18n/locales/`.
2. Copy `en.json` to a new file named with your language code (e.g., `fr.json`, `de.json`).
3. Translate the values in the JSON file.
4. Submit a Pull Request.

### Improving Documentation
- Fix typos or grammatical errors.
- Translate documentation files to other languages.

## Development Process

1. **Fork the repo** and create your branch from `main`.
2. **Setup your environment** (Python 3.8+).
3. **Run in dev mode** using `./main.py`.
4. **Follow Style Standards**:
   - Internal code MUST be in **English**.
   - No single-letter variables (minimum 3 chars).
   - Use `ui.interface` for console input/output.
5. **Ensure tests pass**: `python3 -m unittest discover tests`.
6. **Submit a Pull Request**.

## Style Guide
- **Descriptive Naming**: Use names that explain intent (e.g., `active_project_id` instead of `id`).
- **Dry Logic**: Centralize data operations in the `database` domain.
- **UI Independence**: Never import `Rich` outside the `ui/` directory.

---

By contributing, you agree that your contributions will be licensed under the **GPL-3.0 License**.

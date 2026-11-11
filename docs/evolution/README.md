# Evolution

*Read this in [Spanish](README-es.md).*

How time-balance went from its first commit to its final version, why it exists, and what was tried and left out.

## The story

The time-tracking tool used at work was not transparent, and it was not simple to get one number from the worker's side of the desk: whether a day had been shorter or longer than it should have been, and how that added up over the weeks.

The answer was a small terminal tool that does only that. You say how long your day is supposed to be (the daily base), you type the hours and minutes you worked at the end of each day, and it tells you the difference and keeps a running balance. No accounts, no network, one SQLite file. Several projects, because the same person can have more than one base.

It grew from a script into a package with a database, translations and tests, but the idea stayed the same size. When the idea outgrew the terminal it started again as [time-tracker](https://time-tracker.jnfire.dev/), a web application you can install, and this repository was left as the clean, final version of the first experiment.

## Timeline

| When | What happened |
| --- | --- |
| January 2026 | First commit: a script to count the hours of a workday. |
| April 2026 | Version 0.5.0: SQLite storage, several projects, translations and a modular structure. |
| April 2026 | A live timer was tried on a separate branch (`live-tracking`) and left out. See below. |
| June 2026 | The idea outgrew the terminal and started again as time-tracker, a web application. |
| November 2026 | Cleanup and final release, 0.6.0: typed code, tests for every flow, translated screens and a documented data format. |

## An experiment that was left out

Between 26 and 27 April 2026, right after version 0.5.0, a branch tried a different way in: instead of typing the hours at the end of the day, a timer ran in the terminal. It had a real-time timer screen with pause and resume, a balance that updated while the timer ran, an automatic save every 60 seconds (minutes only) and a confirmation when cancelling. It was 8 commits and about 800 added lines, and it was never merged.

It was discarded because it was not really necessary. Typing the day at the end already answered the question. What was missing was not a smarter terminal, it was a tool you install and use every day with an accessible interface. That is what time-tracker became.

The code is kept so the attempt stays on record. [`docs/experiments/live-tracking.patch`](../experiments/live-tracking.patch) holds the changes of the branch to `time_balance/`, without its documentation:

```bash
git checkout 172562d          # version 0.5.0, the base of the branch
git apply docs/experiments/live-tracking.patch
```

The last commit of the branch was `3867dc0`.

## In numbers

| | Version 0.5.0 | Final version (0.6.0) |
| --- | --- | --- |
| Automated tests | 51 | 144 |
| Test coverage | 63% | 96% |
| Lint findings (ruff, with the rules the project uses now) | 488 | 0 |
| Type errors (mypy) | 16 | 0 |
| Python versions in CI | 1 (the latest) | 3.10 to 3.14 |

The "before" column is the state of the code just before the cleanup described above.

## Images

- [`dashboard-en.png`](../screenshots/dashboard-en.png): the dashboard
- [`history-en.png`](../screenshots/history-en.png): the history

# Why time-balance exists, and what was tried

## The problem

The time-tracking tool used at work was not transparent, and it was not simple to get one number from the worker's side of the desk: whether a day had been shorter or longer than it should have been, and how that added up over the weeks.

## The simple answer

A small terminal tool that does only that:

1. You say how long your day is supposed to be (the daily base).
2. At the end of each day you type the hours and minutes you worked.
3. It tells you the difference of that day and keeps a running balance: how many hours you are ahead or behind.

No accounts, no network, one SQLite file. Several projects, because the same person can have more than one base. Everything else in the code (the translations, the typed layers, the tests) is there to keep that idea small and clear.

## An experiment that was left out: the live timer

Between 26 and 27 April 2026, right after version 0.5.0, a branch called `live-tracking` tried a different way in: instead of typing the hours at the end of the day, a timer ran in the terminal.

What it contained (8 commits, about 800 added lines, never merged):

- A real-time timer screen with pause and resume.
- The balance updated while the timer ran, with the cache adjusted atomically.
- An automatic save every 60 seconds (minutes only, seconds were not stored).
- A confirmation when cancelling, and new translation keys in both languages.

It was discarded because it was not really necessary. Typing the day at the end already answered the question. What was missing was not a smarter terminal, it was a tool you install and use every day with an accessible interface. That is what time-tracker became, starting in June 2026.

## Where the code is

The work is kept so the attempt is on record:

- [`docs/experiments/live-tracking.patch`](experiments/live-tracking.patch) holds all the code of the branch (the `time_balance/` changes, without the documentation). To look at it:

  ```bash
  git checkout 172562d          # version 0.5.0, the base of the branch
  git apply docs/experiments/live-tracking.patch
  ```

- The last commit of the branch was `3867dc0`.

## What it led to

time-balance was the first sketch of [time-tracker](https://time-tracker.jnfire.dev/), a web application you can install, with tasks, real time blocks and an audit history. This repository stays as the clean, final version of that first experiment.

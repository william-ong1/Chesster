# Chesster

## Gamma Release

## User Documentation
[User Guide](USER_DOCUMENTATION.md)

## Developer Documentation
Obtain the source code by cloning the repo (git clone ...).

## Our Repository Structure

```text
/
├── .github/            # CI/CD workflows
├── app/                # Main application logic (API routes, game logic)
├── models/             # Stores trained models
├── maia-individual/    # Custom model training, evaluation, and base maia models
├── Tests/              # Unit and integration tests for backend logic
├── scripts/            # To assist with data cleaning and other utilities
├── StatusReports/      # Project documentation, progress and status reports
├── README.md           # Description on the application and how to build/test it
```

**Testing the system:**
- To install all required testing tools (requires Python and NodeJS):
```sh
npm i --save-dev vitest
npm i --save-dev @vitest/coverage-v8
pip install pytest
pip install coverage
```
- To run python tests with a coverage report:
```sh
coverage run -m pytest; coverage report -m
```
- To run TypeScript tests with a coverage report:
```sh
npm run test:coverage
```
- Alternative method for TypeScript tests:
```sh
vitest run --coverage
```
- CI: With GitHub Actions, all unit tests (Python and TypeScript) and their coverage reports are run on every push and pull request. A linter is also run over all code written by us (we exclude some config files that have a JavaScript or TypeScript file extension from the linter).
- `vitest`

## Overview

Allows users to upload their past chess data and then trains a chess bot with this data such that it learns to mimic their playstyle. The user can then play against this bot when they want. 

## Goals

- Learn and replicate individual player playstyles
- Enable users to play against a bot modeled after themselves
- Help users identify weaknesses and mistakes they make

---

## How It Works

1. **Data Upload**  
   Users upload previous chess games in chess notation.

2. **Preprocessing**  
   Chess data, in chess notation text, is processed and converted into board states with each state labeled with the move taken.

3. **Training**  
   Processed data is given to a model to be trained to predict the most probable move for a given board state.

4. **Inference**  
   - For Known positions,  bot selects the user’s most common move  
   - For Unknown positions, bot extrapolates using similar board states

5. **Gameplay**  
   Users play against their trained bot.

---

## Our Document

**[Chesster Document](https://docs.google.com/document/d/1vwO41rhAHU9qlyoL9fNLt6wjTwUivhy5ou2r9YIWVBE/edit?tab=t.0#heading=h.1ruhqhxj255p)**

---

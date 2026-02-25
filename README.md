# Chesster

## Beta Release
The use cases that are functional for our beta release are: 
1. User can upload their personal chess data for the bot to train on
2. User can see all legal moves when playing a game
3. An entire chess game can be played from start to finish with legal moves

We are actively working on integrating the training feature into our application. 

## How to Build and Test the system

1. Open frontend/index.html
2. Download it to your local computer
3. Open it with a web browser (ensure Javascript is enabled in that browser)
4. Play chess!

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

## Our Repository Structure

```text
/
├── frontend/     # Chess GUI and user interaction
├── backend/      # APIs, authentication, data upload/storage
├── data/         # Data preprocessing
├── ML/           # Chess bot logic and training
├── Tests/        # Tests for application components
├── docs/         # Technical documentation
└── README.md     # Project overview

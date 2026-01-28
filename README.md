# Chesster

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

**[Chesster Document]([docs/living-document.md](https://docs.google.com/document/d/1vwO41rhAHU9qlyoL9fNLt6wjTwUivhy5ou2r9YIWVBE/edit?pli=1&tab=t.0))**

---

## Our Repository Structure

```text
/
├── frontend/     # Chess GUI and user interaction
├── backend/      # APIs, authentication, data storage
├── bots/         # Chess bot logic and training
├── models/       # trained models and configs
├── data/         # Data preprocessing
├── docs/         # Technical documentation
└── README.md     # Project overview

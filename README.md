# Chesster

## Overview

Allows users to upload their past chess data and then trains a chess bot with this data such that it learns to mimic their playstyle. The user can then play against this bot when they want. 

## Goals

- Learn and replicate individual player playstyles
- Enable users to play against a bot modeled after themselves
- Help users identify weaknesses and recurring mistakes
- Allow experimentation against playstyles that counter the user’s own
- Provide an engaging and personalized chess training experience

---

## How It Works

1. **Data Upload**  
   Users upload previous chess games in algebraic notation.

2. **Preprocessing**  
   A custom chess data preprocessor converts game notation into board states and labels each state with the move taken.

3. **Training**  
   Processed data is fed into a machine learning model trained to predict the most probable move for a given board state.

4. **Inference**  
   - Known positions → bot selects the user’s most common move  
   - Unknown positions → bot extrapolates using similar board states

5. **Gameplay**  
   Users play against their trained bot.

---

## 📄 Our Document

➡️ **[Chesster Document]([docs/living-document.md](https://docs.google.com/document/d/1vwO41rhAHU9qlyoL9fNLt6wjTwUivhy5ou2r9YIWVBE/edit?pli=1&tab=t.0))**

---

## 🗂️ Repository Structure

```text
/
├── frontend/     # Chess GUI and user interaction
├── backend/      # APIs, authentication, data storage
├── bots/         # Chess bot logic and training code
├── models/       # Machine learning models and configs
├── data/         # Data preprocessing and schemas
├── docs/         # TEchnical documentation
└── README.md     # Project overview

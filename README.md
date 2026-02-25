# Chesster

## Gamma Release

## User Documentation
[User Guide](USER_DOCUMENTATION.md)

## Developer Documentation
[Developer Guide](DEVELOPER_DOCUMENTATION.md)
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

## AI Disclaimer
AI was used for configuration files and UI formatting for this project. We also used AI as a starting point for our tests, but modified the code to verify the validity of the tests and to suit our project's needs.


**[Chesster Document](https://docs.google.com/document/d/1vwO41rhAHU9qlyoL9fNLt6wjTwUivhy5ou2r9YIWVBE/edit?tab=t.0#heading=h.1ruhqhxj255p)**

---
## Gamma Release Tag
**Gamma Tag ID (1 hour late):** 122824562302d2699cf0f7e93247b9183f39777b
(Please grade this one if possible, we needed only one extra hour to finish)

**Gamma Tag ID (On-Time):** b31d31d7d4fe1f05ae5e3e08501c02b2ce89bf06
(In case the late one can't be graded for credit)

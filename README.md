# Chesster

## Documentation
### User Documentation
[User Guide](https://docs.google.com/document/d/1fhgFQ0q_iIjsCposVSkGihsz5ofvjDJe07hAGC5pVm0/edit?tab=t.0)

### Developer Documentation
[Developer Guide](https://docs.google.com/document/d/14J1EzREBiGWFm7s0mDv4Xl-arWvJFn0pm5AYJfUlh_0/edit?tab=t.0#heading=h.l1ejxsbujjuj)

### Living Document
[Chesster Document](https://docs.google.com/document/d/1vwO41rhAHU9qlyoL9fNLt6wjTwUivhy5ou2r9YIWVBE/edit?tab=t.0#heading=h.1ruhqhxj255p)

---

## Overview

Allows users to upload their past chess data and then trains a chess bot with this data such that it learns to mimic their playstyle. The user can then play against this bot when they want. 

---

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

## Architecture Diagram
<img width="543" height="720" alt="Image" src="https://github.com/user-attachments/assets/8dead6b8-cb7f-491f-bc20-ee256a25b3d2" />

---

## AI Disclaimer
AI was used for configuration files and UI formatting for this project. We also used AI as a starting point for our tests, but modified the code to verify the validity of the tests and to suit our project's needs.

---

## Release Tags
**Beta Release Tag:** beta-release
**Gamma Release Tag:** gamma-release-late
**Final Release Tag:** final-release

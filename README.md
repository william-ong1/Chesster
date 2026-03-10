# Chesster

## Documentation
### User Documentation
[User Documentation](https://docs.google.com/document/d/1fhgFQ0q_iIjsCposVSkGihsz5ofvjDJe07hAGC5pVm0/edit?tab=t.0)

### Developer Documentation
[Developer Documentation](https://docs.google.com/document/d/14J1EzREBiGWFm7s0mDv4Xl-arWvJFn0pm5AYJfUlh_0/edit?tab=t.0#heading=h.l1ejxsbujjuj)

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

## Completed Features and Functionality
- **PGN Upload:**
  The user uploads a PGN file containing their chess games.

- **PGN Cleaning and Game Processing:**
  Our system removes incomplete or invalid games, including format standardization. Games are then converted into a structured format for our training.

- **Local Data Storage:**
  Board states for each user are saved in local storagein a database on the backend so that each bot can be trained on a dataset unique to each user.

- **Style Learning:**
  Chesster analyzes and mimics one’s playstyle patterns such as opening plays, common moves, move preferences, and game progression habits. In normal mode, training can take upwards of 1 day depending on hardware. Use *Quick Train* mode to train a less accurate model in 20-25 minutes.

- **Training Output & Model Evaluation:**
  View the progress of the bot you're training. Also displays the policy and value accuracy of the bot during training.

- **Play Against a Bot:**
  Users can choose to play against their personalized chess bot or a pre-trained model!

- **Cross-Platform:**
  Chesster was built using Docker and Electron, and runs on Windows, MacOS, and Linux machines.

- **Accessibility:**
  Each page of the app has semantic labels, uses proper heading structure, and can be navigated with a Screen Reader using only keyboard commands.

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
**Final Release Tag:** final-release

**Gamma Release Tag:** gamma-release-late

**Beta Release Tag:** beta-release

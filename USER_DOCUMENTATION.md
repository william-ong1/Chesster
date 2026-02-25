# User Documentation

## 1. High-Level Description of the Software

Chesster is designed to help players analyze and improve their chess by creating a personalized opponent. The application works through the following pipeline:

1. **PGN Import**
   - The user uploads a PGN file containing their chess games.

2. **PGN Cleaning**
   - The system removes incomplete or invalid games.
   - Standardizes formatting and prepares the data.

3. **Game Processing**
   - Games are converted into a structured format that can be used for training.

4. **Style Learning**
   - Chesster analyzes patterns such as:
     - Opening choices
     - Common tactics
     - Move preferences
     - Game progression habits

5. **Chess Bot Generation**
   - A chess bot is created that mirrors the user's playing style.

6. **User Interaction**
   - The user can play games against their personalized chess bot.
   - Alternatively, choose a pre-trained model to play against
   - All features required to play a standard game of chess are present

## 2. Installing Chesster
Users will need to navigate to our landing page (tbd) and download our application.

## 3. Getting Started (UI Guide) 
  This section explaines how to use the Chesster interface. 

- There are three main tabs: Train, Play, and System Check
- You don't need to pay much attention to system check - if it is all green, you're good. If not, file a bug report by creating an issue on our Github page or by emailing s99s42m@uw.edu.
- In the Train tab, upload a PGN file of your games. The more games, the better. If you are a Chess.com or Lichess user, you can download a PGN of your game history from the website and then upload that. Then enter your elo and the player name (must match name used in the PGN file). Click "Train" and wait for the output terminal that appears on the right to tell you that training is complete. This might take 10-20 minutes. In the meantime, you can move the app to the background and do other things.
- In the play tab, choose a model to play against (can be a model you just trained or some default base models). Choose whether to play as white and black, and click Load Engine. After the engine has been loaded, click New Game. Enjoy!


## 4. Reporting Bugs
File a bug report by creating an issue on our Github page or by emailing s99s42m@uw.edu. Please include:
- Precise steps to reproduce the bug
- If you can't reproduce the bug or can only occasionally reproduce the bug, provide any information about when the bug occurs
- Describe what you expected to see vs what you actually saw

## 5. Known Bugs
- The app fails to build on certain Windows devices.
- Occasionally, the initial load engine doesn’t work and times out after in 8 seconds.
- Usually, attempting to build/load again will resolve these errors temporarily

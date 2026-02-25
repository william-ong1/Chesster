# User Documentation
---

# 1. High-Level Description of the Software

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

---

# 2. Installing Chesster

 -  git clone https://github.com/chesster.git
 -    cd chesster
   
# 3. Verify Installation
  </> Bash
  python main.py

  If successful, the UI should start.

# 4. Getting Started (UI Guide) 
  This section explaines how to use the Chesster interface. 

 **Step 1 - Open Chesster**
   When the system starts, you will see: 

  - Chesster Dashboard

  - Main sections:

    - Upload Games
    - Train Bot
    - Play Against Chesster
    - Game History

  # Step 2 - UPload Your Games

  Click : </> Code 
    upload PGN
    Then: - Select your PGN File
          - Upload it
          - The system begins processing


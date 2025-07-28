# Python Rhythm Typing Game
A simple but addictive rhythm-based typing game built with Python and the PyQt6 framework. Test your typing speed and accuracy as letters fall down the screen. Hit them at the right moment to rack up points, build your combo, and compete for the high score!

## Features
Fast-Paced Gameplay: Single letters fall from the top of the screen, and you must press the corresponding key as they cross the hit line.

Timed Sessions: Each game lasts for 60 seconds, making it a perfect quick challenge.

Scoring and Combos: Earn points for each successful hit and build a combo multiplier for consecutive successful hits.

Persistent High Scores: The game saves the top 5 scores in a local high_scores.json file, so you can compete against yourself and others.

Easy to Customize: A central Config class allows for easy modification of game parameters like speed, spawn rate, and game duration.

Clean UI: A simple and clean user interface that switches between the game screen and a "Game Over" screen for score entry.

Requirements
To run this game, you will need the following installed on your system:

Python 3.x

PyQt6

## Installation & Setup
Clone the repository:

git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
cd YOUR_REPOSITORY_NAME

Install the required Python library:
Open your terminal or command prompt and run the following command to install PyQt6.

pip install PyQt6

## How to Play
Run the application:
Execute the main Python script from your terminal.

```
python rhythm_game.py
```


### Gameplay:

The game will start immediately.

Letters will begin falling from the top of the screen.

Press the corresponding key on your keyboard just as the letter passes over the cyan hit line at the bottom.

A successful hit will turn the letter green and increase your score and combo.

Missing a letter will turn it red, increase your miss count, and reset your combo.

The game ends after 60 seconds.

### Saving Your Score:

After the game ends, you will be taken to the "Game Over" screen.

Enter your name in the input box and click "Save Score".

Your score will be added to the high score list if it's in the top 5.

Click "Play Again" to start a new game.

## Customizing the Game
This project was designed to be easily configurable. All major game variables are located in the Config class at the top of the script. You can tweak these values to change the game's difficulty and feel.

```
--- Configuration ---
class Config:
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    HIT_LINE_Y = 500
    WORD_SPEED = 3.0  # How fast the letters fall. Increase for more difficulty.
    WORD_SPAWN_RATE = 500 # Time in milliseconds between new letters. Decrease for more letters.
    FONT_SIZE = 30
    HIT_TOLERANCE = 25 # The "hit window" in pixels. Increase for an easier game.
    GAME_DURATION_SECONDS = 60 # Change the length of a game session.
    HIGH_SCORE_FILE = "high_scores.json"
    MAX_HIGH_SCORES = 5

    # You could even change this back to words or add numbers/symbols!
    WORD_LIST = list("abcdefghijklmnopqrstuvwxyz")
```

### Examples of Customization:
To make the game harder: Increase WORD_SPEED and decrease WORD_SPAWN_RATE.

To make the game easier: Decrease WORD_SPEED and increase HIT_TOLERANCE.

To create a "marathon" mode: Increase GAME_DURATION_SECONDS to a much larger number.

To add numbers to the game: Change WORD_LIST to list("abcdefghijklmnopqrstuvwxyz0123456789").

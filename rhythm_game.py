import sys
import random
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QLabel, QPushButton, QLineEdit, QStackedWidget,
                             QHBoxLayout, QFormLayout)
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QFontMetrics
from PyQt6.QtCore import Qt, QTimer, QPointF, pyqtSignal

# --- Configuration ---
class Config:
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    HIT_LINE_Y = 500
    WORD_SPEED = 3.0  # Slightly faster for single letters
    WORD_SPAWN_RATE = 500 # Spawn letters more frequently
    FONT_SIZE = 30
    HIT_TOLERANCE = 25
    GAME_DURATION_SECONDS = 60 # The game lasts for 60 seconds
    HIGH_SCORE_FILE = "high_scores.json"
    MAX_HIGH_SCORES = 5

    # The game now uses single letters from the alphabet
    WORD_LIST = list("abcdefghijklmnopqrstuvwxyz")

# Represents a single falling letter on the screen
class FallingLetter:
    def __init__(self, letter, x_pos):
        self.letter = letter.lower()
        self.pos = QPointF(x_pos, -Config.FONT_SIZE) # Start off-screen
        self.is_hit = False
        self.is_missed = False

    def move(self):
        """Moves the letter down the screen."""
        if not self.is_hit:
            self.pos.setY(self.pos.y() + Config.WORD_SPEED)

    def draw(self, painter):
        """Draws the letter on the screen."""
        if self.is_hit:
            painter.setPen(QColor("lime"))
        elif self.is_missed:
            painter.setPen(QColor("red"))
        else:
            painter.setPen(QColor("white"))
        painter.drawText(self.pos, self.letter)

# The main widget where the game is rendered and played
class GameWidget(QWidget):
    # Signal emitted when the game ends, carrying the final score
    gameOver = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Set up a font for drawing text
        self.game_font = QFont("Consolas", Config.FONT_SIZE, QFont.Weight.Bold)
        self.font_metrics = QFontMetrics(self.game_font)

        # Main game loop timer
        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self.update_game)

        # Timer to spawn new words
        self.word_spawn_timer = QTimer(self)
        self.word_spawn_timer.timeout.connect(self.spawn_letter)
        
        # Timer for the overall game duration
        self.game_duration_timer = QTimer(self)
        self.game_duration_timer.timeout.connect(self.update_game_time)

    def start_game(self):
        """Initializes game state and starts all timers."""
        self.falling_letters = []
        self.score = 0
        self.misses = 0
        self.combo = 0
        self.time_left = Config.GAME_DURATION_SECONDS
        
        self.game_timer.start(16)  # ~60 FPS
        self.word_spawn_timer.start(Config.WORD_SPAWN_RATE)
        self.game_duration_timer.start(1000) # Update time every second
        self.setFocus()

    def stop_game(self):
        """Stops all game timers."""
        self.game_timer.stop()
        self.word_spawn_timer.stop()
        self.game_duration_timer.stop()

    def update_game_time(self):
        """Counts down the game time and ends the game when it reaches zero."""
        self.time_left -= 1
        if self.time_left <= 0:
            self.stop_game()
            self.gameOver.emit(self.score)
        self.update() # Redraw to show new time

    def spawn_letter(self):
        """Creates a new random letter and adds it to the game."""
        letter_text = random.choice(Config.WORD_LIST)
        letter_width = self.font_metrics.horizontalAdvance(letter_text)
        max_x = self.width() - letter_width
        start_x = random.randint(20, max(21, max_x))
        
        new_letter = FallingLetter(letter_text, start_x)
        self.falling_letters.append(new_letter)

    def update_game(self):
        """The main game loop."""
        letters_to_remove = []
        for letter in self.falling_letters:
            letter.move()

            # Check for misses
            if not letter.is_hit and not letter.is_missed:
                if letter.pos.y() > Config.HIT_LINE_Y + Config.HIT_TOLERANCE:
                    letter.is_missed = True
                    self.misses += 1
                    self.combo = 0

            # Clean up letters that are off screen
            if letter.pos.y() > self.height():
                letters_to_remove.append(letter)

        for letter in letters_to_remove:
            self.falling_letters.remove(letter)

        self.update()

    def paintEvent(self, event):
        """Handles all drawing for the game."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor("#1c1c24"))

        pen = QPen(QColor("cyan"))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawLine(0, Config.HIT_LINE_Y, self.width(), Config.HIT_LINE_Y)

        painter.setFont(self.game_font)
        for letter in self.falling_letters:
            letter.draw(painter)
        
        self.draw_ui(painter)

    def draw_ui(self, painter):
        """Draws the user interface elements."""
        painter.setPen(QColor("white"))
        painter.setFont(QFont("Arial", 16))
        
        painter.drawText(10, 30, f"Score: {self.score}")
        painter.drawText(10, 60, f"Misses: {self.misses}")
        
        time_text = f"Time: {self.time_left}"
        time_width = painter.fontMetrics().horizontalAdvance(time_text)
        painter.drawText(self.width() // 2 - time_width // 2, 30, time_text)

        combo_text = f"Combo: {self.combo}x"
        combo_width = painter.fontMetrics().horizontalAdvance(combo_text)
        painter.drawText(self.width() - combo_width - 10, 30, combo_text)

    def keyPressEvent(self, event):
        """Handles keyboard input from the player."""
        pressed_key = event.text().lower()
        if not pressed_key or not pressed_key.isalpha() or len(pressed_key) > 1:
            return

        hit_found = False
        # Find the lowest letter on screen that matches the key
        best_target = None
        for letter in self.falling_letters:
            if letter.letter == pressed_key and not letter.is_hit and not letter.is_missed:
                distance_from_line = abs(letter.pos.y() - Config.HIT_LINE_Y)
                if distance_from_line <= Config.HIT_TOLERANCE:
                    if best_target is None or letter.pos.y() > best_target.pos.y():
                        best_target = letter
        
        if best_target:
            best_target.is_hit = True
            self.score += 10 * (1 + self.combo // 10)
            self.combo += 1
            hit_found = True

        if not hit_found:
            self.misses += 1
            self.combo = 0

# Widget for the "Game Over" screen and high score entry
class GameOverWidget(QWidget):
    playAgain = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.final_score = 0
        self.init_ui()

    def init_ui(self):
        """Sets up the UI elements for the game over screen."""
        self.setStyleSheet("""
            QLabel { font-size: 24px; color: white; }
            QPushButton { font-size: 18px; padding: 10px; background-color: #007acc; color: white; border-radius: 5px; }
            QPushButton:hover { background-color: #005f9e; }
            QLineEdit { font-size: 18px; padding: 8px; border-radius: 5px; }
        """)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        self.title_label = QLabel("Game Over")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 48px; font-weight: bold;")

        self.score_label = QLabel()
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # High score entry form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(10)
        form_layout.addRow(QLabel("Enter Name:"), self.name_input)
        
        self.save_button = QPushButton("Save Score")
        self.save_button.clicked.connect(self.save_and_show_scores)

        # High score display
        self.high_score_title = QLabel("High Scores")
        self.high_score_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.high_score_list = QLabel()
        self.high_score_list.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.play_again_button = QPushButton("Play Again")
        self.play_again_button.clicked.connect(self.playAgain.emit)

        layout.addWidget(self.title_label)
        layout.addWidget(self.score_label)
        layout.addLayout(form_layout)
        layout.addWidget(self.save_button)
        layout.addWidget(self.high_score_title)
        layout.addWidget(self.high_score_list)
        layout.addWidget(self.play_again_button)

    def set_screen(self, score):
        """Prepares the screen with the final score and high scores."""
        self.final_score = score
        self.score_label.setText(f"Final Score: {self.final_score}")
        self.name_input.setText("")
        self.name_input.setEnabled(True)
        self.save_button.setEnabled(True)
        self.load_high_scores()

    def load_high_scores(self):
        """Loads scores from the JSON file and displays them."""
        if not os.path.exists(Config.HIGH_SCORE_FILE):
            self.high_score_list.setText("No high scores yet!")
            return []

        try:
            with open(Config.HIGH_SCORE_FILE, 'r') as f:
                scores = json.load(f)
        except (json.JSONDecodeError, IOError):
            scores = []
        
        display_text = ""
        for i, entry in enumerate(scores):
            display_text += f"{i+1}. {entry['name']} - {entry['score']}\n"
        
        self.high_score_list.setText(display_text.strip())
        return scores

    def save_and_show_scores(self):
        """Saves the new score and reloads the high score display."""
        name = self.name_input.text().strip()
        if not name:
            name = "Player"

        scores = self.load_high_scores()
        scores.append({"name": name, "score": self.final_score})
        
        # Sort scores descending and keep the top N
        scores.sort(key=lambda x: x['score'], reverse=True)
        scores = scores[:Config.MAX_HIGH_SCORES]

        try:
            with open(Config.HIGH_SCORE_FILE, 'w') as f:
                json.dump(scores, f, indent=4)
        except IOError as e:
            print(f"Error saving high scores: {e}")
        
        self.name_input.setEnabled(False)
        self.save_button.setEnabled(False)
        self.load_high_scores() # Reload to show the new list

# Main window to manage different screens (game, game over)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rhythm Typing Game")
        self.setGeometry(100, 100, Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        self.setStyleSheet("background-color: #1c1c24;")

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.game_widget = GameWidget()
        self.game_over_widget = GameOverWidget()

        self.stacked_widget.addWidget(self.game_widget)
        self.stacked_widget.addWidget(self.game_over_widget)

        # Connect signals between widgets
        self.game_widget.gameOver.connect(self.show_game_over)
        self.game_over_widget.playAgain.connect(self.show_game)

        self.show_game()

    def show_game(self):
        """Switches to the game screen and starts a new game."""
        self.stacked_widget.setCurrentWidget(self.game_widget)
        self.game_widget.start_game()

    def show_game_over(self, score):
        """Switches to the game over screen."""
        self.stacked_widget.setCurrentWidget(self.game_over_widget)
        self.game_over_widget.set_screen(score)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

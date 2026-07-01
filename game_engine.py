# Board Generation
import random
from collections import Counter
from word_utils import WORDS
from datetime import datetime


def get_daily_seed():
    return datetime.utcnow().strftime("%Y-%m-%d")


def has_enough_words(board, min_words=8):
    valid_words = 0
    board_letters = Counter(letter.lower() for letter in board)

    for word in WORDS:
        if len(word) < 3 or len(word) > 8:
            continue

        word_letters = Counter(word)

        if all(board_letters[l] >= c for l, c in word_letters.items()):
            valid_words += 1

        if valid_words >= min_words:
            return True

    return False


def generate_board(seed=None, size=4):
    letter_weights = {
        "A": 8.2, "B": 1.5, "C": 2.8, "D": 4.3,
        "E": 12.7, "F": 2.2, "G": 2.0, "H": 6.1,
        "I": 7.0, "J": 0.15, "K": 0.8, "L": 4.0,
        "M": 2.4, "N": 6.7, "O": 7.5, "P": 1.9,
        "Q": 0.10, "R": 6.0, "S": 6.3, "T": 9.1,
        "U": 2.8, "V": 1.0, "W": 2.4, "X": 0.15,
        "Y": 2.0, "Z": 0.07
    }

    vowels = {"A", "E", "I", "O", "U"}
    rare_letters = {"Q", "X", "Z", "J"}
    rng = random.Random(seed)

    letters = list(letter_weights.keys())
    weights = list(letter_weights.values())

    while True:
        board = rng.choices(letters, weights=weights, k=size * size)

        counts = Counter(board)
        vowel_count = sum(letter in vowels for letter in board)
        rare_count = sum(letter in rare_letters for letter in board)

        if not (4 <= vowel_count <= 8):
            continue

        if max(counts.values()) > 3:
            continue

        if rare_count > 1:
            continue

        if has_enough_words(board):
            return board


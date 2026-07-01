# Dictionary and Word Validation
with open("words.txt", "r", encoding="utf-8") as f:
    WORDS = set()

    for line in f:
        word = line.strip().lower()

        if word.isalpha():
            WORDS.add(word)

CUSTOM_WORDS = {
    "oats", "dots", "dot", "oat", "sat", "sod",
    "dog", "dogs", "cat", "cats", "rat", "rats",
    "bird", "code", "game", "play", "tree", "fish",
    "moon", "star", "book"
}

WORDS.update(CUSTOM_WORDS)


def check_word_status(word):
    word = word.lower().strip()

    if len(word) < 3:
        return {
            "valid": False,
            "reason": "too_short",
            "message": "Word must be at least 3 letters."
        }

    if word not in WORDS:
        return {
            "valid": False,
            "reason": "not_dictionary",
            "message": "Not in dictionary."
        }

    return {
        "valid": True,
        "reason": "valid",
        "message": f"+{len(word) * 10} points!",
        "score": len(word) * 10
    }
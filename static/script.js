// Game elements
const board = document.getElementById("board");
const currentWordDisplay = document.getElementById("currentWord");
const foundWordsList = document.getElementById("foundWords");
const timerDisplay = document.getElementById("timer");
const scoreDisplay = document.getElementById("scoreDisplay");
const StreakDisplay = document.getElementById("StreakDisplay");
const wordMessage = document.getElementById("wordMessage");
const gameOverModal = document.getElementById("gameOverModal");
const finalScore = document.getElementById("finalScore");
const finalWords = document.getElementById("finalWords");
const finalStreak = document.getElementById("finalStreak");

// Game state
let currentWord = "";
let selectedTiles = [];
let foundWords = [];
let score = 0;
let streak = 0;
let longestStreak = 0;
let isDragging = false;
let gameSaved = false;
let gameEnded = false;
let timeLeft = 90;
let countdown;

// Start game
function startGame() {
    if (!board) return;

    board.addEventListener("mousedown", startSelection);
    board.addEventListener("mouseover", continueSelection);
    document.addEventListener("mouseup", finishSelection);

    updateTimer();
    countdown = setInterval(updateTimer, 1000);
}

// Start selecting letters
function startSelection(event) {
    if (gameEnded) return;
    if (!event.target.classList.contains("tile")) return;

    resetSelection();
    isDragging = true;
    selectTile(event.target);
}

// Continue selecting letters
function continueSelection(event) {
    if (gameEnded) return;
    if (!isDragging) return;
    if (!event.target.classList.contains("tile")) return;

    selectTile(event.target);
}

// Finish selecting letters
function finishSelection() {
    if (gameEnded) return;
    if (!isDragging) return;

    isDragging = false;

    if (currentWord.length >= 2) {
        submitWord();
    } else {
        resetSelection();
    }
}

// Select one tile
function selectTile(tile) {
    if (selectedTiles.includes(tile)) return;

    const lastTile = selectedTiles[selectedTiles.length - 1];

    if (lastTile && !isAdjacent(lastTile, tile)) {
        return;
    }

    tile.classList.add("selected");
    selectedTiles.push(tile);

    currentWord += tile.textContent.toLowerCase();
    currentWordDisplay.textContent = currentWord.toUpperCase();
}

// Check adjacency
function isAdjacent(tile1, tile2) {
    const index1 = Number(tile1.dataset.index);
    const index2 = Number(tile2.dataset.index);

    const row1 = Math.floor(index1 / 4);
    const col1 = index1 % 4;

    const row2 = Math.floor(index2 / 4);
    const col2 = index2 % 4;

    return Math.abs(row1 - row2) <= 1 && Math.abs(col1 - col2) <= 1;
}

// Submit selected word
async function submitWord() {
    if (foundWords.includes(currentWord)) {
        resetStreak();
        showMessage(`"${currentWord.toUpperCase()}" was already found.`, "invalid");
        resetSelection();
        return;
    }

    const response = await fetch("/check-word", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ word: currentWord })
    });

    const data = await response.json();

    if (data.valid) {
        foundWords.push(currentWord);
        addFoundWord(currentWord);
        updateScore(data.score);
        updateStreak();
        showMessage(data.message, "valid");
    } else {
        resetStreak();
        showMessage(data.message, "invalid");
    }

    resetSelection();
}

// Add word to found words list
function addFoundWord(word) {
    const li = document.createElement("li");
    li.textContent = word.toUpperCase();
    foundWordsList.appendChild(li);
}

// Add points
function updateScore(points) {
    score += points;
    scoreDisplay.textContent = score;
}

// Update streak
function updateStreak() {
    streak++;

    if (streak > longestStreak) {
        longestStreak = streak;
    }

    StreakDisplay.textContent = streak;
}

// Reset streak
function resetStreak() {
    streak = 0;
    StreakDisplay.textContent = streak;
}

// Show valid/invalid messages
function showMessage(message, type) {
    wordMessage.textContent = message;
    wordMessage.className = type === "valid" ? "valid-message" : "invalid-message";

    setTimeout(() => {
        wordMessage.textContent = "";
        wordMessage.className = "";
    }, 1500);
}

// Reset selected tiles
function resetSelection() {
    currentWord = "";
    selectedTiles = [];
    currentWordDisplay.textContent = "";

    document.querySelectorAll(".tile").forEach(tile => {
        tile.classList.remove("selected");
    });
}

// Timer
function updateTimer() {
    if (gameEnded) return;

    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;

    timerDisplay.textContent =
        `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;

    if (timeLeft <= 0) {
        endGame();
        return;
    }

    timeLeft--;
}

// Save game to database
async function saveGame() {
    if (gameSaved) return;

    gameSaved = true;

    const gameType = board.dataset.gameType || "single";

    await fetch("/save-game", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            score: score,
            words_found: foundWords.length,
            longest_streak: longestStreak,
            game_type: gameType
        })
    });
}

// End game
async function endGame() {
    gameEnded = true;
    clearInterval(countdown);

    await saveGame();

    finalScore.textContent = score;
    finalWords.textContent = foundWords.length;
    finalStreak.textContent = longestStreak;

    gameOverModal.classList.remove("hidden");
}

startGame();
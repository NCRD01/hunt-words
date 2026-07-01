# Routes and Flask
from flask import Flask, render_template, request, redirect, jsonify
from flask_login import LoginManager, login_user, login_required, current_user, logout_user

from extensions import db, bcrypt
from models import User, GameResult
from game_engine import generate_board, get_daily_seed
from word_utils import check_word_status
import re

app = Flask(__name__)

app.config["SECRET_KEY"] = "super-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "index"

def validate_username(username):
    if len(username) < 3 or len(username) > 20:
        return False
    if not re.match(r"^[A-Za-z0-9_]+$", username):
        return False
    return True

def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def index():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        return redirect("/home")

    return render_template("login.html", invalidLogin=True)


@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]

    if User.query.filter_by(username=username).first():
        return render_template("login.html", usernameTaken=True)

    if not validate_username(username):
        return render_template("login.html", invalidUsername=True)

    if not validate_password(password):
        return render_template("login.html", invalidPassword=True)

    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(username=username, password=hashed_pw)

    db.session.add(user)
    db.session.commit()

    login_user(user)
    return redirect("/home")


@app.route("/home")
@login_required
def home():
    return render_template("home.html", username=current_user.username)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/game")
@login_required
def game():
    board_letters = generate_board()

    return render_template(
        "game.html",
        board_letters=board_letters,
        game_type="single"
    )

@app.route("/daily-puzzle")
@login_required
def daily_puzzle():
    seed = get_daily_seed()

    already_played = GameResult.query.filter_by(
        user_id=current_user.id,
        game_type="daily",
        daily_seed=seed
    ).first()

    if already_played:
        return render_template(
            "game.html",
            board_letters=[],   # or None
            game_type="daily",
            locked=True,
            final_score=already_played.score,
            final_words=already_played.words_found,
            final_streak=already_played.longest_streak
        )

    board_letters = generate_board(seed)

    return render_template(
        "game.html",
        board_letters=board_letters,
        game_type="daily",
        locked=False
    )

@app.route("/check-word", methods=["POST"])
@login_required
def check_word():
    data = request.get_json()
    word = data.get("word", "")

    return jsonify(check_word_status(word))


@app.route("/save-game", methods=["POST"])
@login_required
def save_game():
    data = request.get_json()

    score = data.get("score", 0)
    words_found = data.get("words_found", 0)
    longest_streak = data.get("longest_streak", 0)
    game_type = data.get("game_type", "single")

    
    if game_type == "daily":
        seed = get_daily_seed()

        existing = GameResult.query.filter_by(
            user_id=current_user.id,
            game_type="daily",
            daily_seed=seed
        ).first()

        if existing:
            return jsonify({
                "success": False,
                "message": "Already completed today"
            }), 403
        
    game_result = GameResult(
        user_id=current_user.id,
        score=score,
        longest_streak=longest_streak,
        words_found=words_found,
        game_type=game_type,
        daily_seed=get_daily_seed() if game_type == "daily" else None
    )

    db.session.add(game_result)

    if(game_type == "single"):
        current_user.timesSingle += 1
        if score > current_user.globalhighest_score:
            current_user.globalhighest_score = score

        if words_found > current_user.globalmost_words_found:
            current_user.globalmost_words_found = words_found

        if longest_streak > current_user.globallongest_streak:
            current_user.globallongest_streak = longest_streak

    if (game_type == "daily"):
        current_user.timesDaily += 1
        if score > current_user.dailyhighest_score:
            current_user.dailyhighest_score = score

        if words_found > current_user.dailymost_words_found:
            current_user.dailymost_words_found = words_found

        if longest_streak > current_user.dailylongest_streak:
            current_user.dailylongest_streak = longest_streak
        
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Game saved!"
    })


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)


@app.route("/leaderboard_data")
@login_required
def leaderboard_data():
    
    users = User.query.all()

    return jsonify([
        {
            "username": user.username,
            "highest_score": user.globalhighest_score,
            "longest_streak": user.globallongest_streak,
            "most_words_found": user.globalmost_words_found
        }
        for user in users
    ])

@app.route("/dailyleaderboard_data")
@login_required
def dailyleaderboard_data():
    
    users = User.query.all()

    return jsonify([
        {
            "username": user.username,
            "highest_score": user.dailyhighest_score,
            "longest_streak": user.dailylongest_streak,
            "most_words_found": user.dailymost_words_found
        }
        for user in users
    ])

@app.route("/leaderboard")
@login_required
def leaderboard():
    return render_template("leaderboard.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
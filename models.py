# SQLAlchemy Models
from datetime import datetime
from flask_login import UserMixin
from extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    joinDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    timesSingle = db.Column(db.Integer, default=0)
    globalhighest_score = db.Column(db.Integer, default=0)
    globallongest_streak = db.Column(db.Integer, default=0)
    globalmost_words_found = db.Column(db.Integer, default=0)

    timesDaily = db.Column(db.Integer, default=0)
    dailyhighest_score = db.Column(db.Integer, default=0)
    dailylongest_streak = db.Column(db.Integer, default=0)
    dailymost_words_found = db.Column(db.Integer, default=0)


class GameResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    score = db.Column(db.Integer, nullable=False, default=0)
    words_found = db.Column(db.Integer, nullable=False, default=0)
    longest_streak = db.Column(db.Integer, nullable=False, default=0)

    game_type = db.Column(db.String(20), nullable=False, default="single")
    date_played = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    daily_seed = db.Column(db.String(20), nullable=True)  # NEW

    user = db.relationship("User", backref="game_results")
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to game history
    game_history = db.relationship('GameHistory', backref='player', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if password is correct"""
        return check_password_hash(self.password_hash, password)

    def get_statistics(self):
        """Get user's game statistics"""
        total_games = len(self.game_history)
        if total_games == 0:
            return {
                'total_games': 0,
                'won_games': 0,
                'win_rate': 0,
                'average_attempts': 0,
                'best_score': None
            }

        won_games = sum(1 for game in self.game_history if game.won)
        win_rate = (won_games / total_games) * 100 if total_games > 0 else 0

        won_attempts = [game.attempts for game in self.game_history if game.won]
        average_attempts = sum(won_attempts) / len(won_attempts) if won_attempts else 0
        best_score = min(won_attempts) if won_attempts else None

        return {
            'total_games': total_games,
            'won_games': won_games,
            'win_rate': round(win_rate, 1),
            'average_attempts': round(average_attempts, 1),
            'best_score': best_score
        }

    def __repr__(self):
        return f'<User {self.username}>'


class GameHistory(db.Model):
    """Game history model to store game results"""
    __tablename__ = 'game_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    secret_number = db.Column(db.String(3), nullable=False)
    attempts = db.Column(db.Integer, nullable=False)
    won = db.Column(db.Boolean, nullable=False)
    played_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Store the guesses as JSON string
    guesses_data = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<GameHistory user={self.user_id} won={self.won} attempts={self.attempts}>'

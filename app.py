from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, GameHistory
import random
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///hitblow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'ログインが必要です'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def make_random_num():
    """Generate a random 3-digit number with unique digits"""
    ary = []
    while len(ary) < 3:
        random_num = random.randint(0, 9)
        if random_num not in ary:
            ary.append(random_num)
    return ary

# Public routes
@app.route('/')
def index():
    """Landing page with game rules"""
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        # Validation
        if not username or not email or not password:
            flash('すべての項目を入力してください', 'error')
            return render_template('signup.html')

        if password != password_confirm:
            flash('パスワードが一致しません', 'error')
            return render_template('signup.html')

        if len(password) < 6:
            flash('パスワードは6文字以上にしてください', 'error')
            return render_template('signup.html')

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('そのユーザー名は既に使用されています', 'error')
            return render_template('signup.html')

        if User.query.filter_by(email=email).first():
            flash('そのメールアドレスは既に使用されています', 'error')
            return render_template('signup.html')

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('登録が完了しました。ログインしてください', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'ようこそ、{user.username}さん！', 'success')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash('ユーザー名またはパスワードが正しくありません', 'error')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('ログアウトしました', 'success')
    return redirect(url_for('index'))

# Game routes (login required)
@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with statistics"""
    stats = current_user.get_statistics()
    recent_games = GameHistory.query.filter_by(user_id=current_user.id).order_by(
        GameHistory.played_at.desc()
    ).limit(5).all()

    return render_template('dashboard.html', stats=stats, recent_games=recent_games)

@app.route('/start', methods=['GET'])
@login_required
def start():
    """Initialize game"""
    # Generate random 3-digit number and store in session
    answer_num_ary = make_random_num()

    session['answer'] = answer_num_ary
    session['count'] = 0
    session['history'] = []

    return render_template('game.html', username=current_user.username, count=0)

@app.route('/guess', methods=['POST'])
@login_required
def guess():
    """Process player's guess"""
    answer_num_ary = session.get('answer', [0, 0, 0])
    count = session.get('count', 0)
    history = session.get('history', [])

    guess_str = request.form.get('answer', '')

    # Validation
    error_msg = None
    if not guess_str:
        return render_template('game.html', username=current_user.username, count=count, history=history)

    if not (guess_str.isdigit() and len(guess_str) == 3):
        error_msg = "3桁の数字を入力してください"
    else:
        guess_num_ary = [int(d) for d in guess_str]
        if len(set(guess_num_ary)) != 3:
            error_msg = "重複のない3桁の数字を入力してください"

    if error_msg:
        return render_template('game.html',
                             username=current_user.username,
                             count=count,
                             error=error_msg,
                             history=history)

    # Increment count
    count += 1
    session['count'] = count

    # Calculate Hit and Blow
    guess_num_ary = [int(d) for d in guess_str]
    hit_count = 0
    blow_count = 0

    for i in range(3):
        for j in range(3):
            if i == j and answer_num_ary[i] == guess_num_ary[j]:
                hit_count += 1
            elif i != j and answer_num_ary[i] == guess_num_ary[j]:
                blow_count += 1

    # Add to history
    history.append({
        'guess': guess_str,
        'hit': hit_count,
        'blow': blow_count,
        'attempt': count
    })
    session['history'] = history

    # Check if won
    won = hit_count == 3

    # Save game result to database if game ended
    if won or count >= 10:
        secret_number = ''.join(map(str, answer_num_ary))
        game = GameHistory(
            user_id=current_user.id,
            secret_number=secret_number,
            attempts=count,
            won=won,
            guesses_data=json.dumps(history)
        )
        db.session.add(game)
        db.session.commit()

        # Clear session
        session.pop('answer', None)
        session.pop('count', None)
        session.pop('history', None)

    return render_template('result.html',
                         username=current_user.username,
                         count=count,
                         guess=guess_str,
                         hit=hit_count,
                         blow=blow_count,
                         won=won,
                         history=history,
                         game_over=(won or count >= 10))

@app.route('/history')
@login_required
def history():
    """View game history"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    pagination = GameHistory.query.filter_by(user_id=current_user.id).order_by(
        GameHistory.played_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('history.html', pagination=pagination)

@app.route('/ranking')
def ranking():
    """View global ranking"""
    # Get best scores (minimum attempts where won=True)
    subquery = db.session.query(
        GameHistory.user_id,
        db.func.min(GameHistory.attempts).label('best_attempts')
    ).filter(GameHistory.won == True).group_by(GameHistory.user_id).subquery()

    ranking_data = db.session.query(
        User.username,
        subquery.c.best_attempts,
        db.func.count(GameHistory.id).label('total_games'),
        db.func.sum(db.case((GameHistory.won == True, 1), else_=0)).label('won_games')
    ).join(subquery, User.id == subquery.c.user_id
    ).join(GameHistory, User.id == GameHistory.user_id
    ).group_by(User.id, User.username, subquery.c.best_attempts
    ).order_by(subquery.c.best_attempts.asc()
    ).limit(50).all()

    return render_template('ranking.html', ranking_data=ranking_data)

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

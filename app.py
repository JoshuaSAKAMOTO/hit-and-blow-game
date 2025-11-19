from flask import Flask, render_template, request, session, redirect, url_for
import random
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

def make_random_num():
    """Generate a random 3-digit number with unique digits"""
    ary = []
    while len(ary) < 3:
        random_num = random.randint(0, 9)
        if random_num not in ary:
            ary.append(random_num)
    return ary

@app.route('/')
def index():
    """Landing page with game rules"""
    return render_template('index.html')

@app.route('/start', methods=['GET'])
def start():
    """Initialize game with player name"""
    username = request.args.get('username', 'Guest')

    # Generate random 3-digit number and store in session
    answer_num_ary = make_random_num()

    session['username'] = username
    session['answer'] = answer_num_ary
    session['count'] = 0
    session['history'] = []

    return render_template('game.html', username=username, count=0)

@app.route('/guess', methods=['POST'])
def guess():
    """Process player's guess"""
    username = session.get('username', 'Guest')
    answer_num_ary = session.get('answer', [0, 0, 0])
    count = session.get('count', 0)
    history = session.get('history', [])

    guess_str = request.form.get('answer', '')

    # Validation
    error_msg = None
    if not guess_str:
        return render_template('game.html', username=username, count=count, history=history)

    if not (guess_str.isdigit() and len(guess_str) == 3):
        error_msg = "3桁の数字を入力してください"
    else:
        guess_num_ary = [int(d) for d in guess_str]
        if len(set(guess_num_ary)) != 3:
            error_msg = "重複のない3桁の数字を入力してください"

    if error_msg:
        return render_template('game.html',
                             username=username,
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
    if hit_count == 3:
        return render_template('result.html',
                             username=username,
                             count=count,
                             guess=guess_str,
                             hit=hit_count,
                             blow=blow_count,
                             won=True,
                             history=history)

    return render_template('result.html',
                         username=username,
                         count=count,
                         guess=guess_str,
                         hit=hit_count,
                         blow=blow_count,
                         won=False,
                         history=history)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

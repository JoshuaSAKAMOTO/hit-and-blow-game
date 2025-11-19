#!/usr/bin/env python3
import cgi
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
print("Content-Type: text/html;charset=utf-8\n\n")

html_head="""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hit & Blow Game</title>
<style>
  body {
    font-family: serif;
    background-color: #f5f5dc;
    margin: 0;
    padding: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
  }
  .container {
    background-color: white;
    border: 2px solid #333;
    padding: 30px;
    max-width: 500px;
    width: 100%;
    box-shadow: 3px 3px 0px #333;
  }
  h1 {
    text-align: center;
    font-size: 28px;
    margin: 0 0 20px 0;
    border-bottom: 2px solid #333;
    padding-bottom: 10px;
  }
  p {
    line-height: 1.6;
    margin: 10px 0;
    text-align: center;
  }
  .error {
    background-color: #ffcccc;
    border: 2px solid #cc0000;
    padding: 10px;
    margin: 20px 0;
    text-align: center;
    color: #cc0000;
  }
  .result {
    text-align: center;
    margin: 20px 0;
  }
  .result-number {
    font-size: 48px;
    font-family: monospace;
    letter-spacing: 15px;
    margin: 20px 0;
  }
  .score {
    display: inline-block;
    width: 45%;
    border: 2px solid #333;
    padding: 20px;
    margin: 10px 5px;
    text-align: center;
  }
  .score-value {
    font-size: 36px;
    font-weight: bold;
  }
  .score-label {
    font-size: 14px;
    margin-top: 5px;
  }
  .success {
    background-color: #e6ffe6;
    border: 2px solid #00cc00;
    padding: 20px;
    margin: 20px 0;
    text-align: center;
  }
  input[type="text"] {
    width: 100%;
    padding: 12px;
    border: 2px solid #333;
    font-size: 24px;
    text-align: center;
    box-sizing: border-box;
    font-family: monospace;
    letter-spacing: 10px;
  }
  button {
    width: 100%;
    padding: 12px;
    background-color: #333;
    color: white;
    border: none;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
    margin-top: 20px;
  }
  button:hover {
    background-color: #555;
  }
  a {
    display: block;
    width: 100%;
    padding: 12px;
    background-color: #333;
    color: white;
    text-decoration: none;
    font-size: 16px;
    font-weight: bold;
    text-align: center;
    margin-top: 20px;
    box-sizing: border-box;
  }
  a:hover {
    background-color: #555;
  }
</style>
</head>
<body>
<div class="container">
  <h1>Hit & Blow</h1>
"""

html_tail="""
</div>
</body>
</html>
"""
form = cgi.FieldStorage()
username = form.getvalue("username", "Guest")
try:
    cnt = int(form.getvalue("count", "0")) + 1
    num = int(form.getvalue("number", "0"))
    ans_str = form.getvalue("answer", "")
except ValueError:
    cnt = 1
    num = 0
    ans_str = ""

# Reconstruct target number list
answer_num_ary = [int(d) for d in str(num).zfill(3)]

# Form for next guess
form_post=f"""
<p>次の予想を入力してください</p>
<form action="ht02.py" method="post">
  <input type="text" name="answer" value="{ans_str}" required maxlength="3">
  <input type="hidden" name="count" value={cnt}>
  <input type="hidden" name="number" value={num}>
  <input type="hidden" name="username" value="{username}">
  <button type="submit">回答する</button>
</form>
"""

# Validation
is_valid = False
error_msg = ""
my_answer_num_ary = []

# Only validate if user has submitted an answer
if ans_str:
    if ans_str.isdigit() and len(ans_str) == 3:
        my_answer_num_ary = [int(d) for d in ans_str]
        if len(set(my_answer_num_ary)) == 3:
            is_valid = True
        else:
            error_msg = "重複のない3桁の数字を入力してください"
    else:
        error_msg = "3桁の数字を入力してください"

    if not is_valid:
        print(html_head)
        print(f'<div class="error">{error_msg}</div>')
        print(form_post)
        print(html_tail)
        sys.exit()

    # Game Logic
    hit_count = 0
    blow_count = 0

    for i in range(3):
        for j in range(3):
            if i == j and answer_num_ary[i] == my_answer_num_ary[j]:
                hit_count += 1
            elif i != j and answer_num_ary[i] == my_answer_num_ary[j]:
                blow_count += 1

    # Result Display
    print(html_head)
    print(f"""
    <div class="result">
      <p><strong>{cnt}回目のチャレンジ</strong></p>
      <div class="result-number">{ans_str}</div>
      <div>
        <div class="score">
          <div class="score-value">{hit_count}</div>
          <div class="score-label">Hit</div>
        </div>
        <div class="score">
          <div class="score-value">{blow_count}</div>
          <div class="score-label">Blow</div>
        </div>
      </div>
    </div>
    """)

    if hit_count == 3:
        print(f"""
        <div class="success">
          <h2>Congratulations!</h2>
          <p>おめでとうございます、<strong>{username}</strong>さん！</p>
          <p><strong>{cnt}</strong>回で正解しました！</p>
        </div>
        <a href="index.html">トップに戻る</a>
        """)
    else:
        print(form_post)

    print(html_tail)
else:
    # First time loading the page, just show the form
    print(html_head)
    print(form_post)
    print(html_tail)

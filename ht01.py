#!/usr/bin/env python3
import myway
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
    margin: 0 0 10px 0;
    border-bottom: 2px solid #333;
    padding-bottom: 10px;
  }
  p {
    line-height: 1.6;
    margin: 10px 0;
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
</style>
</head>
<body>
<div class="container">
  <h1>Game Start</h1>
  <p>さあ、ゲームを始めましょう！</p>
"""

html_tail="""
</div>
</body>
</html>
"""
form = cgi.FieldStorage()
username = form.getvalue("username", "Guest")
cnt = 0

# Generate random 3-digit number
answer_num_ary = myway.make_random_num()
# Convert list [1, 2, 3] to integer 123 for storage
num = int("".join(map(str, answer_num_ary)))

form_post=f"""
<p>ようこそ、<strong>{username}</strong>さん</p>
<p style="margin-top: 20px;">3桁の数字を予想して入力してください</p>

<form action="ht02.py" method="post">
  <input type="text" name="answer" required maxlength="3" placeholder="123">
  <input type="hidden" name="count" value={cnt}>
  <input type="hidden" name="number" value={num}>
  <input type="hidden" name="username" value="{username}">
  <button type="submit">回答する</button>
</form>
"""

print(html_head)
print(form_post)
print(html_tail)

from flask import Flask, render_template, request
import random
import sqlite3

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


# 패 선택하기
@app.route('/play', methods=['POST'])
def play():
    options = ['가위', '바위', '보']

    user = request.form['choice']
    computer = random.choice(options)

    result = get_game_result(user, computer)

    return render_template('result.html', user=user, computer=computer, result=result)
#--- sql코드 추가한 후로 23번 라인이 오류 남

# 승부규칙
def get_game_result(u, c):
    win=0
    draw=0
    lose=0

    if u == c:
        draw+=1
        return '비겼습니다'
    elif (u == '가위' and c == '보') or (u == '바위' and c == '가위') or (u == '보' and c == '바위'):
        win+=1
        return '이겼습니다'
    else:
        lose+=1
        return '졌습니다'
    

# 데이터베이스 선언
def init_db():
    connect=sqlite3.connect('score.db')
    c=connect.cursor()
    c.execute('''create table SCORE
                 (id char(10), user TEXT, computer TEXT, result TEXT)''')
    connect.commit()
    connect.close()

# db에 승부 입력
def save_result(user, computer, result):
    connect=sqlite3.connect('score.db')
    c=connect.cursor()
    c.execute('insert into score (user, computer, result) \
              values (?, ?, ?)', user, computer, result)
    connect.commit()
    connect.close()


# 전적 조회
def check_score():
    connect=sqlite3.connect('score.db')
    c=connect.cursor()
    c.execute('select * from score order by id desc')
    score=c.fetchall()
    connect.close()
    return score


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request
import random

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/play', methods=['POST'])
def play():
    options = ['가위', '바위', '보']

    user = request.form['choice']
    computer = random.choice(options)

    result = get_game_result(user, computer)

    return render_template('result.html', user=user, computer=computer, result=result)


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
    


if __name__ == '__main__':
    app.run(debug=True)

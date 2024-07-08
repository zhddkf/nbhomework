from flask import Flask, request, render_template, redirect, url_for, session, flash
import sqlite3
from flask_bootstrap import Bootstrap
import random
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
# from request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
bootstrap = Bootstrap(app)


# SQLite 데이터베이스 초기화 함수
def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                result TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()


# 사용자
class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


# 가위바위보 폼
class PlayForm(FlaskForm):
    choice = StringField('나의 패 선택하기', validators=[DataRequired()], render_kw={
                         "placeholder": "가위/바위/보 중 하나를 입력하세요"})
    submit = SubmitField('Play')


# 회원가입 폼
class SignupForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=4, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


# 초기화 함수
init_db()


# 라우트들
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash('회원가입이 완료되었습니다. 로그인하세요', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('play'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            if user:
                session['username'] = user[1]
                flash('로그인 완료!', 'success')
                return redirect(url_for('play'))
            else:
                flash('다시 시도해주세요.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('로그아웃했습니다.', 'success')
    return redirect(url_for('index'))


@app.route('/play', methods=['GET', 'POST'])
def play():
    if 'username' not in session:
        flash('우선 로그인하세요.', 'warning')
        return redirect(url_for('login'))

    form = PlayForm()
    if form.validate_on_submit():
        user_choice = form.choice.data
        computer_choice = random.choice(['가위', '바위', '보'])

        # 가위바위보 규칙
        if user_choice == computer_choice:
            result = '비겼습니다'
        elif (user_choice == '가위' and computer_choice == '보') or \
             (user_choice == '바위' and computer_choice == '가위') or \
             (user_choice == '보' and computer_choice == '바위'):
            result = '이겼습니다'
        else:
            result = '졌습니다'

        # 결과 저장
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE username = ?", (session['username'],))
            user_id = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO records (user_id, result) VALUES (?, ?)", (user_id, result))
            conn.commit()

        return render_template('result.html', user_choice=user_choice, computer_choice=computer_choice, result=result)

    return render_template('play.html', form=form)


# 메인 함수
if __name__ == '__main__':
    app.run(debug=True)

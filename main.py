from flask import Flask, render_template, redirect, make_response, request, session, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.users import User
from data.games import Games
from data.matches import Matches
from forms.user import RegisterForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'scythe'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init("db/matches.db")
    app.run()


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="first", img='static/img/dice.png')


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template('register.html', title='Регистрация')
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        if request.form['password'] != request.form['password_again']:
            return render_template('register.html', title='Registration', message='Пароли не совпадают')
        if db_sess.query(User).filter(User.email == request.form['email'].lower()).first():
            return render_template('register.html', title='Registration',
                                   message="Пользователь с такой почтой уже есть")
        if not db_sess.query(Games).filter(Games.title == request.form['game'].lower()).first():
            g = Games(title=request.form['game'].lower())
            db_sess.add(g)
            db_sess.commit()
        user = User(name=request.form['name'], email=request.form['email'].lower(),
                    favorite_game=request.form['game'].lower())
        user.set_password(request.form['password'])
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html', title='Авторизация')
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == request.form['email']).first()
        if user and user.check_password(request.form['password']):
            login_user(user, remember=request.form['RememberMe'])
            return redirect("/index")
        return render_template('login.html', message="Неправильный логин или пароль", title='Авторизация')
    return render_template('login.html', title='Авторизация')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'GET':
        return render_template('add_note.html', title='Добавление записи', img='static/img/dice.png')
    elif request.method == 'POST':
        game = request.form['game'].lower()
        score = request.form['score']
        result = request.form['result']
        print(game, result, score)
        db_sess = db_session.create_session()
        if not db_sess.query(Games).filter(Games.title == game).first():
            g = Games(title=game)
            db_sess.add(g)
            db_sess.commit()

        id_game = db_sess.query(Games).filter(Games.title == game).first()
        match = Matches()
        match.game = id_game
        match.score = score
        match.result = result
        match.user_id = current_user.id
        db_sess.add(match)
        if str(id_game.id) not in str(current_user.my_games):
            if current_user.my_games:
                current_user.my_games = str(current_user.my_games) + ' ' + str(id_game.id)
            else:
                current_user.my_games = str(id_game.id)

        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/index')


@app.route('/statistic', methods=['GET', 'POST'])
@login_required
def statistic():
    games = []
    k = 0
    db_sess = db_session.create_session()
    if current_user.my_games:
        for id in current_user.my_games.split():
            game = db_sess.query(Games).filter(Games.id == id).first().title
            games.append(game.capitalize())
    if request.method == 'GET':
        return render_template('statistic.html', title='Статистика', games=games, name="Статистика")
    elif request.method == 'POST':
        select_game = request.form['game'].lower()
        print(select_game)
        user_id = current_user.id
        game_id = db_sess.query(Games).filter(Games.title == select_game).first().id
        print(user_id, game_id)
        res = db_sess.query(Matches).filter(Matches.user_id == user_id, Matches.game_id == game_id)
        w = 0
        lo = 0
        d = 0
        scores = []
        name = 'Статистика по игре "' + select_game + '"'
        print(res)
        for i in res:
            if i.result == 'win':
                w += 1
            elif i.result == 'lose':
                lo += 1
            else:
                d += 1
            scores.append(int(i.score))
        print(w, lo, d)
        k = 1
        md = round(sum(scores) / len(scores))
        return render_template('statistic.html', title='Статистика', w=w, lo=lo, d=d, max=max(scores), min=min(scores),
                               md=md, name=name)


@app.route('/statistic<game>')
def stat(game):
    print(game)


@app.route('/account')
@login_required
def my_account():
    return render_template('account.html', title='Мой аккаунт')


@app.route('/edit')
@login_required
def edit():
    return render_template('edit.html', title='Изменение записи')


if __name__ == '__main__':
    main()

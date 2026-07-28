import os

from flask import Flask, render_template, redirect, make_response, request, session, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.users import User
from data.games import Games
from data.matches import Matches
from api import matches_api

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init("db/matches.db")
    app.register_blueprint(matches_api.blueprint)
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
            remember = bool(request.form.get('RememberMe'))
            login_user(user, remember=remember)
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
        return redirect('/statistic')


@app.route('/statistic', methods=['GET', 'POST'])
@login_required
def statistic():
    db_sess = db_session.create_session()
    games = []
    if current_user.my_games:
        for game_id in current_user.my_games.split():
            game = db_sess.query(Games).get(game_id)
            if game:
                games.append(game.title.capitalize())

    if request.method == 'POST':
        select_game = request.form.get('game')
        if select_game:
            return redirect('/statistic/' + select_game.lower())

    return render_template('statistic.html', title='Статистика', games=sorted(games), name="Статистика")


def calculate_stats_for_game(db_sess, user_id, game_title):
    """Вычисляет статистику для пользователя и игры."""
    game = db_sess.query(Games).filter(Games.title == game_title.lower()).first()
    if not game:
        return None

    matches = db_sess.query(Matches).filter(
        Matches.user_id == user_id,
        Matches.game_id == game.id
    ).all()

    scores = [int(m.score) for m in matches]
    name = f'Статистика по игре "{game_title.capitalize()}"'

    if not scores:
        return {'w': 0, 'lo': 0, 'd': 0, 'max': 0, 'min': 0, 'md': 0, 'name': name}

    w = sum(1 for m in matches if m.result == 'win')
    lo = sum(1 for m in matches if m.result == 'lose')
    d = sum(1 for m in matches if m.result == 'draw')

    return {
        'w': w, 'lo': lo, 'd': d,
        'max': max(scores),
        'min': min(scores),
        'md': round(sum(scores) / len(scores)),
        'name': name
    }


@app.route('/statistic/<game>')
@login_required
def stat(game):
    db_sess = db_session.create_session()
    stats = calculate_stats_for_game(db_sess, current_user.id, game)
    # Если игра не найдена, перенаправляем на общую страницу статистики
    if stats is None:
        return redirect('/statistic')
    return render_template('game_statistic.html', title=game.capitalize(), **stats)


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

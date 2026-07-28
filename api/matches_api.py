import flask
from flask import jsonify

from data import db_session
from data.matches import Matches

blueprint = flask.Blueprint(
    'matches_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/matches')
def get_matches():
    db_sess = db_session.create_session()
    matches = db_sess.query(Matches).all()
    return jsonify(
        {
            'matches':
                [item.to_dict(only=('id', 'result', 'user.name', 'game.title', 'score'))
                 for item in matches]
        }
    )


@blueprint.route('/api/matches/<user_id>', methods=['GET'])
def get_user_matches(user_id):
    db_sess = db_session.create_session()
    matches = db_sess.query(Matches).filter(Matches.user_id == user_id).all()
    return jsonify(
        {
            'matches':
                [item.to_dict(only=('id', 'result', 'game.title', 'score'))
                 for item in matches]
        }
    )

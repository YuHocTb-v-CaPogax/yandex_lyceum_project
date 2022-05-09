from flask_restful import Resource, reqparse
from flask import abort, jsonify
from data import db_session
from data.users import User

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('about', required=True)
parser.add_argument('email', required=True)
parser.add_argument('password')


def abort_if_not_found(user_id):
    session = db_session.create_session()
    news = session.query(User).get(user_id)
    if not news:
        abort(404)


class UsersResource(Resource):
    @staticmethod
    def get(user_id):
        abort_if_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=('name', 'about', 'email', 'news.title'))})

    @staticmethod
    def delete(user_id):
        abort_if_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    @staticmethod
    def get():
        session = db_session.create_session()
        user = session.query(User).all()
        return jsonify({'user': [item.to_dict(
            only=('name', 'about', 'email', 'news.title')) for item in user]})

    @staticmethod
    def post():
        args = parser.parse_args()
        session = db_session.create_session()
        user = User()
        user.name = args['name']
        user.about = args['about']
        user.email = args['email']
        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})

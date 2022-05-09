from data import db_session
from flask_restful import Resource, reqparse
from flask import abort, jsonify
from data.comments import Comment

parser = reqparse.RequestParser()
parser.add_argument('content', required=True)
parser.add_argument('news_id')
parser.add_argument('user_id')


def abort_if_not_found(comment_id):
    session = db_session.create_session()
    news = session.query(Comment).get(comment_id)
    if not news:
        abort(404)


class CommentsResource(Resource):
    @staticmethod
    def get(comment_id):
        abort_if_not_found(comment_id)
        session = db_session.create_session()
        comment = session.query(Comment).get(comment_id)
        return jsonify({'comment': comment.to_dict(
            only=('content', 'news_id', 'user_id'))})

    @staticmethod
    def delete(comment_id):
        abort_if_not_found(comment_id)
        session = db_session.create_session()
        comment = session.query(Comment).get(comment_id)
        session.delete(comment)
        session.commit()
        return jsonify({'success': 'OK'})


class CommentsListResource(Resource):
    @staticmethod
    def get():
        session = db_session.create_session()
        comment = session.query(Comment).all()
        return jsonify({'comments': [item.to_dict(
            only=('content', 'news_id', 'user_id')) for item in comment]})

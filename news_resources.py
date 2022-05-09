from data import db_session
from flask_restful import Resource, reqparse
from flask import abort, jsonify
from data.news import News

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('is_private', required=True, type=bool)
parser.add_argument('user_id', required=True, type=int)


def abort_if_news_not_found(news_id):
    session = db_session.create_session()
    news = session.query(News).get(news_id)
    if not news:
        abort(404)


class NewsResource(Resource):
    @staticmethod
    def get(news_id):
        abort_if_news_not_found(news_id)
        session = db_session.create_session()
        news = session.query(News).get(news_id)
        return jsonify({'news': news.to_dict(
            only=('title', 'content', 'user_id', 'is_private'))})

    @staticmethod
    def delete(news_id):
        abort_if_news_not_found(news_id)
        session = db_session.create_session()
        news = session.query(News).get(news_id)
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})


class NewsListResource(Resource):
    @staticmethod
    def get():
        session = db_session.create_session()
        news = session.query(News).all()
        return jsonify({'news': [item.to_dict(
            only=('title', 'content', 'user.name')) for item in news]})

    @staticmethod
    def post():
        args = parser.parse_args()
        session = db_session.create_session()
        news = News()
        news.title = args['title']
        news.content = args['content']
        news.user_id = args['user_id']
        news.is_published = args['is_published']
        news.is_private = args['is_private']
        session.add(news)
        session.commit()
        return jsonify({'success': 'OK'})

from flask import Flask, render_template, redirect, abort, request
from flask_restful import Api
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from news_resources import NewsListResource, NewsResource
from users_resources import UsersListResource, UsersResource
from comments_resources import CommentsListResource, CommentsResource
from data import db_session
from data.news import News
from data.users import User
from data.comments import Comment
from forms.loginform import LoginForm
from forms.newsform import NewsForm
from forms.registerform import RegisterForm
from forms.accountform import AccountForm
from forms.commentform import CommentForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandex_lyceum_secret_key'
api = Api(app)

api.add_resource(NewsListResource, '/api/news')
api.add_resource(NewsResource, '/api/news/<int:news_id>')

api.add_resource(UsersListResource, '/api/users')
api.add_resource(UsersResource, '/api/users/<int:user_id>')

api.add_resource(CommentsListResource, '/api/comments')
api.add_resource(CommentsResource, '/api/comments/<int:comment_id>')

login_manager = LoginManager()
login_manager.init_app(app)


# def load_css():
#     return url_for('static', filename='css/style.css')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def start():
    db_sess = db_session.create_session()
    comments = db_sess.query(Comment).all()
    users = db_sess.query(User).all()
    if current_user.is_authenticated:
        all_news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        all_news = db_sess.query(News).filter(News.is_private != True)
    return render_template('start.html', title='Блог', all_news=all_news, comments=comments, users=users)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html',
                                   title='Регистрация', form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html',
                                   title='Регистрация', form=form, message="Такой пользователь уже есть")
        user = User()
        user.name = form.name.data
        user.email = form.email.data
        user.about = form.about.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    else:
        return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               title='Авторизация', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:_id>', methods=['GET', 'POST'])
@login_required
def edit_news(_id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == _id,
                                          News.user == current_user).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == _id,
                                          News.user == current_user).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости', form=form)


@app.route('/news_delete/<int:_id>', methods=['GET', 'POST'])
@login_required
def news_delete(_id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == _id,
                                      News.user == current_user).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/account')
@login_required
def account_info():
    return render_template('account.html', title='Информация об аккаунте')


@app.route('/account_edit/<int:_id>', methods=['GET', 'POST'])
@login_required
def account_edit(_id):
    title = 'Изменение информации об аккаунте'
    form = AccountForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == _id).first()
        if user:
            form.about.data = user.about
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == _id).first()
        if user:
            user.about = form.about.data
            if user.check_password(form.password.data):
                user.set_password(form.new_password.data)
                db_sess.commit()
                return redirect('/')
            else:
                return render_template('account_edit.html',
                                       title=title, form=form, message='Неверно введен старый пароль')
        else:
            abort(404)
    return render_template('account_edit.html',
                           title=title, form=form, message='')


@app.route('/account_delete/<int:_id>', methods=['GET', 'POST'])
@login_required
def account_delete(_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == _id).first()
    if user:
        db_sess.delete(user)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/comment_add/<int:_id>', methods=['GET', 'POST'])
@login_required
def comment_add(_id):
    form = CommentForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == _id).first()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        comment = Comment()
        comment.content = form.content.data
        comment.user_id = user.id
        comment.news_id = news.id
        db_sess.add(comment)
        db_sess.commit()
        return redirect('/')
    return render_template('comment_add.html', title='Оставить комментарии',
                           form=form)


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.run(port=8080, host='127.0.0.1')

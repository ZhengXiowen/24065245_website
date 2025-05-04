import re
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YourSecretKey' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Bootstrap(app)  
db = SQLAlchemy(app)  
login_manager = LoginManager(app) 
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
  
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """用户模型：包含用户名、邮箱和密码哈希"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        """设置用户密码（将明文密码哈希存储）"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """检查密码是否正确"""
        return check_password_hash(self.password_hash, password)

class Book(db.Model):
    """图书模型：包含中英文名称、描述、价格、环境影响指数和封面图片文件名"""
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(200), nullable=False)
    name_zh = db.Column(db.String(200), nullable=False)
    description_en = db.Column(db.Text, nullable=False)
    description_zh = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    env_impact = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(100), nullable=False)  

class Comment(db.Model):
    """评论模型：每条评论关联一个用户和一本书"""
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    book = db.relationship('Book', backref=db.backref('comments', lazy=True))

class RegisterForm(FlaskForm):
    """用户注册表单，包含用户名、邮箱、密码和确认密码字段"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=100)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    def validate_username(self, field):
 
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already exists.')
    def validate_email(self, field):

        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    """用户登录表单，包含用户名和密码字段"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class CheckoutForm(FlaskForm):
    """结账表单，包含姓名、银行卡号、CVV、有效月份/年份、邮箱和收货地址"""
    name = StringField('Name', validators=[DataRequired()])
    card_number = StringField('Card Number', validators=[DataRequired()])
    cvv = StringField('CVV', validators=[DataRequired(), Regexp('^\d{3}$', message='CVV must be 3 digits')])
    exp_month = SelectField('Exp Month', choices=[(f"{i:02d}", f"{i:02d}") for i in range(1, 13)], validators=[DataRequired()])
    exp_year = IntegerField('Exp Year', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = TextAreaField('Shipping Address', validators=[DataRequired()])

    def validate_card_number(self, field):

        digits = re.sub(r'[\s-]', '', field.data)
        if not (digits.isdigit() and len(digits) == 16):
            raise ValidationError('Invalid card number. Must be 16 digits.')

    def validate_exp_year(self, field):

        current_year = datetime.datetime.now().year
        try:
            year = int(field.data) if isinstance(field.data, str) else field.data
        except Exception:
            raise ValidationError('Invalid year.')
        if year < current_year:
            raise ValidationError('Expiration year must be this year or later.')

class CommentForm(FlaskForm):
    """商品评论表单，只有一个内容字段"""
    content = TextAreaField('Comment', validators=[DataRequired(), Length(max=1000)])

@app.route('/')
def index():
    """首页：展示图书列表，支持搜索和排序，并实现AJAX悬浮详情预览"""
    lang = session.get('lang', 'en')  
    query = Book.query

    q = request.args.get('q', '')
    if q:
        query = query.filter((Book.name_en.ilike(f'%{q}%')) | (Book.name_zh.ilike(f'%{q}%')))
    sort_key = request.args.get('sort', 'name')
    if sort_key == 'price':
        query = query.order_by(Book.price)
    elif sort_key == 'env':
        query = query.order_by(Book.env_impact)
    else:
        query = query.order_by(Book.name_zh if lang == 'zh' else Book.name_en)
    books = query.all()
    return render_template('index.html', books=books)

@app.route('/book/<int:book_id>', methods=['GET', 'POST'])
def book_detail(book_id):
    """详情页：显示图书详情，及其用户评论列表；提供评论发表和加入购物篮功能"""
    book = Book.query.get_or_404(book_id)
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You must log in to leave a comment.')
            return redirect(url_for('login', next=request.path))
        comment = Comment(content=form.content.data, user_id=current_user.id, book_id=book.id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('book_detail', book_id=book_id))
    comments = Comment.query.filter_by(book_id=book.id).order_by(Comment.timestamp.desc()).all()
    return render_template('detail.html', book=book, form=form, comments=comments)

@app.route('/api/book/<int:book_id>')
def book_info(book_id):
    """AJAX接口：返回指定图书的详细描述（根据当前语言）"""
    book = Book.query.get_or_404(book_id)
    lang = session.get('lang', 'en')
    if lang == 'zh':
        data = {
            'name': book.name_zh,
            'description': book.description_zh,
            'env': book.env_impact
        }
    else:
        data = {
            'name': book.name_en,
            'description': book.description_en,
            'env': book.env_impact
        }
    return data 
@app.route('/add_to_basket/<int:book_id>')
def add_to_basket(book_id):
    """将图书加入购物篮（保存在 session）"""
    book = Book.query.get_or_404(book_id)
    basket = session.get('basket', {})
    if str(book_id) in basket:
        basket[str(book_id)] += 1
    else:
        basket[str(book_id)] = 1
    session['basket'] = basket
    flash('Item added to basket.')
    return redirect(request.referrer or url_for('index'))

@app.route('/basket')
def basket():
    """购物篮页面：显示当前会话用户的购物篮内容"""
    basket = session.get('basket', {})
    items = []
    total_price = 0.0
    for book_id_str, qty in basket.items():
        book = Book.query.get(int(book_id_str))
        if book:
            items.append((book, qty))
            total_price += book.price * qty
    return render_template('basket.html', items=items, total=total_price)

@app.route('/remove_from_basket/<int:book_id>')
def remove_from_basket(book_id):
    """从购物篮移除指定图书"""
    basket = session.get('basket', {})
    if str(book_id) in basket:
        basket.pop(str(book_id), None)
        session['basket'] = basket
    return redirect(url_for('basket'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """结账页面：填写支付信息表单并验证"""
    form = CheckoutForm()
    if form.validate_on_submit():
        session.pop('basket', None)  
        return redirect(url_for('success'))
    return render_template('checkout.html', form=form)

@app.route('/success')
def success():
    """支付成功页面"""
    return render_template('success.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """用户登出"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/lang/<lang_code>')
def set_language(lang_code):
    """切换站点语言（中英文）"""
    if lang_code in ['en', 'zh']:
        session['lang'] = lang_code
    next_page = request.args.get('next')
    if next_page:
        return redirect(next_page)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

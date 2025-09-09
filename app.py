import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Post, Work
from dotenv import load_dotenv

# Load biến môi trường từ file .env (nếu có)
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-me')

db.init_app(app)

# --- tạo DB nếu chưa có ---
with app.app_context():
    db.create_all()

# ---------- Public routes ----------
@app.route('/')
def home():
    posts = Post.query.order_by(Post.id.desc()).limit(3).all()
    works = Work.query.order_by(Work.id.desc()).limit(3).all()
    return render_template('index.html', posts=posts, works=works)

@app.route('/blog')
def blog():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('Blog.html', posts=posts)

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@app.route('/works')
def works_list():
    works = Work.query.order_by(Work.id.desc()).all()
    return render_template('work.html', works=works)

# ---------- Simple Admin Auth ----------
ADMIN_USER = os.getenv('ADMIN_USER', 'admin')
ADMIN_PASS = os.getenv('ADMIN_PASS', 'admin')

def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return wrapper

@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('username') == ADMIN_USER and request.form.get('password') == ADMIN_PASS:
            session['admin'] = True
            return redirect(url_for('admin_index'))
        flash('Sai username hoặc password!', 'error')
    return render_template('admin/admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

# ---------- Admin Dashboard ----------
@app.route('/admin')
@login_required
def admin_index():
    post_count = Post.query.count()
    work_count = Work.query.count()
    return render_template('admin/admin_dashboard.html', post_count=post_count, work_count=work_count)

# ---------- Posts CRUD ----------
@app.route('/admin/posts')
@login_required
def admin_posts():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('admin/admin_posts.html', posts=posts)

@app.route('/admin/posts/new', methods=['GET','POST'])
@login_required
def admin_posts_new():
    if request.method == 'POST':
        p = Post(
            title=request.form['title'],
            date=request.form.get('date',''),
            tags=request.form.get('tags',''),
            desc=request.form.get('desc',''),
            content=request.form.get('content','')
        )
        db.session.add(p)
        db.session.commit()
        flash('Thêm bài viết mới thành công!', 'success')
        return redirect(url_for('admin_posts'))
    return render_template('admin/admin_post_form.html', mode='new')

@app.route('/admin/posts/<int:pid>/edit', methods=['GET','POST'])
@login_required
def admin_posts_edit(pid):
    post = Post.query.get_or_404(pid)
    if request.method == 'POST':
        post.title = request.form['title']
        post.date = request.form.get('date','')
        post.tags = request.form.get('tags','')
        post.desc = request.form.get('desc','')
        post.content = request.form.get('content','')
        db.session.commit()
        flash('Cập nhật bài viết thành công!', 'success')
        return redirect(url_for('admin_posts'))
    return render_template('admin/admin_post_form.html', mode='edit', post=post)

@app.route('/admin/posts/<int:pid>/delete', methods=['POST'])
@login_required
def admin_posts_delete(pid):
    post = Post.query.get_or_404(pid)
    db.session.delete(post)
    db.session.commit()
    flash('Xóa bài viết thành công!', 'info')
    return redirect(url_for('admin_posts'))

# ---------- Works CRUD ----------
@app.route('/admin/works')
@login_required
def admin_works():
    works = Work.query.order_by(Work.id.desc()).all()
    return render_template('admin/admin_works.html', works=works)

@app.route('/admin/works/new', methods=['GET','POST'])
@login_required
def admin_works_new():
    if request.method == 'POST':
        w = Work(
            title=request.form['title'],
            year=request.form.get('year',''),
            category=request.form.get('category',''),
            desc=request.form.get('desc',''),
            image=request.form.get('image','')
        )
        db.session.add(w)
        db.session.commit()
        flash('Thêm dự án mới thành công!', 'success')
        return redirect(url_for('admin_works'))
    return render_template('admin/admin_work_form.html', mode='new')

@app.route('/admin/works/<int:wid>/edit', methods=['GET','POST'])
@login_required
def admin_works_edit(wid):
    work = Work.query.get_or_404(wid)
    if request.method == 'POST':
        work.title = request.form['title']
        work.year = request.form.get('year','')
        work.category = request.form.get('category','')
        work.desc = request.form.get('desc','')
        work.image = request.form.get('image','')
        db.session.commit()
        flash('Cập nhật dự án thành công!', 'success')
        return redirect(url_for('admin_works'))
    return render_template('admin/admin_work_form.html', mode='edit', work=work)

@app.route('/admin/works/<int:wid>/delete', methods=['POST'])
@login_required
def admin_works_delete(wid):
    w = Work.query.get_or_404(wid)
    db.session.delete(w)
    db.session.commit()
    flash('Xóa dự án thành công!', 'info')
    return redirect(url_for('admin_works'))

if __name__ == '__main__':
    app.run(debug=True)

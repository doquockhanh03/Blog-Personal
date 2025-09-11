import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from dotenv import load_dotenv
from models import db, Post, Work, Roadmap, Stage, Task

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-me')

db.init_app(app)

with app.app_context():
    db.create_all()

# ---------------- Public Routes ----------------
@app.route('/')
def home():
    posts = Post.query.order_by(Post.id.desc()).limit(3).all()
    works = Work.query.order_by(Work.id.desc()).limit(3).all()
    return render_template('index.html', posts=posts, works=works)

@app.route('/blog')
def blog():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('blog.html', posts=posts)

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@app.route('/works')
def works_list():
    works = Work.query.order_by(Work.id.desc()).all()
    return render_template('work.html', works=works)

@app.route('/roadmap')
def roadmap_list():
    roadmaps = Roadmap.query.all()
    stage_progress = {}
    roadmap_progress = {}
    for r in roadmaps:
        # roadmap progress
        total_r = Task.query.join(Stage).filter(Stage.roadmap_id==r.id).count()
        done_r = Task.query.join(Stage).filter(Stage.roadmap_id==r.id, Task.is_done==True).count()
        roadmap_progress[r.id] = int(done_r * 100 / total_r) if total_r else 0

        # stage progress
        for s in r.stages:
            total_s = Task.query.filter_by(stage_id=s.id).count()
            done_s = Task.query.filter_by(stage_id=s.id, is_done=True).count()
            stage_progress[s.id] = int(done_s * 100 / total_s) if total_s else 0

    return render_template('roadmap.html', roadmaps=roadmaps, stage_progress=stage_progress, roadmap_progress=roadmap_progress)


# ---------------- Admin Auth ----------------
ADMIN_USER = os.getenv('ADMIN_USER')
ADMIN_PASS = os.getenv('ADMIN_PASS')

def login_required(f):
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

@app.route('/admin')
@login_required
def admin_index():
    post_count = Post.query.count()
    work_count = Work.query.count()
    return render_template('admin/admin_dashboard.html', post_count=post_count, work_count=work_count)

# ---------------- Posts CRUD ----------------
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
            date=request.form.get('date', datetime.utcnow()),
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
        post.date = request.form.get('date', post.date)
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

# ---------------- Works CRUD ----------------
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

# ---------------- Roadmaps CRUD ----------------
@app.route('/admin/roadmaps')
@login_required
def admin_roadmaps():
    roadmaps = Roadmap.query.all()
    return render_template('admin/admin_roadmaps.html', roadmaps=roadmaps)

@app.route('/admin/roadmaps/new', methods=['GET','POST'])
@login_required
def admin_roadmaps_new():
    if request.method == 'POST':
        r = Roadmap(
            title=request.form['title'],
            description=request.form.get('description','')
        )
        db.session.add(r)
        db.session.commit()
        flash('Thêm lộ trình mới thành công!', 'success')
        return redirect(url_for('admin_roadmaps'))
    return render_template('admin/admin_roadmap_form.html', mode='new')

@app.route('/admin/roadmaps/<int:rid>/edit', methods=['GET','POST'])
@login_required
def admin_roadmaps_edit(rid):
    r = Roadmap.query.get_or_404(rid)
    if request.method == 'POST':
        r.title = request.form['title']
        r.description = request.form.get('description','')
        db.session.commit()
        flash('Cập nhật lộ trình thành công!', 'success')
        return redirect(url_for('admin_roadmaps'))
    return render_template('admin/admin_roadmap_form.html', mode='edit', roadmap=r)

@app.route('/admin/roadmaps/<int:rid>/delete', methods=['POST'])
@login_required
def admin_roadmaps_delete(rid):
    r = Roadmap.query.get_or_404(rid)
    db.session.delete(r)
    db.session.commit()
    flash('Xóa lộ trình thành công!', 'info')
    return redirect(url_for('admin_roadmaps'))

# ---------------- Stages CRUD ----------------
@app.route('/admin/roadmaps/<int:rid>/stages')
@login_required
def admin_stages(rid):
    roadmap = Roadmap.query.get_or_404(rid)
    stages = Stage.query.filter_by(roadmap_id=rid).order_by(Stage.order).all()
    return render_template('admin/admin_stages.html', roadmap=roadmap, stages=stages)

@app.route('/admin/roadmaps/<int:rid>/stages/new', methods=['GET','POST'])
@login_required
def admin_stages_new(rid):
    roadmap = Roadmap.query.get_or_404(rid)
    if request.method == 'POST':
        max_order = db.session.query(db.func.max(Stage.order)).filter_by(roadmap_id=rid).scalar() or 0
        order_value = int(request.form.get('order') or (max_order + 1))
        stage = Stage(
            title=request.form['title'],
            description=request.form.get('description',''),
            order=order_value,
            roadmap_id=rid
        )
        db.session.add(stage)
        db.session.commit()
        flash('Thêm stage thành công!', 'success')
        return redirect(url_for('admin_stages', rid=rid))
    return render_template('admin/admin_stage_form.html', mode='new', roadmap=roadmap, stage=None)

@app.route('/admin/stages/<int:sid>/edit', methods=['GET','POST'])
@login_required
def admin_stages_edit(sid):
    stage = Stage.query.get_or_404(sid)
    if request.method == 'POST':
        stage.title = request.form['title']
        stage.description = request.form.get('description','')
        stage.order = int(request.form.get('order') or stage.order)
        db.session.commit()
        flash('Cập nhật stage thành công!', 'success')
        return redirect(url_for('admin_stages', rid=stage.roadmap_id))
    return render_template('admin/admin_stage_form.html', mode='edit', roadmap=stage.roadmap, stage=stage)

@app.route('/admin/stages/<int:sid>/delete', methods=['POST'])
@login_required
def admin_stages_delete(sid):
    stage = Stage.query.get_or_404(sid)
    rid = stage.roadmap_id
    db.session.delete(stage)
    db.session.commit()
    flash('Xóa stage thành công!', 'info')
    return redirect(url_for('admin_stages', rid=rid))

@app.route('/admin/roadmaps/<int:rid>/stages/reorder', methods=['POST'])
@login_required
def admin_stages_reorder(rid):
    data = request.get_json()
    order_list = data.get('order', [])
    for idx, sid in enumerate(order_list, start=1):
        s = Stage.query.filter_by(id=sid, roadmap_id=rid).first()
        if s:
            s.order = idx
    db.session.commit()
    return jsonify({'status': 'ok'})

def compute_stage_progress(stage):
    total = Task.query.filter_by(stage_id=stage.id).count()
    if total == 0:
        return 0
    done = Task.query.filter_by(stage_id=stage.id, is_done=True).count()
    return int(done * 100 / total)

def compute_roadmap_progress(roadmap):
    total = Task.query.join(Stage).filter(Stage.roadmap_id==roadmap.id).count()
    if total == 0:
        return 0
    done = Task.query.join(Stage).filter(Stage.roadmap_id==roadmap.id, Task.is_done==True).count()
    return int(done * 100 / total)

# ---------------- Tasks (Admin CRUD) ----------------
@app.route('/admin/stages/<int:sid>/tasks')
@login_required
def admin_tasks(sid):
    stage = Stage.query.get_or_404(sid)
    tasks = Task.query.filter_by(stage_id=sid).order_by(Task.order).all()
    return render_template('admin/admin_tasks.html', stage=stage, tasks=tasks)

@app.route('/admin/stages/<int:sid>/tasks/new', methods=['GET','POST'])
@login_required
def admin_tasks_new(sid):
    stage = Stage.query.get_or_404(sid)
    if request.method == 'POST':
        max_order = db.session.query(db.func.max(Task.order)).filter_by(stage_id=sid).scalar() or 0
        order_value = int(request.form.get('order') or (max_order + 1))
        t = Task(
            title=request.form['title'],
            description=request.form.get('description',''),
            order=order_value,
            stage_id=sid,
            is_done=bool(request.form.get('is_done'))
        )
        db.session.add(t)
        db.session.commit()
        flash('Thêm task thành công!', 'success')
        return redirect(url_for('admin_tasks', sid=sid))
    return render_template('admin/admin_task_form.html', mode='new', stage=stage, task=None)

@app.route('/admin/tasks/<int:tid>/edit', methods=['GET','POST'])
@login_required
def admin_tasks_edit(tid):
    task = Task.query.get_or_404(tid)
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form.get('description','')
        task.order = int(request.form.get('order') or task.order)
        task.is_done = bool(request.form.get('is_done'))
        db.session.commit()
        flash('Cập nhật task thành công!', 'success')
        return redirect(url_for('admin_tasks', sid=task.stage_id))
    return render_template('admin/admin_task_form.html', mode='edit', stage=task.stage, task=task)

@app.route('/admin/tasks/<int:tid>/delete', methods=['POST'])
@login_required
def admin_tasks_delete(tid):
    task = Task.query.get_or_404(tid)
    sid = task.stage_id
    db.session.delete(task)
    db.session.commit()
    flash('Xóa task thành công!', 'info')
    return redirect(url_for('admin_tasks', sid=sid))

@app.route('/admin/stages/<int:sid>/tasks/reorder', methods=['POST'])
@login_required
def admin_tasks_reorder(sid):
    data = request.get_json()
    order_list = data.get('order', [])
    for idx, tid in enumerate(order_list, start=1):
        t = Task.query.filter_by(id=tid, stage_id=sid).first()
        if t:
            t.order = idx
    db.session.commit()
    return jsonify({'status':'ok'})


@app.route('/roadmap/task/<int:tid>/toggle', methods=['POST'])
def roadmap_task_toggle(tid):
    t = Task.query.get_or_404(tid)
    t.is_done = not t.is_done
    db.session.commit()
    stage = t.stage
    roadmap = stage.roadmap
    sp = compute_stage_progress(stage)
    rp = compute_roadmap_progress(roadmap)
    return jsonify({
        'status':'ok',
        'is_done': t.is_done,
        'stage_progress': sp,
        'roadmap_progress': rp,
        'stage_id': stage.id,
        'roadmap_id': roadmap.id
    })


if __name__ == '__main__':
    app.run(debug=True)

#Flask là lớp chính của Flask Framework, dùng để tạo ứng dụng web.
#Render_template là hàm để load file HTML từ thư mục templates/ và trả về cho client trình duyệt.
from flask import Flask, render_template

app = Flask(__name__) #Khởi tạo một ứng dụng Flask, __name_ là tên module hiện tại. Flask dùng nó để xác định vị trí của app, giúp tìm thư mục template/ và static/

posts = [
    {
        'id': 1,
        'title': 'UI Interactions of the week',
        'date': '12 Feb 2019',
        'tags': 'Express, Handlebars',
        'desc': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque euismod, nisi eu consectetur consectetur, nisl nisi consectetur nisi, euismod euismod nisi euismod.'
    },
    {
        'id': 2,
        'title': 'Form Validation in React',
        'date': '10 Feb 2019',
        'tags': 'React, Formik',
        'desc': 'Suspendisse potenti. Etiam euismod, nisi eu consectetur consectetur, nisl nisi consectetur nisi, euismod euismod nisi euismod.'
    }
]

@app.route('/')                             #Flask decorator, định nghĩa URL / (trang chủ).
def home():                                 #hàm xử lý khi có request GET tới /
    return render_template('index.html', posts=posts) #Trả về file index.html từ thư mục templates/, truyền biến posts vào template.

@app.route('/post/<int:post_id>')
def post(post_id):
    post = next((p for p in posts if p['id'] == post_id), None)#Tìm bài viết theo ID
    return render_template('post.html', posts = posts)

@app.route('/blog')
def blog():
    return render_template('Blog.html', posts=posts)

@app.route('/works')
def works():
    return render_template('work.html', posts=posts)

@app.route('/admin/posts')
def admin_posts():
    return render_template('admin_posts.html', posts=posts)

if __name__ == '__main__':
    app.run(debug=True) #Chạy ứng dụng Flask ở chế độ debug, tự động reload khi code thay đổi và hiển thị lỗi chi tiết.


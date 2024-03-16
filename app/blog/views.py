from flask import render_template, Blueprint
from app.models import Blogpost


blog_blueprint = Blueprint(
    'blog',
    __name__,
    template_folder='templates'
)


@blog_blueprint.route('/allPosts')
def allPosts():
    posts = Blogpost.query.order_by(Blogpost.date_posted.desc()).all()
    return render_template('blog/all-posts.html', posts=posts)


@blog_blueprint.route('/post/<int:post_id>')
def post(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()
    return render_template('blog/post.html', post=post)

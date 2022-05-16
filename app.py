from datetime import datetime
import random
from sqlalchemy import desc
import os
from flask import Flask, render_template, redirect, request, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///friends.db'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')

association_table = db.Table('association', db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('following_id', db.Integer, db.ForeignKey('following.id'))
)
save_association_table = db.Table('save_association', db.Model.metadata,
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('save_id', db.Integer, db.ForeignKey('save.id'))
)
like_association_table = db.Table('like_association', db.Model.metadata,
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)
comment_association_table = db.Table('comment_association', db.Model.metadata,
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id'))
)




class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    image = db.Column(db.String(120), nullable=False, default="default.png")
    bio = db.Column(db.String(80), nullable=True)
    relationship = db.Column(db.String(80), nullable=True)
    gender = db.Column(db.String(80), nullable=False)
    birth = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.String(120), nullable=False)
    reply = db.relationship('Comment', cascade="all, delete-orphan", passive_deletes=True, backref="comment_author",lazy=True)
    posts = db.relationship('Post', cascade="all, delete-orphan", passive_deletes=True, backref="author",lazy=True)
    saves = db.relationship('Save', cascade="all, delete-orphan", passive_deletes=True, backref="save_author",lazy=True)
    
    follow = db.relationship("Following",
                    secondary=association_table)
    follow_user = db.relationship('Following', backref="f",lazy=True)



class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(300), nullable=False)
    post_image = db.Column(db.String(120), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    liked_users = db.relationship("User",
                    secondary=like_association_table)
    commented_users = db.relationship("Comment",
                    secondary=comment_association_table)        
    count_like = db.Column(db.Integer,nullable=False,default=0)
    count_comment = db.Column(db.Integer,nullable=False,default=0)


class Following(db.Model):
    __tablename__ = 'following'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Save(db.Model):
    __tablename__ = 'save'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    saved_posts = db.relationship("Post",
                    secondary=save_association_table)

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.String(300), nullable=False)




@app.route("/")
@login_required
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    following_count = len(current_user.follow)
    
    n = Following.query.filter_by(f=current_user).first()
    users = User.query.all()
    followers = []
    for i in users:
        if n in i.follow:
            followers.append(i)

    follower_count  = len(followers)
    following = []
    if current_user.follow:
        for i in current_user.follow:
            u = User.query.filter_by(id=i.user_id).first()
            following.append(u)

    saves = Save.query.filter_by(user_id=current_user.id).first()
    if saves:
        savedposts = saves.saved_posts
    else:
        save_user = Save(user_id=current_user.id)
        db.session.add(save_user)
        db.session.commit()
        savedposts = save_user.saved_posts



    youmayknow = []
    for i in users:
        if not i in following:
            if not i == current_user:
                youmayknow.append(i)
    
    you = random.sample(youmayknow,k=len(youmayknow))

    posts = Post.query.order_by(desc(Post.timestamp)).all()
    
        
   
    return render_template("index.html",
                            posts=posts,
                            following_count=following_count,
                            follower_count=follower_count,
                            followers=followers,
                            following=following,
                            youmayknow=you[:5],
                            savedposts=savedposts,               
                            )

@app.route("/follow")
@login_required
def follow():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    following_count = len(current_user.follow)

    n = Following.query.filter_by(f=current_user).first()
    users = User.query.all()
    followers = []
    for i in users:
        if n in i.follow:
            followers.append(i)
    follower_count  = len(followers)

    following = []
    if current_user.follow:
        for i in current_user.follow:
            u = User.query.filter_by(id=i.user_id).first()
            following.append(u)
    
    
    #save_posts
    save = Save.query.filter_by(user_id=current_user.id).first()
    savedposts = save.saved_posts



    youmayknow = []
    for i in users:
        if not i in following:
            if not i == current_user:
                youmayknow.append(i)

    you = random.sample(youmayknow,k=len(youmayknow))
    
 
    posts = []
    for i in following:
        posts.extend(Post.query.filter_by(author=i).order_by(desc(Post.timestamp)).all())

    return render_template("following.html",posts=posts,
                            following_count=following_count,
                            follower_count=follower_count,
                            followers=followers,
                            following=following,
                            youmayknow=you[:5],
                            savedposts=savedposts                    
                            )



@app.route("/logout")
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('login'))


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            p = check_password_hash(user.password,password)
            if p:
                login_user(user) 
                flash("Login!","primary")
                return redirect(url_for('index'))
            else:
                flash("password is incorrect!","danger")
                return redirect(url_for('login'))
        else:
            flash("email doesn't exists!","danger")
            return redirect(url_for('login'))       
    return render_template("login.html")


@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        birth = request.form.get("birth")
        gender = request.form.get("gender")
        now = datetime.now()
        date_time = now.strftime("%m-%d-%Y")
        if not username or not email or not password or not birth or not gender:
            flash("input field is empty")
            return redirect(url_for('register'))
        exists_email = User.query.filter_by(email=email).first()
        if exists_email:
            flash("email is already exists")
            return redirect(url_for('register'))
        if len(password) < 5:
            flash("weak password. password length must be greater than five")
            return redirect(url_for('register'))
        hash = generate_password_hash(password=password,salt_length=8)
        user = User(username=username, email=email, password=hash, birth=birth, gender=gender, timestamp=date_time)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Successfully Register!","primary")
        return redirect(url_for('index'))
    return render_template("register.html")




@app.route("/delete_account",methods=["GET","POST"])
@login_required
def delete_account():
    if request.method == "POST":
        User.query.filter_by(id=current_user.id).delete()
        db.session.commit()
        return redirect(url_for('login'))





@app.route("/profile/<int:id>",methods=["GET","POST"])
@login_required
def profile(id):
    user = User.query.get(id)
    following_count = len(user.follow)
    n = Following.query.filter_by(f=user).first()
    users = User.query.all()
    followers = []
    for i in users:
        if n in i.follow:
            followers.append(i)

    follower_count  = len(followers)
    profile_image = url_for('static', filename="images/" + user.image)
    users_posts = Post.query.filter_by(author=user).order_by(desc(Post.timestamp)).all()
    posts_count = len(users_posts)

    #following
    ff = Following.query.filter_by(user_id=user.id).first()
    follow_status = False
    if ff in current_user.follow:
        follow_status = True



    #display followers and following
    following = []
    for i in user.follow:
        u = User.query.filter_by(id=i.user_id).first()
        following.append(u)



    # save_posts
    save = Save.query.filter_by(user_id=user.id).first()
    savedposts = save.saved_posts

    save = Save.query.filter_by(user_id=user.id).first()
    save_posts = save.saved_posts



    b = user.birth
    a = b.split("-")
    year = int(a[0])
    now = datetime.now().year
    age = now - year
    if request.method == "POST":
        name = request.form.get("username")
        bio = request.form.get("bio")
        gender = request.form.get("gender")
        relationship = request.form.get("relationship")
        birth = request.form.get("birth")

        if not name:
            flash("invalid input field")
            return redirect(url_for('profile'))
        
        if not birth:
            birth = current_user.birth
        
        if not gender:
            gender = current_user.gender

        if not relationship:
            relationship = current_user.relationship
      
        current_user.username = name
        current_user.bio = bio
        current_user.relationship = relationship
        current_user.birth = birth
        current_user.gender = gender
   

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            db.session.commit()
            flash("Updated Profile!","primary")
            return redirect(url_for('profile',id=id))  
        if file and file.filename:
            filename = secure_filename(file.filename)                
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            current_user.image = filename    
            db.session.commit()
            return redirect(url_for('profile',id=id))
        # if file and allowed_file(file.filename):
         

        db.session.commit()
        flash("Updated Profile!","primary")
        return redirect(url_for('profile',id=id))    
        
    return render_template("profile.html",
                profile_image=profile_image,
                age=age,
                posts=users_posts,
                user=user,
                following_count=following_count,
                follower_count=follower_count, 
                posts_count=posts_count,
                follow_status=follow_status,
                following=following,
                followers=followers,   
                save_posts = save_posts,
                savedposts=savedposts
                )


@app.route("/create",methods=["GET","POST"])
@login_required
def create():
    if request.method == "POST":
        text = request.form.get("text")
        if not text:
            flash("required text")
            return redirect('/')
        post = Post(author=current_user,text=text)
        file = request.files['file']
        if file.filename == '':
            db.session.add(post)
            db.session.commit()
            flash("Created Post!","primary")
            return redirect(url_for('index'))  
        if file and file.filename:
            filename = secure_filename(file.filename)                
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            post.post_image = filename   
            flash("Created Post!","primary")
            db.session.add(post) 
            db.session.commit()
            return redirect(url_for('index'))

        db.session.add(post)
        db.session.commit()
        flash("Created Post!","primary")
        return redirect(url_for('index'))  
    
    
         
@app.route("/edit_post/<int:id>",methods=["GET","POST"])
@login_required
def edit_post(id):
    post = Post.query.get(id)
    if request.method == "POST":
        post.text = request.form.get("text")
        file = request.files['file']
        if file.filename == '':
            db.session.add(post)
            db.session.commit()
            flash("Edited Post!","primary")
            return redirect(url_for('index'))  
        if file and file.filename:
            filename = secure_filename(file.filename)                
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            post.post_image = filename   
            flash("Edited Post!","primary")
            db.session.add(post) 
            db.session.commit()
            return redirect(url_for('index'))
        db.session.add(post)
        db.session.commit()
        flash("Edited Post!","primary")
        return redirect(url_for('index'))  
    


@app.route("/delete_post/<int:id>",methods=["GET","POST"])
@login_required
def delete_post(id):
    if request.method == "POST":      
        post = Post.query.get(id)
        if current_user == post.author:
            db.session.delete(post)
            db.session.commit()
            flash("Deleted Post!","danger")
            return redirect(url_for('index'))
        flash("No permission")
        return redirect(url_for('index'))


@app.route("/profile_delete_post/<int:id>",methods=["GET","POST"])
@login_required
def profile_delete_post(id):
    if request.method == "POST":      
        post = Post.query.get(id)
        if current_user == post.author:
            db.session.delete(post)
            db.session.commit()
            flash("Deleted Post!","danger")
            return redirect(url_for('profile',id=current_user.id))
        flash("No permission","danger")
        return redirect(url_for('profile',id=current_user.id))
        
        

@app.route("/following/<int:id>",methods=["GET","POST"])
@login_required
def following(id):
    if request.method == "POST":       
        other = User.query.get(id)
        ff = Following.query.filter_by(user_id=id).first()
    
        
                
        if ff in current_user.follow:
                # unfollow
            current_user.follow.remove(ff)             
            db.session.add(current_user) 
            db.session.commit()
            return redirect(url_for('profile',id=id))
        else:
                # follow
            if ff is None:
                follow = Following(f=other)
                db.session.add(follow)
                db.session.commit()
                current_user.follow.append(follow)      
                db.session.add(current_user)
                db.session.commit()
                return redirect(url_for('profile',id=id))    
            current_user.follow.append(ff)      
            db.session.add(current_user)
            db.session.commit()
            return redirect(url_for('profile',id=id))     



              
@app.route("/saved",methods=["GET","POST"])
@login_required
def saved():
    id = request.form.get('id')
    if request.method == "POST":
        post = Post.query.get(id)
        exists_save = Save.query.filter_by(user_id=current_user.id).first()
        if not exists_save:
            new_user = Save(user_id=current_user.id)
            db.session.add(new_user)
            db.session.commit()

        if not exists_save.saved_posts is None:
            if post in exists_save.saved_posts:
                exists_save.saved_posts.remove(post)
                db.session.add(exists_save)
                db.session.commit()
                return ('',200)

            else:
                exists_save.saved_posts.append(post)
                db.session.add(exists_save)
       
                db.session.commit()
                return ('',200)
        exists_save.saved_posts.append(post)
        db.session.add(exists_save)     
        db.session.commit()

        return ('',200)
        
        


@app.route("/liked",methods=["GET","POST"])
@login_required
def liked():
    id = request.form.get('id')
    if request.method == "POST":
        post = Post.query.get(id)
        if not current_user in post.liked_users:
            post.count_like += 1
            post.liked_users.append(current_user)
            db.session.add(post)
            db.session.commit()
            return ('',200)
        else:
            post.count_like -= 1
            post.liked_users.remove(current_user)
            db.session.add(post)
            db.session.commit()
            return ('',200)
       
       

@app.route("/comment",methods=["GET","POST"])
@login_required
def comment():
    id = request.form.get('id')
    text = request.form.get('text')
    if request.method == "POST":
        post = Post.query.get(id)    
        com = Comment(user_id=current_user.id,text=text)
        db.session.add(com)
        db.session.commit()
        post.commented_users.append(com)
        post.count_comment += 1
        db.session.add(post)        
        db.session.commit()
        username = current_user.username
        image = current_user.image
        user_id = current_user.id
        return jsonify({'username':username,'image':image,'user_id':user_id})

@app.route("/delete_comment",methods=["GET","POST"])
@login_required
def delete_comment():
    id = request.form.get('id')
    post_id = request.form.get('post_id')
    if request.method == "POST": 
        post = Post.query.filter_by(id=post_id).first()
        com = Comment.query.filter_by(id=id).first()
        if com.user_id == current_user.id:
            post.commented_users.remove(com)
            post.count_comment = post.count_comment - 1
            db.session.add(post)        
            db.session.commit()
            db.session.delete(com)
            db.session.commit()
            return ('',200)
      

@app.route("/search",methods=["GET","POST"])
@login_required
def search():
    saves = Save.query.filter_by(user_id=current_user.id).first()
    if saves:
        savedposts = saves.saved_posts
    else:
        save_user = Save(user_id=current_user.id)
        db.session.add(save_user)
        db.session.commit()
        savedposts = save_user.saved_posts
    if request.method == "GET":
        q = request.args.get('q')
        print(q)
        users = User.query.filter(User.username.like('%' +q+ '%')).all()
        posts = Post.query.filter(Post.text.like('%' +q+ '%' )).all()
       
        # print(posts)
    return render_template("search.html",users=users,posts=posts,savedposts=savedposts)

if __name__ == '__main__':
    app.run(debug=True)
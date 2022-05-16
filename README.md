# Friends social networking application

#### Introduction
This project is social networking application. Users are able to create account,uploading photo,create post, delete post and edit post."like" other users'posts or "unlike other users'posts. Users can save posts and comment other users'posts. Users can view their and other users profile.Users can edit their profile.Users can also follow eachother and unfollow as well. users can see post's liked_users and other users comments. Users can delete their comments. Users can search other users and posts. Users can see their following users's posts.  


This project was built using Flask as a backend framework and JavaScript as a frontend programming language.this project including five models.All generated information are saved in database (sqlalchemy.

All webpages of the project are mobile-responsive.

#### Tools and Languages
HTML CSS Bootstrap Python Flask Javascript Ajax Bootstrap Icon

#### Installation
pip install requirements.txt.

In python shell- 

from app import db

db.create_all()

And You can run this command to run your server.

python -m flask run 


#### Files and directories
FRIENDS - main application directory. templates/layout.html contains all static content.

Login.html - you need to first login for application.

Register.html - If you don't have login account you can register with username, email, password, birth and gender.

index.html - when you are register,you can create account with birthday date,profile picture,gender,interest,like_gender,height,passions and if you are not register or login.you can't create account.

index.html - when you created account,redirect to index page.first you can see newfeed and then you will see other users posts, people you may know and profile page and you can like or unlike other users posts
and save and comment system in index page.It contains other features like search, following, delete, edit posts.

if you click other users in people you may know,you will see other users's profiles.

if you click your profile,you will see your profile detail and you can edit your profile detail and upload new profile picture and you can delete or logout.

profile.html - For users profile page users can follow eachother and see save posts and their posts.

following.html - users can see their following users's posts.

app.py respectively, contains all backend codes.




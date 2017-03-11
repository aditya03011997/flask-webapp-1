from flask import make_response, url_for, request, render_template, flash, session, redirect
from .forms import ChangeNickForm, ChangePasswordForm, SearchForm, SignupForm, SigninForm, PostForm, RecoveryForm, NewpasswordForm
from app import authomatic, page, db, models
from .models import User, Post, Like
import datetime
from werkzeug.utils import secure_filename
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature
import smtplib
import os
from flask_whooshee import WhoosheeQuery
from authomatic.adapters import WerkzeugAdapter
from newspaper import Article

def get_serializer(secret_key=None):
    if secret_key is None:
        secret_key = page.secret_key
    return Serializer(secret_key, 100)

def get_serializer2(secret_key=None):
    if secret_key is None:
        secret_key = page.secret_key
    return Serializer(secret_key)

def get_activation_link(user):
    s = get_serializer()
    payload = s.dumps(user.id)
    return url_for('activate_user', payload=payload, _external=True)

def send_mail(address, user):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("EMAIL", "PASS")
    msg = "click this link to confirm: " + str(get_activation_link(user)) 
    server.sendmail("EMAIL", address, msg)
    server.quit()

@page.route('/')
@page.route('/index')
def index():
    return render_template('index.html', title='Home')

@page.route('/login/<provider_name>/', methods=['GET', 'POST'])
def login(provider_name):
    response = make_response()

    # Authenticate the user
    result = authomatic.login(WerkzeugAdapter(request, response), provider_name)

    if result:
        if result.user:
            # Get user info
            result.user.update()
        return render_template(user_name=result.user.name,
                               user_email=result.user.email,
                               user_id=result.user.id)
    return response

@page.route('/register', methods=['GET', 'POST'])
def register():
    form = SignupForm()

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('register.html', title='Register', form=form)
        else:
            newuser = User(form.nickname.data, form.email.data, form.password.data)
            db.session.add(newuser)
            db.session.commit()
            db.session.add(newuser.follow(newuser))
            db.session.commit()
            newuser.make_dirs()

            flash('Registration Successfull')
            
            send_mail(newuser.email, newuser)
            
            return redirect(url_for('signin')) 

    elif request.method == 'GET':
        return render_template('register.html', title="Register", form=form)

@page.route('/profile/<nick>')
def profile(nick):
    if 'email' not in session:
        return redirect(url_for('signin'))

    user = User.query.filter_by(nickname=nick).first()
    me = User.query.filter_by(nickname=session['nick']).first()

    if user is None:
        return redirect(url_for('signin'))
    else:
        user = User.query.filter_by(nickname=nick).first()
        posts = Post.query.order_by(Post.timestamp.desc())
        posts = posts.filter_by(author=user)

        return render_template('profile.html', title="Profile", user=user, pp=posts, me=me)

@page.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()

    if 'email' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('signin.html', form=form)
        else:
            session['email'] = form.email.data
            user = User.query.filter_by(email = form.email.data.lower()).first()
            session['nick'] = user.nickname
            session['id'] = user.id
            
            return redirect(url_for('profile', nick=user.nickname))

    elif request.method == 'GET':
        return render_template('signin.html', title="Sign In", form=form)

@page.route('/signout')
def signout():
    if 'email' not in session:
        return redirect(url_for('signin'))
    session.pop('email', None)
    session.pop('nick', None)
    session.pop('id', None)
    return redirect(url_for('index'))

@page.route('/newpost', methods=['GET', 'POST'])
def newpost():
    form = PostForm()

    if 'email' not in session:
        return redirect(url_for('signin'))

    if request.method == 'POST':
        if form.validate() == False:
            return render_template('newpost.html', title="New Post", form=form)
        else:
            cur_user = User.query.filter_by(email = session['email']).first()
            link = form.body.data
            article = Article(url=link)
            article.download()
            article.parse()
            post_body = article.text[:160]+'...'
            post_title = article.title
            if len(str(article.top_image)) > 0:
                img_addr = str(article.top_image)
            else:
                img_addr = '/static/userdata/avatar.png'
            new = models.Post(title=post_title, body=post_body, timestamp=datetime.datetime.utcnow(), link=link, image=img_addr, likes=0, author=cur_user)
            db.session.add(new)
            db.session.commit()
            flash("Post Successfull")
            return redirect(url_for('profile', nick=session['nick']))

    elif request.method == 'GET':
        return render_template('newpost.html', title="New Post", form=form)

@page.route('/changeprofile', methods=['GET','POST'])
def changeprofile():
    if 'email' not in session:
        return redirect(url_for('signin'))
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('changeprofile'))
        filename = secure_filename(file.filename)
        file.save(os.path.join(page.config['UPLOAD_FOLDER'], filename))

        for root, dirs, files in os.walk("/home/manan/Programs/EduTech/app/static/userdata/"+str(session['nick'])):
            for f in files:
                if f.endswith(".jpg") or f.endswith(".png"):
                    os.remove("/home/manan/Programs/EduTech/app/static/userdata/"+str(session['nick'])+'/'+str(f))

        os.rename("/home/manan/Programs/EduTech/app/static/userdata/"+str(filename), "/home/manan/Programs/EduTech/app/static/userdata/" + str(session['nick']) + "/" + str(filename))
        return redirect(url_for('profile', nick=session['nick']))
    elif request.method == 'GET':
        return render_template("changeprofile.html", title="Change Profile") 

@page.route('/removeprofile')
def removeprofile():
    for root, dirs, files in os.walk("/home/manan/Programs/EduTech/app/static/userdata/"+str(session['nick'])):
        for f in files:
            if f.endswith(".jpg") or f.endswith(".png"):
                os.remove("/home/manan/Programs/EduTech/app/static/userdata/"+str(session['nick'])+'/'+str(f))
    return redirect(url_for('profile', nick=session['nick']))

@page.route('/users/activate/<payload>')
def activate_user(payload):
    s = get_serializer2()
    try:
        user_id = s.loads(payload)
    except BadSignature:
        return 'Invalid or Expired URL'

    user = User.query.get_or_404(user_id)
    user.activation_status = True
    db.session.commit()
    return 'User activated'

@page.route('/users/changepass/<payload>', methods=['GET', 'POST'])
def changepass(payload):
    form = NewpasswordForm()
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('newpass.html', form=form)
        else:
            s = get_serializer2()
            try:
                user_id = s.loads(payload)
            except BadSignature:
                return 'Session Expired'
            user = User.query.get_or_404(user_id)
            user.set_password(form.password.data)
            db.session.commit()
            return 'Password Changed'

    elif request.method == 'GET':
        s = get_serializer2()
        try:
            user_id = s.loads(payload)
        except BadSignature:
            return 'Invalid or Expired URL'
        return render_template("newpass.html", form=form)

@page.route('/forgotpassword', methods=['POST', 'GET'])
def forgotpassword():
    form = RecoveryForm()
    if request.method == 'POST':
        if form.validate()  == False:
            return render_template('recovery.html', title="Forgot Password", form=form)
        else:
            user = User.query.filter_by(email=form.email.data).first()
            send_mail(form.email.data, user)
            return 'mail sent successfully'

    elif request.method == 'GET':
        return render_template('recovery.html', title="Forgot Password", form=form)

@page.route('/resendmail', methods=['POST', 'GET'])
def resendmail():
    form = RecoveryForm()
    if request.method == 'POST':
        if form.validate()  == False:
            return render_template('resend.html', title="Forgot Password", form=form)
        else:
            user = User.query.filter_by(email=form.email.data).first()
            send_mail(form.email.data, user)
            return 'mail sent successfully'

    elif request.method == 'GET':
        return render_template('resend.html', title="Resend Mail", form=form)

@page.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    
    if request.method == 'POST':
        if form.validate()  == False:
            return render_template('search.html', title="Search", form=form)
        else:
            q = form.search.data
            return redirect(url_for('search_results', query=q))
    elif request.method == 'GET':
        return render_template('search.html', title="Search", form=form)

@page.route('/upvote/<int:post_id>/<int:user_id>')
def upvote(post_id, user_id):
    post = Post.query.filter_by(id = post_id).first()
    user = User.query.filter_by(id = user_id).first()

    res = Like.query.filter_by(post_id = post_id).all()

    for r in res:
        if r.user_id == user_id:
            return 'You cannot like this post again'

    like = Like(user.id, post.id)
    post.likes = post.likes + 1
    db.session.add(like)
    db.session.commit()

    return redirect(url_for('profile', nick=post.author.nickname))

@page.route('/undoupvote/<int:post_id>/<int:user_id>')
def undoupvote(post_id, user_id):
    post = Post.query.filter_by(id = post_id).first()
    user = User.query.filter_by(id = user_id).first()

    res = Like.query.filter_by(post_id = post_id).all()

    for r in res:
        if r.user_id == user_id:
            post.likes = post.likes - 1
            db.session.delete(r)
            db.session.commit()
            session['flag'] = False
            return redirect(url_for('profile', nick=post.author.nickname))

    return 'You cannot dislike this post again'

@page.route('/follow/<nickname>')
def follow(nickname):
    if 'email' not in session:
        return redirect(url_for('signin'))
    user = User.query.filter_by(nickname=nickname).first()
    me = User.query.filter_by(nickname=session['nick']).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if user == me:
        flash('You can\'t follow yourself!')
        return redirect(url_for('profile', nick=nickname))
    u = me.follow(user)
    if u is None:
        flash('Cannot follow ' + nickname + '.')
        return redirect(url_for('profile', nick=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname + '!')
    return redirect(url_for('profile', nick=nickname))

@page.route('/unfollow/<nickname>')
def unfollow(nickname):
    if 'email' not in session:
        return redirect(url_for('signin'))
    user = User.query.filter_by(nickname=nickname).first()
    me = User.query.filter_by(nickname=session['nick']).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if user == me:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('profile', nick=nickname))
    u = me.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.')
        return redirect(url_for('profile', nick=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.')
    return redirect(url_for('profile', nick=nickname))

@page.route('/settings')
def settings():
    if 'email' not in session:
        return redirect(url_for('signin'))
    return render_template('settings.html', title="Account Settings")

@page.route('/changepassword', methods=['POST', 'GET'])
def changepassword():
    if 'email' not in session:
        return redirect(url_for('signin'))
    form = ChangePasswordForm()
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('changepassword.html', title="Change Password", form=form)
        else:
            user = User.query.filter_by(nickname=session['nick']).first()
            user.set_password(form.new_password.data)
            db.session.commit()
            return redirect(url_for('profile', nick=session['nick']))
    elif request.method == 'GET':
        return render_template('changepassword.html', title="Change Password", form=form)

@page.route('/changenickname', methods=['POST', 'GET'])
def changenickname():
    form = ChangeNickForm()
    if 'email' not in session:
        return redirect(url_for('signin'))
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('changenick.html', title="Change Nickname", form=form)
        else:
            user = User.query.filter_by(nickname=session['nick']).first()
            user.nickname = form.nickname.data
            db.session.commit()
            return redirect(url_for('profile', nick=session['nick']))
    elif request.method == 'GET':
        return render_template('changenick.html', title="Change Nickname", form=form)

@page.route('/search_results/<query>')
def search_results(query):
    results = Post.query.whooshee_search(query).all()
    return render_template('search_results.html', title="Search Results", query=query, results=results)

@page.route('/5menu')
def five_menu():
    return render_template('5menu.html', title="5 Minutes")

@page.route('/15menu')
def fifteen_menu():
    return render_template('15menu.html', title="15 Minutes")

@page.route('/30menu')
def thirty_menu():
    return render_template('30menu.html', title="30 Minutes")

@page.route('/imenu')
def imenu():
    return render_template('imenu.html', title="Time is no Barrier")

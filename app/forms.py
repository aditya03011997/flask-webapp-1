from wtforms import SelectField, SubmitField, StringField, validators, PasswordField
from flask_wtf import Form
from .models import User 
from flask import flash, session
import re

class SignupForm(Form):
    nickname = StringField("Nickname", [validators.Required("Please Enter Your Nickname")])
    email = StringField("Email",  [validators.Required("Please enter your email address.")])
    password = PasswordField('Password', [validators.Required("Please enter a password.")])
    submit = SubmitField("Create account")

    def validate(self):
        if not Form.validate(self):
            return False
        
        user = User.query.filter_by(email = self.email.data.lower()).first()
        nick = User.query.filter_by(nickname = self.nickname.data).first()

        addresstoverify = self.email.data.lower()
        match = match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', addresstoverify)

        if match == None:
            self.email.errors.append("That email doesnt looks correct")
            return False
        if user:
            self.email.errors.append("That email is already taken")
            return False
        if nick:
            self.nickname.errors.append("That nick is already taken")
            return False
        else:
            return True

class SigninForm(Form):
    email = StringField("Email", [validators.Required("Please enter your email address.")])
    password = PasswordField('Password', [validators.Required("Please enter a password.")])
    submit = SubmitField("Sign In")

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user and user.check_password(self.password.data):
            if user.activation_status == False:
                self.email.errors.append("Email has not been verified!")
                return False
            else:
                return True
        else:
            self.password.errors.append("Invalud e-mail or password")
            return False

class PostForm(Form):
    body = StringField("Body", [validators.Required("Body cannot be empty")])
    myChoices = [('5 Minutes', '5 Minutes'), ('15 Minutes', '15 Minutes'), ('30 Minutes', '30 Minutes'), ('Long', 'Long')]
    category = SelectField(label='Category', coerce=str, choices = myChoices)
    submit = SubmitField("Post")

    def validate(self):
        if not Form.validate(self):
            return False
        return True

    
    
class Categorychoiceform(Form):
    selected_ones=[('Technology','Technology'),('Business & Finance', 'Business & Finance'),('Lifehacks','Lifehacks'),('Softskills','Softskills'),('DS & Algo','DS & Algo'),('Machine Learning & AI','Machine Learning & AI')]
    choices = SelectField(label='Category', choices=[selected_ones], coerce=str)
    submit = SubmitField("Post")
    
    def validate(self):
        if not Form.validate(self):
            return False
        return True
        

class RecoveryForm(Form):
    email = StringField("Email", [validators.Required("Please enter your email address.")])
    submit = SubmitField("Send Mail")

    def validate(self):
        if not Form.validate(self):
            return False
        user = User.query.filter_by(email = self.email.data.lower()).first()
        if not user:
            self.email.errors.append("Email not found")
            return False
        else:
            return True

class NewpasswordForm(Form):
    password = PasswordField('Password', [validators.Required("Please enter a password.")])
    submit = SubmitField("Reset")

    def validate(self):
        if not Form.validate(self):
            return False
        return True

class SearchForm(Form):
    search = StringField("Search", [validators.Required("This cant be empty.")])
    submit = SubmitField("Search")
    
    def validate(self):
        if not Form.validate(self):
            return False
        return True

class ChangeNickForm(Form):
    nickname = StringField("Search", [validators.Required("This cant be empty.")])
    password = PasswordField('Password', [validators.Required("Please enter a password.")])
    submit = SubmitField("Change")

    def validate(self):
        if not Form.validate(self):
            return False
        user = User.query.filter_by(nickname = session['nick']).first()
        if user and user.check_password(self.password.data):
            return True
        else:
            self.password.errors.append("Wrong password")
            return False

class ChangePasswordForm(Form):
    old_password = PasswordField('Password', [validators.Required("Please enter a password.")])
    new_password = PasswordField('Password', [validators.Required("Please enter a password.")])
    submit = SubmitField("Change")

    def validate(self):
        if not Form.validate(self):
            return False
        user = User.query.filter_by(nickname = session['nick']).first()
        if user and user.check_password(self.old_password.data):
            return True
        else:
            self.old_password.errors.append("Wrong password")
            return False
        

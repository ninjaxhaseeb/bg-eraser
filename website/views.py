from flask import Blueprint, render_template,session

views = Blueprint('views', __name__)

@views.route('/')
def home():
    user = session.get('user')  
    return render_template("home.html", user=user)

@views.route("/terms")
def terms():
    user = session.get("user")
    return render_template("terms.html",user=user)
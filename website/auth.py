from flask import Blueprint,render_template,request,redirect,url_for,session,flash
import json
import os
from werkzeug.security import generate_password_hash,check_password_hash
import random
from datetime import datetime,timedelta
from .utils import send_email,load_users,save_users




auth = Blueprint('auth',__name__)

@auth.route('/login',methods=['GET', 'POST'])
def login():
    error_message = None

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            error_message = "Email and password are required!"
            return render_template("login.html", error=error_message)

        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "users.json")
        try:
            with open(file_path, "r") as f:
                users = json.load(f)
        except FileNotFoundError:
            users = []

        user_found = False
        for user in users:
            if user['email'] == email:
                user_found = True
                from werkzeug.security import check_password_hash
                if check_password_hash(user['password'], password):
                    session['user'] = {
                        "username": user['username'],
                        "email": user['email']
                    }
                    return redirect(url_for('views.home'))  # ✅ must RETURN
                else:
                    flash("Wrong Email or Password")
                    return render_template("login.html", error=error_message)

        if not user_found:
            flash("Wrong Email or Password")
            return render_template("login.html", error=error_message)

    # GET request → always return template
    return render_template("login.html", error=error_message)

@auth.route('/dashboard')
def dashboard():
    user = session.get('user')
    if not user:
        return redirect(url_for('auth.login'))  # redirect if not logged in
    return render_template('home.html', user=user)

@auth.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('views.home'))

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        agree = request.form.get("agreeTerms")
        
        
        # Server-side T&C check
        if not agree:
            flash("You must agree to the Terms & Conditions to sign up.")
            return redirect(url_for("auth.signup"))
        
        users = load_users()
        if any(user["email"] == email for user in users):
            flash("Email is already registered. Please login.")
            return redirect(url_for("auth.login"))
        
        otp = str(random.randint(100000, 999999))
        
        session["signup_otp"] = otp
        session["signup_email"] = email
        session["signup_username"] = request.form["username"]
        session["signup_password"] = request.form["password"]
        print("Sending OTP to",email)
        send_email(email, otp)
        return redirect(url_for("auth.verify_otp"))


    # Safety check
        if not username or not email or not password:
           return "All fields are required!", 400

        from werkzeug.security import generate_password_hash
        hashed_password = generate_password_hash(password)
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "users.json")
    # Read existing users
        try:
            with open(file_path, "r") as f:
                users = json.load(f)
        except FileNotFoundError:
            users = []

    # Add new user
        users.append({
        "username": username,
        "email": email,
        "password": hashed_password
        })

    # Save back to JSON
        with open(file_path, "w") as f:
            json.dump(users, f, indent=4)

        return redirect("/login")
    
    return render_template("signup.html")

@auth.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    if request.method == "POST":
        entered_otp = request.form["otp"]
        if entered_otp == session.get("signup_otp"):
            # OTP is correct, add user to your JSON storage
            new_user = {
                "username": session["signup_username"],
                "email": session["signup_email"],
                "password": generate_password_hash(session["signup_password"])
            }
            # load JSON, append new_user, save JSON
            users = load_users()  # your existing function to load users
            users.append(new_user)
            save_users(users)     # your existing function to save users

            # Log in the user automatically
            session["user"] = {"username": new_user["username"], "email": new_user["email"]}

            # Clear OTP from session
            session.pop("signup_otp")
            session.pop("signup_username")
            session.pop("signup_email")
            session.pop("signup_password")

            return redirect(url_for("views.home"))
        else:
            flash("Incorrect OTP. Try again.")
            return redirect(url_for("auth.verify_otp"))

    # GET request: show OTP form
    return render_template("verify_email.html")

@auth.route('/reset-password')
def reset_password():
    return '<h1> Reset Password Page </h1>'
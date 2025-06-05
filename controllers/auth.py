from flask import Blueprint, request, render_template, flash, redirect, url_for
from models import db, User
from werkzeug.security import check_password_hash, generate_password_hash

api = Blueprint('auth', __name__)

@api.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("User does not exist.")
            return redirect(url_for('auth.login'))

        if not check_password_hash(user.password, password):
            flash("Incorrect password.")
            return redirect(url_for('auth.login'))

        if user.is_admin:
            return redirect(url_for('auth.admin_dashboard'))
        else:
            return redirect(url_for('auth.user_dashboard')) 

    return render_template("login.html")


@api.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form.get("phone")
        address = request.form.get("address")
        pincode = request.form.get("pincode")

        if not email or not password:
            flash("Email and password are required.")
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash("Email already registered.")
            return redirect(url_for('auth.register'))

        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            phone=phone,
            address=address,
            pincode=pincode
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.")
        return redirect(url_for('auth.login'))

    return render_template("register.html")

@api.route("/admin/dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")

@api.route("/user/dashboard")
def user_dashboard():
    return render_template("user_dashboard.html")
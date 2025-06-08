from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from models import db, User, Lot, Spot
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
        
        session['user_id'] = user.id
        session['is_admin'] = user.is_admin
        session['username'] = user.name
        
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
        if len(phone) != 10:
            flash("Phone number must be 10 digits.")
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
    lots = Lot.query.all()
    return render_template("admin/dashboard.html", lots=lots)

@api.route("/user/dashboard")
def user_dashboard():
    return render_template("user/dashboard.html")

@api.route('/admin/add_lot', methods=["GET", "POST"])
def add_lot():
    if request.method == "POST":
        name = request.form.get("name")
        price_per_hour = request.form.get("price")
        address = request.form.get("address")
        pincode = request.form.get("pincode")
        total_spots = request.form.get("max")

        if not name or not price_per_hour or not address or not pincode or not total_spots:
            flash("All fields are required.")
            return redirect(url_for('auth.add_lot'))
        
        try:
            price_per_hour = float(price_per_hour)
            total_spots = int(total_spots)
        except ValueError:
            flash("Price must be a number and total spots must be an integer.")
            return redirect(url_for('auth.add_lot'))

        new_lot = Lot(
            name=name,
            price_per_hour=price_per_hour,
            address=address,
            pincode=pincode,
            total_spots=total_spots
        )

        db.session.add(new_lot)
        db.session.commit()
        
        for i in range(int(total_spots)):
            spot = Spot(
                lot_id=new_lot.id,
                spot_number=f"Spot {i + 1}",
                status=False
            )
            db.session.add(spot)
        db.session.commit()

        flash("Parking lot created successfully!")
        return redirect(url_for('auth.admin_dashboard'))
    return render_template("admin/add_lot.html")

@api.route('/admin/delete_lot/<int:lot_id>')
def delete_lot(lot_id):
    lot = Lot.query.get_or_404(lot_id)
    if any(spot.status for spot in lot.spots):
        flash("Cannot delete lot with occupied spots.")
        return redirect(url_for('auth.admin_dashboard'))
    Spot.query.filter_by(lot_id=lot.id).delete()
    db.session.delete(lot)
    db.session.commit()
    flash("Parking lot deleted successfully!")
    return redirect(url_for('auth.admin_dashboard'))

@api.route('/admin/edit_lot/<int:lot_id>', methods=["GET", "POST"])
def edit_lot(lot_id):
    lot = Lot.query.get_or_404(lot_id)

    if request.method == "POST":

        name = request.form.get("name")
        price_per_hour = request.form.get("price")
        address = request.form.get("address")
        pincode = request.form.get("pincode")
        new_total_spots = request.form.get("max")

        try:
            price_per_hour = float(price_per_hour)
            new_total_spots = int(new_total_spots)
        except ValueError:
            flash("Price must be a number and total spots must be an integer.")
            return redirect(url_for('auth.edit_lot', lot_id=lot_id))

        lot.name = name
        lot.price_per_hour = price_per_hour
        lot.address = address
        lot.pincode = pincode

        old_total_spots = lot.total_spots

        if new_total_spots > old_total_spots:
            for i in range(old_total_spots + 1, new_total_spots + 1):
                new_spot = Spot(
                    lot_id=lot.id,
                    spot_number=f"Spot {i}",
                    status=False
                )
                db.session.add(new_spot)

        elif new_total_spots < old_total_spots:
            extra_spots = Spot.query.filter_by(lot_id=lot.id).order_by(Spot.id.desc()).limit(old_total_spots - new_total_spots).all()
            for spot in extra_spots:
                db.session.delete(spot)

        lot.total_spots = new_total_spots

        db.session.commit()
        flash("Lot updated successfully!")
        return redirect(url_for('auth.admin_dashboard'))
    
    return render_template("admin/edit_lot.html", lot=lot)

@api.route('/admin/spot/<int:spot_id>')
def view_spot(spot_id):
    spot = Spot.query.get_or_404(spot_id)
    return render_template("admin/view_spot.html", spot=spot)

@api.route('/admin/spot/<int:spot_id>/delete', methods=["POST"])
def delete_spot(spot_id):
    spot = Spot.query.get_or_404(spot_id)

    if spot.status:
        flash("Cannot delete occupied spot.")
        return redirect(url_for('auth.view_spot', spot_id=spot.id))

    lot = spot.lot
    db.session.delete(spot)
    lot.total_spots -= 1
    db.session.commit()

    flash("Spot deleted successfully.")
    return redirect(url_for('auth.admin_dashboard'))

@api.route("/admin/dashboard/users")
def admin_users():
    users = User.query.all()
    return render_template("admin/users.html", users=users)
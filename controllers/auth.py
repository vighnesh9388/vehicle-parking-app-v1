from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from models import db, User, Lot, Spot, Reserve
from werkzeug.security import check_password_hash, generate_password_hash
import math

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
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    lots = Lot.query.all()
    return render_template("admin/dashboard.html", lots=lots, user=user, is_admin=True)

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
        db.session.flush()
        
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

@api.route("/admin/spot/<int:spot_id>/details")
def view_occupied_spot(spot_id):
    spot = Spot.query.get_or_404(spot_id)

    reservation = Reserve.query.filter_by(spot_id=spot.id).order_by(Reserve.start_time.desc()).first()

    duration = datetime.now() - reservation.start_time
    hours = duration.total_seconds() / 3600
    estimated_cost = round(hours * reservation.cost_per_hour, 2)
    

    return render_template("admin/view_occupied_spot.html", reservation=reservation, estimated_cost=estimated_cost)


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

@api.route("/admin/user/<int:user_id>/reservations")
def user_parking_history(user_id):
    user = User.query.get_or_404(user_id)
    
    reservations = [
        {
            "id": r.id,
            "location": r.spot.lot.name,
            "address": r.spot.lot.address,
            "pincode": r.spot.lot.pincode,
            "vehicle_number": r.vehicle_number,
            "start_time": r.start_time,
            "end_time": r.end_time,
            "cost_per_hour": r.cost_per_hour
        }
        for r in Reserve.query.filter_by(user_id=user_id).order_by(Reserve.start_time.desc()).all()
    ]

    return render_template("admin/user_history.html", user=user, reservations=reservations)

@api.route("/admin/dashboard/search")
def admin_search():
    filter_by = request.args.get("filter_by")
    query = request.args.get("query")
    results = []

    if filter_by and query:
        if filter_by == "spot_id":
            from models import Spot  # adjust if needed
            spot = Spot.query.filter_by(id=query).first()
            if spot:
                results.append({
                    "type": "Spot",
                    "id": spot.id,
                    "lot_id": spot.lot_id,
                    "status": "Occupied" if spot.status else "Available"
                })
        elif filter_by == "user_id":
            from models import User
            user = User.query.filter_by(id=query).first()
            if user:
                results.append({
                    "type": "User",
                    "id": user.id,
                    "name": user.name,
                    "email": user.email
                })
        elif filter_by == "location":
            from models import Lot
            lots = Lot.query.filter(Lot.address.ilike(f"%{query}%")).all()
            for lot in lots:
                results.append({
                    "type": "Lot",
                    "id": lot.id,
                    "name": lot.name,
                    "address": lot.address,
                    "available": sum(1 for s in lot.spots if not s.status)
                })

    return render_template("admin/search.html", results=results, current_path="/admin/dashboard/search")

@api.route("/user/dashboard")
def user_dashboard():
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    lots = Lot.query.all()
    user_lots = []

    for lot in lots:
        available_spot = Spot.query.filter_by(lot_id=lot.id, status=False).first()
        user_lots.append({
            "id": lot.id,
            "name": lot.name,
            "address": lot.address,
            "pincode": lot.pincode,
            "price_per_hour": lot.price_per_hour,
            "available_spots": Spot.query.filter_by(lot_id=lot.id, status=False).count(),
            "first_available_spot_id": available_spot.id if available_spot else None
        })

    return render_template("user/dashboard.html", lots=user_lots, user=user, is_admin=False)

from datetime import datetime

@api.route("/user/book/<int:spot_id>", methods=["GET", "POST"])
def book_spot(spot_id):
    spot = Spot.query.get_or_404(spot_id)
    lot = Lot.query.get_or_404(spot.lot_id)
    user_id = session.get('user_id')

    if request.method == "POST":
        vehicle_number = request.form.get("vehicle_number")
        reservation = Reserve(
            spot_id=spot.id,
            user_id=user_id,
            vehicle_number=vehicle_number,
            start_time=datetime.now(),
            end_time= None,
            cost_per_hour=lot.price_per_hour
        )
        spot.status = True
        db.session.add(reservation)
        db.session.commit()
        flash("Reservation confirmed!")
        return redirect(url_for('auth.user_dashboard'))

    return render_template("user/reserve.html", spot=spot, lot=lot, user_id=user_id,)

@api.route("/user/reservations")
def user_reservations():
    reservations = [
        {
            "id": r.id,
            "location": r.spot.lot.name,
            "pincode": r.spot.lot.pincode,
            "address": r.spot.lot.address,
            "vehicle_number": r.vehicle_number,
            "start_time": r.start_time,
            "end_time": r.end_time,
            "cost_per_hour": r.cost_per_hour,
        }
        for r in Reserve.query.filter_by(user_id=session["user_id"]).order_by(Reserve.start_time.desc()).all()
    ]

    return render_template("user/reservations.html", reservations=reservations)

@api.route("/user/release/<int:reservation_id>", methods=["GET", "POST"])
def release_spot(reservation_id):
    reservation = Reserve.query.get_or_404(reservation_id)
    now = datetime.now()
    duration = datetime.now() - reservation.start_time
    hours = duration.total_seconds() / 3600
    cost = round(hours * reservation.cost_per_hour, 2)

    if request.method == "POST":
        reservation.end_time = now
        spot = Spot.query.get(reservation.spot_id)
        if spot:
            spot.status = False
        db.session.commit()
        flash(f"Payment of ${cost} was successful!")
        return redirect(url_for('auth.user_reservations'))

    return render_template("user/release.html", reservation=reservation, now=datetime.now(), estimated_cost=cost)



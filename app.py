from flask import Flask, render_template, request
from models import db, User
from werkzeug.security import generate_password_hash
from controllers.auth import api as auth_api
def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.secret_key = "shh-its-a-secret"
    
    db.init_app(app)

    from models import lot, spot, reserve, user
    with app.app_context():
        db.create_all()
        
        if not User.query.filter_by(id=0).first():
            db.session.add(User(
                id=0,
                name='admin',
                email='admin@email.com',
                password=generate_password_hash('admin'),
                is_admin=True,
            ))
            db.session.commit()
    
    app.register_blueprint(auth_api)
    
    @app.route("/")
    def home():
        return render_template("home.html")
    
    @app.context_processor
    def inject_request():
        return dict(request=request)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
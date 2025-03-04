from app import app, db, Admin
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    # Create a default admin if one doesn't exist
    if not Admin.query.filter_by(email='admin@example.com').first():
        hashed_pw = generate_password_hash('badri@26')
        admin = Admin(name='Admin', email='badrinathachanta@gmail.com', hashed_password=hashed_pw)
        db.session.add(admin)
        db.session.commit()
    print("Tables created and admin initialized!")

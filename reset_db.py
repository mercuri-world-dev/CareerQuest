# reset_db.py
import os
from features.jobs.routes import db, User
from database import Role
from __init__ import create_app

app = create_app()

# Delete the database file if it exists
db_path = 'instance/careerquest.db'
if os.path.exists(db_path):
    print(f"Removing existing database: {db_path}")
    os.remove(db_path)
    print("Database file removed.")

with app.app_context():
    print("Creating new database tables...")
    db.create_all()
    
    # Add roles
    roles = [
        Role(name='user', description='Regular job seeker'),
        Role(name='company', description='Company posting jobs'),
        Role(name='admin', description='Administrator')
    ]
    db.session.add_all(roles)
    db.session.commit()
    print("Roles created successfully")
    
    # Add admin user
    admin_user = User(username='admin', email='admin@careerquest.com')
    admin_user.set_password('admin123')  # Change this in production!
    admin_role = Role.query.filter_by(name='admin').first()
    if admin_role:
        admin_user.roles.append(admin_role)
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created successfully")
    
    print("Database setup complete!")
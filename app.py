from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__, template_folder='templates')

# Update the SQLALCHEMY_DATABASE_URI for MySQL:
# Format: mysql+pymysql://<username>:<password>@<host>/<database>
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Tempest%4026@localhost/robovanza'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 3600,  # Recycle connections every hour (adjust based on your MySQL wait_timeout)
    'pool_pre_ping': True   # Check connection health before using
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'Robotics_cbit'

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

db = SQLAlchemy(app)

# --------------------
# Database Models
# --------------------

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.Date, nullable=False)
    rule_book = db.Column(db.String(200))  # File path or URL to the PDF
    
    teams = db.relationship('Team', back_populates='event', cascade="all, delete")
    matches = db.relationship('Match', back_populates='event', cascade="all, delete")

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(100), nullable=False)
    team_members = db.Column(db.Text, nullable=False)  # Comma separated names
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    event = db.relationship('Event', back_populates='teams')

class Match(db.Model):
    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    team1_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    team2_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)  # For one-team events
    team1_score = db.Column(db.Integer, default=0)
    team2_score = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='ongoing')  # 'ongoing' or 'ended'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    event = db.relationship('Event', back_populates='matches')
    team1 = db.relationship('Team', foreign_keys=[team1_id])
    team2 = db.relationship('Team', foreign_keys=[team2_id])

class Admin(db.Model, UserMixin):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    hashed_password = db.Column(db.String(200), nullable=False)

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))
# --------------------
# Routes
# --------------------

# Public route: display matches (both ongoing and ended)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/team')
def team():
    return render_template('team.html')
@app.route('/matches')
def matches():
    ongoing_matches = Match.query.filter_by(status='ongoing').all()
    ended_matches = Match.query.filter_by(status='ended').all()
    return render_template('matches.html', ongoing_matches=ongoing_matches, ended_matches=ended_matches)

# --------------------
# Admin Authentication Routes
# --------------------

# Admin authentication routes
# @app.route('/login', methods=['GET', 'POST'])
# def admin_login():
#     if current_user.is_authenticated:
#         return redirect(url_for('admin_dashboard'))

#     if request.method == 'POST':
#         email = request.form.get('email')
#         password = request.form.get('password')
#         admin = Admin.query.filter_by(email=email).first()

#         if admin and check_password_hash(admin.hashed_password, password):
#             login_user(admin)
#             return redirect(url_for('admin_dashboard'))
#         flash('Invalid email or password')
#     return render_template('admin_login.html')

# Change the login route to /admin/login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        admin = Admin.query.filter_by(email=email).first()

        if admin and check_password_hash(admin.hashed_password, password):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        flash('Invalid email or password')
    return render_template('admin_login.html')

# Add a redirect from /login to /admin/login
@app.route('/login')
def login_redirect():
    return render_template('admin.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('login_redirect'))

# @app.route('/admin/dashboard')
# @login_required
# def admin_dashboard():
#     return render_template('admin_dashboard.html')




# --------------------
# Dashboard Route
# --------------------

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    ongoing_matches = Match.query.filter_by(status='ongoing').all()
    ended_matches = Match.query.filter_by(status='ended').all()
    teams = Team.query.all()
    events = Event.query.all()
    return render_template('admin_dashboard.html',
                           ongoing_matches=ongoing_matches,
                           ended_matches=ended_matches,
                           teams=teams,
                           events=events)



@app.route('/admin/add_event', methods=['POST'])
@login_required
def add_event():
    event_name = request.form.get('event_name')
    description = request.form.get('description')
    event_date = request.form.get('event_date')

    if not event_name or not event_date:
        flash("Event name and date are required!", "error")
        return redirect(url_for('admin_dashboard'))

    new_event = Event(event_name=event_name, description=description, event_date=event_date)
    db.session.add(new_event)
    db.session.commit()
    flash("Event added successfully!")
    
    return redirect(url_for('admin_dashboard'))
@app.route('/admin/delete_event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get(event_id)
    if event:
        db.session.delete(event)
        db.session.commit()
        flash("Event deleted successfully!", "success")
    else:
        flash("Event not found!", "error")
    
    return redirect(url_for('admin_dashboard'))


# --------------------
# Team Routes
# --------------------

# Route to list all teams (admin view)
@app.route('/admin/teams')
@login_required  # Add this decorator
def list_teams():
    teams = Team.query.all()
    events = Event.query.all()  # Add this to display event names
    return render_template('admin_dashboard.html', teams=teams, events=events)
# @app.route('/admin/add_team')
# @login_required
# def add_team():
#     events = Event.query.all()
#     return render_template('add_team.html', events=events)

# Route to add a new team
@app.route('/admin/add_team', methods=['GET', 'POST'])
@login_required  # Add this decorator
def add_team():
    if request.method == 'POST':
        team_name = request.form.get('team_name')
        team_members = request.form.get('team_members')  # comma-separated names
        email = request.form.get('email')
        phone = request.form.get('phone')
        event_id = request.form.get('event_id', type=int)
        
        new_team = Team(
            team_name=team_name,
            team_members=team_members,
            email=email,
            phone=phone,
            event_id=event_id
        )
        db.session.add(new_team)
        db.session.commit()
        flash("Team added successfully!")
        return redirect(url_for('admin_dashboard'))
    
    events = Event.query.all()
    return render_template('admin_dashboard.html', events=events)
# Route to delete a team
@app.route('/admin/delete_team/<int:team_id>', methods=['POST'])
@login_required  # Add this decorator
def delete_team(team_id):
    team = Team.query.get_or_404(team_id)
    db.session.delete(team)
    db.session.commit()
    flash("Team deleted successfully!")
    return redirect(url_for('admin_dashboard'))

# # --------------------
# # Match Routes
# # --------------------

# # Route to add a new match (admin creates match just before it begins)
# @app.route('/create_match', methods=['GET', 'POST'])
# def create_match():
#     if request.method == 'POST':
#         event_id = request.form.get('event_id', type=int)
#         team1_id = request.form.get('team1_id', type=int)
#         team2_id = request.form.get('team2_id')
#         # If team2 is not provided or empty (for one-team events), set to None
#         team2_id = int(team2_id) if team2_id and team2_id.isdigit() else None
        
#         new_match = Match(
#             event_id=event_id,
#             team1_id=team1_id,
#             team2_id=team2_id,
#             team1_score=0,
#             team2_score=0,
#             status='ongoing'
#         )
#         db.session.add(new_match)
#         db.session.commit()
#         flash("Match created successfully!")
#         return redirect(url_for('matches'))
    
#     teams = Team.query.all()
#     events = Event.query.all()
#     return render_template('create_match.html', teams=teams, events=events)

# # Route to delete a match
# @app.route('/delete_match/<int:match_id>', methods=['POST'])
# def delete_match(match_id):
#     match = Match.query.get_or_404(match_id)
#     db.session.delete(match)
#     db.session.commit()
#     flash("Match deleted successfully!")
#     return redirect(url_for('matches'))

# # Route to update match score and status (for live updates)
# @app.route('/admin/update_match/<int:match_id>', methods=['GET', 'POST'])
# def update_match(match_id):
#     match = Match.query.get_or_404(match_id)
#     if request.method == 'POST':
#         match.team1_score = request.form.get('team1_score', type=int)
#         match.team2_score = request.form.get('team2_score', type=int)
#         match.status = request.form.get('status')  # either 'ongoing' or 'ended'
#         db.session.commit()
#         flash("Match updated successfully!")
#         return redirect(url_for('matches'))
#     return render_template('update_match.html', match=match)



@app.route('/create_match', methods=['GET', 'POST'])
@login_required
def create_match():
    if request.method == 'POST':
        event_id = request.form.get('event_id')
        team1_id = request.form.get('team1_id')
        team2_id = request.form.get('team2_id') or None

        new_match = Match(
            event_id=event_id,
            team1_id=team1_id,
            team2_id=team2_id
        )
        db.session.add(new_match)
        db.session.commit()
        flash('Match created successfully!')
        return redirect(url_for('admin_dashboard'))

    events = Event.query.all()
    teams = Team.query.all()
    return render_template('admin_dashboard.html', events=events, teams=teams)

@app.route('/update_match/<int:match_id>', methods=['GET', 'POST'])
@login_required
def update_match(match_id):
    match = Match.query.get_or_404(match_id)
    if request.method == 'POST':
        match.team1_score = request.form.get('team1_score', type=int)
        match.team2_score = request.form.get('team2_score', type=int)
        match.status = request.form.get('status')
        db.session.commit()
        flash('Match updated successfully!')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_dashboard.html', match=match)

@app.route('/delete_match/<int:match_id>', methods=['POST'])
@login_required
def delete_match(match_id):
    match = Match.query.get_or_404(match_id)
    db.session.delete(match)
    db.session.commit()
    flash('Match deleted successfully!')
    return redirect(url_for('admin_dashboard'))

# --------------------
# API Route
# --------------------


@app.route('/api/live-scores')
def live_scores():
    # Retrieve all matches (both ongoing and ended)
    matches = Match.query.all()
    matches_data = []
    for match in matches:
        matches_data.append({
            'id': match.id,
            'event_name': match.event.event_name if match.event else "",
            'team1_name': match.team1.team_name if match.team1 else "",
            'team2_name': match.team2.team_name if match.team2 else "",
            'team1_score': match.team1_score,
            'team2_score': match.team2_score,
            'status': match.status
        })
    return jsonify({'matches': matches_data})

# @app.route('/api/live-scores')
# def live_scores():
#     ongoing_matches = Match.query.filter_by(status='ongoing').all()
#     matches_data = []
#     for match in ongoing_matches:
#         matches_data.append({
#             'id': match.id,
#             'team1_score': match.team1_score,
#             'team2_score': match.team2_score
#         })
#     return jsonify({'matches': matches_data})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Admin.query.filter_by(email='admin@example.com').first():
            hashed_pw = generate_password_hash('admin123')
            admin = Admin(name='Super Admin', email='admin@example.com', hashed_password=hashed_pw)
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True, port=int(os.getenv("PORT", 5000)))

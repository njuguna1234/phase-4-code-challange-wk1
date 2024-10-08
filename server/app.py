#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize migration
migrate = Migrate(app, db)

# Initialize the database
db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

# Get all heroes
@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([hero.to_dict() for hero in heroes]), 200

# Get hero by ID
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = Hero.query.get(id)
    if not hero:
        return {"error": "Hero not found"}, 404
    return jsonify(hero.to_dict()), 200

# Get all powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    return jsonify([power.to_dict() for power in powers]), 200

# Get power by ID
@app.route('/powers/<int:id>', methods=['GET'])
def get_power(id):
    power = Power.query.get(id)
    if not power:
        return {"error": "Power not found"}, 404
    return jsonify(power.to_dict()), 200

# Update power (PATCH request)
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    if not power:
        return {"error": "Power not found"}, 404

    data = request.get_json()
    description = data.get('description')

    # Validate description length
    if description and len(description) < 20:
        return {"error": "Description must be at least 20 characters long."}, 400

    power.description = description
    db.session.commit()

    return jsonify(power.to_dict()), 200

# Create new hero_power entry
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    strength = data.get('strength')
    hero_id = data.get('hero_id')
    power_id = data.get('power_id')

    # Validate strength
    if strength not in ['Strong', 'Weak', 'Average']:
        return {"error": "Strength must be 'Strong', 'Weak', or 'Average'."}, 400

    # Validate hero and power existence
    hero = Hero.query.get(hero_id)
    power = Power.query.get(power_id)
    if not hero or not power:
        return {"error": "Invalid hero or power ID."}, 404

    # Create new HeroPower entry
    hero_power = HeroPower(strength=strength, hero_id=hero_id, power_id=power_id)
    db.session.add(hero_power)
    db.session.commit()

    return jsonify(hero_power.to_dict()), 201

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5555, debug=True)

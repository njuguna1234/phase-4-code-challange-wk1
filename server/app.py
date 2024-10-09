#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)
class HeroListResource(Resource):
    def get(self):
        heroes = Hero.query.all()
        return jsonify([hero.to_dict(rules=('-hero_powers',)) for hero in heroes])
class HeroResource(Resource):
    def get(self, id):
        hero = Hero.query.get(id)
        if hero:
            return hero.to_dict(rules=('hero_powers', 'hero_powers.power'))
        return make_response(jsonify({"error": "Hero not found"}), 404)
class PowerListResource(Resource):
    def get(self):
        powers = Power.query.all()
        return jsonify([power.to_dict(rules=('-hero_powers',)) for power in powers])
class PowerResource(Resource):
    def get(self, id):
        power = Power.query.get(id)
        if power:
            return power.to_dict(rules=('-hero_powers',))
        return make_response(jsonify({"error": "Power not found"}), 404)
    def patch(self, id):
        power = Power.query.get(id)
        if not power:
            return make_response(jsonify({"error": "Power not found"}), 404)
        data = request.get_json()
        try:
            power.description = data['description']
            db.session.commit()
            return power.to_dict()
        except ValueError:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)
class HeroPowerResource(Resource):
    def post(self):
        data = request.get_json()
        strength = data.get('strength')
        power_id = data.get('power_id')
        hero_id = data.get('hero_id')
        
        try:
            hero_power = HeroPower(strength=strength, power_id=power_id, hero_id=hero_id)
            db.session.add(hero_power)
            db.session.commit()
            
            # Explicitly set response status code to 201
            response = make_response(jsonify(hero_power.to_dict(rules=('hero', 'power'))), 201)
            return response
        except ValueError:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

# Route setup
api.add_resource(HeroListResource, '/heroes')
api.add_resource(HeroResource, '/heroes/<int:id>')
api.add_resource(PowerListResource, '/powers')
api.add_resource(PowerResource, '/powers/<int:id>')
api.add_resource(HeroPowerResource, '/hero_powers')

if __name__ == '__main__':
    app.run(port=5555, debug=True)



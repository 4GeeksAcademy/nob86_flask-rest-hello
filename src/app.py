"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    planets = Planet.query.all()
    result = [planet.serialize() for planet in planets]

    return jsonify(result), 200


@app.route('/user/<int:id>', methods=['GET'])
def handle_hi():

    planet = Planet.query.get(id)
    if planet is None :
        return jsonify({'message':'404 do not exist'}), 404
    #result = [planet.serialize() for planet in planets]

    return jsonify(planet.serialize()), 200

@app.route('/planet', methods=['POST'])
def create_planets():
    body = request.json
    new_planet = Planet(body.name, body.description)
    db.session.add(new_planet)
    db.session.commit()#enviar datos a la db    
    return jsonify(new_planet.serialize()), 200


@app.route('/planet/<int:id>', methods=['DELETE'])
def delete_planets(id):
    
    
    new_planet = Planet(body.name, body.description)

    planet = Planet.query.get(id)

    if(planet is None):
        return jsonify({'message': 'do not exist for delete'})
    db.session.delete(planet)#maneja el delete pero no lo envia
    db.session.commit()#enviar datos a la db    
    return jsonify(new_planet.serialize()), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

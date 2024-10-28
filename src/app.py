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
from models import db, User, Planet, People, Favorite
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
def get_users():

    users = User.query.all()
    result = [user.serialize() for user in users]

    return jsonify(result), 200


@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):

    user = User.query.get(id)
    if user is None :
        return jsonify({'message':'404 do not exist'}), 404
    #result = [planet.serialize() for planet in planets]

    return jsonify(user.serialize()), 200

@app.route('/people', methods=['GET'])
def get_peoples():

    peoples = People.query.all()
    result = [people.serialize() for people in peoples]

    return jsonify(result), 200


@app.route('/people/<int:id>', methods=['GET'])
def get_people(id):

    people = People.query.get(id)
    if people is None :
        return jsonify({'message':'404 do not exist'}), 404
    #result = [planet.serialize() for planet in planets]

    return jsonify(people.serialize()), 200



@app.route('/planet', methods=['GET'])
def get_planets():

    planets = Planet.query.all()
    result = [planet.serialize() for planet in planets]

    return jsonify(result), 200


@app.route('/planet/<int:id>', methods=['GET'])
def get_planet(id):

    planet = Planet.query.get(id)
    if planet is None :
        return jsonify({'message':'404 do not exist'}), 404
    #result = [planet.serialize() for planet in planets]

    return jsonify(planet.serialize()), 200

@app.route('/user/favorite', methods=['GET'])
def get_favorites():

    favorites = Favorite.query.all()
    result = [favorite.serialize() for favorite in favorites]

    return jsonify(result), 200


@app.route('/favorite', methods=['POST'])
def create_favorites():
    data = request.json

    user_id = data.get('user_id')
    if user_id is None:
        return jsonify({'message': 'The user_id field is required'}), 400


    people_id = data.get('people_id')
    planet_id = data.get('planet_id')
    
    
    if people_id:

        favorite = Favorite.query.filter_by(user_id=user_id, people_id=people_id).first()

        if favorite:
            return jsonify({'message': 'This favorite is already exist'}), 400
        

        new_favorite = Favorite(user_id=user_id, people_id=people_id, planet_id=None)
    
        
            
    elif planet_id:

        favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()

        if favorite:
            return jsonify({'message': 'This favorite is already exist'}), 400
        
        new_favorite = Favorite(user_id=user_id, people_id=None, planet_id=planet_id)

    else:

        return jsonify({'message': 'You most provide a people_id or a planet_id'}), 400

    
    db.session.add(new_favorite)
    db.session.commit()#enviar datos a la db    
    
    return jsonify(new_favorite.serialize()), 200



@app.route('/favorite/<int:id>', methods=['DELETE'])
def delete_favorite(id):
    # favorite = Favorite.query.filter(db.and_(Favorite.user_id == 1, Favorite.character_id == People)).first()
    # favorite = Favorite.query.filter(db.and_(Favorite.user_id == 1, Favorite.character_id == Planet)).first()

    favorite = Favorite.query.get(id)
    

    if favorite is None:
        return jsonify({'message': 'this favorite does not exist'}), 404

    db.session.delete(favorite)#maneja el delete pero no lo envia
    db.session.commit()#enviar datos a la db 

    return jsonify({'message': 'Favorite deleted successfully'}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

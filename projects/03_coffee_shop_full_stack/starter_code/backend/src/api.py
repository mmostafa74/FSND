from flask import Flask, request, jsonify, abort
from flask_cors import CORS
import json

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES


@app.route('/drinks', methods=['GET'])
def get_all_drinks():
    try:
        drinks = Drink.query.all()
        formatted_drinks = [drink.short() for drink in drinks]

        return jsonify({
            'success': True,
            'drinks': formatted_drinks
        })

    except Exception as e:
        print(e)
        abort(404)


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(token):
    try:
        drinks = Drink.query.all()
        formatted_drinks = [drink.long() for drink in drinks]

        return jsonify({
            'success': True,
            'drinks': formatted_drinks
        })
    except Exception as e:
        print(e)
        abort(401)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_new_drink(token):
    body = request.get_json(force=True)

    title = body.get('title', None)
    recipe = body.get('recipe', None)

    print(title)

    if title is None or title == '' or recipe is None:
        abort(422)

    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })

    except Exception as e:
        print(e)
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_existing_drink(token, drink_id):
    body = request.get_json(force=True)

    title = body.get('title', None)
    recipe = body.get('recipe', None)

    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if title is None or recipe is None:
            abort(422)
        else:
            drink.title = title
            drink.recipe = json.dumps(recipe)

        drink.update()

        drink_updated = Drink.query.filter(Drink.id == drink_id).first()

        return jsonify({
            'success': True,
            'drinks': [drink_updated.long()]
        })

    except Exception as e:
        print(e)
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_existing_drink(token, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    if drink is None:
        abort(404)
    else:
        try:
            drink.delete()

            return jsonify({
                'success': True,
                'delete': drink_id
            })

        except Exception as e:
            print(e)
            abort(422)

# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    'success': False,
                    'error': 422,
                    'message': 'unprocessable'
                    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'opject not found!'
    }), 404


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'error': 403,
        'message': 'forbidden to perform this operation!'
    }), 403


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': 'unauthorized user!'
    }), 401

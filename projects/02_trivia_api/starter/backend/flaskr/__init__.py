import json
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
        CORS config
    """

    CORS(app, resources={r'/*': {'origins': '*'}})

    @app.after_request
    def after_request(res):
        res.headers.add(
          'Access-Control-Allow-Headers',
          'Content-Type, Authorization'
        )
        res.headers.add(
          'Access-Control-Allow-Methods',
          'GET, POST, PATCH, DELETE, OPTIONS'
        )

        return res

    """
        app routes section
    """

    @app.route('/categories', methods=['GET'])
    def get_all_categories():
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]
        return jsonify({
            'success': True,
            'categories': formatted_categories
        })

    @app.route('/questions', methods=['GET'])
    def get_paginated_questions():
        questions = Question.query.order_by(Question.id).all()
        categories = Category.query.all()
        current_questions = paginate_questions(request, questions)
        formatted_categories = [category.format() for category in categories]

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'categories': formatted_categories,
            'current_category': None,
            'total_questions': len(questions)
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query\
                .filter(Question.id == question_id).one_or_none()
            if question is None:
                abort(404)
            else:
                question.delete()
                questions = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, questions)

                return jsonify({
                    'success': True,
                    'deleted': question_id,
                    'question': current_questions,
                    'total_questions': len(questions)
                })
        except Exception as ex:
            abort(422)
            print(ex)

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty
                )

            question.insert()

            questions = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, questions)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })

        except Exception as ex:
            abort(422)
            print(ex)

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        body = request.get_json()

        search = body.get('searchTerm', None)

        try:
            if search:
                questions = Question.query.order_by(Question.id)\
                    .filter(Question.title.ilike('%{}%'.format(search)))
                current_questions = paginate_questions(request, questions)

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(questions.all())
                })

        except Exception as ex:
            abort(422)
            print(ex)

    @app.route('/category/<int:category_id>/questions', methods=['GET'])
    def get_categorized_questions(category_id):
        questions = Question.query.filter(Question.category == category_id)\
            .all()
        formatted_questions = [question.format() for question in questions]
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]
        category = Category.query.get(category_id)

        if len(formatted_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': formatted_questions,
            'categories': formatted_categories,
            'current_category': Category.format(category),
            'total_questions': len(formatted_questions)
        })

    @app.route('/quizzes', methods=['POST'])
    def post_quiz():
        if request.data:
            search_data = json.loads(request.data)
            if (('quiz_category' in search_data
                    and 'id' in search_data['quiz_category'])
                    and 'previous_questions' in search_data):
                questions_query = Question.query.filter_by(
                    category=search_data['quiz_category']['id']
                ).filter(
                    Question.id.notin_(search_data["previous_questions"])
                ).all()
                length_of_available_question = len(questions_query)
                if length_of_available_question > 0:
                    return jsonify({
                            'success': True,
                            'question': Question.format(questions_query[
                             random.randrange(0, length_of_available_question)
                            ])
                    })
                else:
                    return jsonify({
                            'success': True,
                            'question': None
                    })
            abort(404)
        abort(422)

    """
        error hadlers section
    """

    @app.errorhandler(400)
    def handle_bad_request(e):
        return jsonify({
            'success': False,
            'status': 400,
            'message': 'bad request!'
        }), 400

    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({
            'success': False,
            'status': 404,
            'message': 'not found!'
        }), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(e):
        return jsonify({
            'success': False,
            'status': 405,
            'message': 'not allowed!'
        }), 405

    @app.errorhandler(422)
    def handle_unprocessable_entity(e):
        return jsonify({
            'success': False,
            'status': 422,
            'message': 'unprocessable entity!'
        }), 422

    @app.errorhandler(500)
    def handle_server_error(e):
        return jsonify({
            'success': False,
            'status': 500,
            'message': 'internal server error'
        }), 500

    return app

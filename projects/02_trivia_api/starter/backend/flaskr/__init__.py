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
            'total_questions': len(questions),
            'categories': formatted_categories,
            'current_category': None,
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
            print(1, ex)
            abort(404)

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json(force=True)

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
            print(ex)
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        body = request.get_json(force=True)

        search = body.get('searchTerm', None)

        try:
            if search:
                questions = Question.query.order_by(Question.id)\
                    .filter(Question.query.ilike('%{}%'.format(search)))
                current_questions = paginate_questions(request, questions)

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(questions.all())
                })

        except Exception as ex:
            print(2, ex)
            abort(422)

    @app.route('/category/<int:category_id>/questions', methods=['GET'])
    def get_categorized_questions(category_id):
        try:
            questions = Question.query\
                .filter(Question.category == category_id).all()
            formatted_questions = [question.format() for question in questions]
            categories = Category.query.all()
            formatted_categories = [
                category.format() for category in categories
                ]
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
        except Exception as ex:
            print(3, ex)
            abort(404)

    @app.route('/quizzes', methods=['POST'])
    def post_quiz():
        body = request.get_json(force=True)

        previous_questions = body.get('previous_questions', None)
        category = body.get('quiz_category', None)

        try:
            if category is not None:
                category_found = Category.query\
                    .filter(Category.id == category['id']).one_or_none()
            if category_found is not None:
                if previous_questions is not None:
                    questions = Question.query\
                        .filter(Question.category == category['id'])\
                        .filter(Question.id.notin_(previous_questions)).all()
                else:
                    questions = Question.query\
                        .filter(Question.category == category['id']).all()

                formatted_questions = [
                    question.format() for question in questions
                    ]

                if len(formatted_questions) != 0:
                    return jsonify({
                            'success': True,
                            'question': formatted_questions[random.randint(
                                0,
                                len(formatted_questions) - 1
                                )
                            ]
                    })
                else:
                    return jsonify({
                        'success': True,
                        'question': None
                    })
            abort(404)
        except Exception as ex:
            print(4, ex)
            abort(404)

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

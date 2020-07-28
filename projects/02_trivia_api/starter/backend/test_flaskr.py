import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.db_username = 'postgres'
        self.db_password = 'postgres'
        self.database_name = 'trivia_test'
        self.database_path = 'postgres://{}:{}@{}/{}'.format(
            self.db_username,
            self.db_password,
            'localhost:5432',
            self.database_name
            )
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question': 'plapla',
            'answer': 'pplpla',
            'category': 1,
            'difficulty': 3
        }

        self.new_quiz = {
            'previous_questions': [],
            'quiz_category': {
                'id': 2,
                'type': 'Art'
            }
        }

        self.null_category = {
            'previous_questions': [],
            'quiz_category': {}
        }

        self.not_found = {
            'previous_questions': [],
            'quiz_category': {
                'Type': 'Pla',
                'id': 1000
            }
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_retrieve_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_retrive_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 10)
        self.assertEqual(data['current_category'], None)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))

    def test_404_questions(self):
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'not found!')

    def test_delete_existing_question(self):
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], False)

    def test_delete_nonexitsting_question(self):
        res = self.client().delete('/questions/10000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(data['total_questions'])

    def test_questions_search(self):
        searchTerm = {'searchTerm': 'title'}
        res = self.client().post('/questions/search', json=searchTerm)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_get_categorized_questions(self):
        res = self.client().get('/category/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])

    def test_get_categorized_questions_not_found(self):
        res = self.client().get('/category/0/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'not found!')

    def test_play_quiz(self):
        res = self.client().post('/quizzes', json=self.new_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_play_quiz_unprocessable(self):
        res = self.client().post('/quizzes', json=self.null_category)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable entity!')

    def test_quiz_not_found(self):
        res = self.client().post('/quizzes', json=self.not_found)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'not found!')


# Make the tests conveniently executable
if __name__ == '__main__':
    unittest.main()

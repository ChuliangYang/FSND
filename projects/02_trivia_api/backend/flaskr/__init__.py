import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from backend.models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app)

    '''
  Use the after_request decorator to set Access-Control-Allow
  '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    '''
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

    @app.route('/categories', methods=['GET'])
    def retrieve_all_categories():
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]

        if categories is None:
            abort(404)

        else:
            return jsonify({
                'Success': True,
                'Categories': formatted_categories,
                'Total_Nums': len(formatted_categories)
            })

    '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  '''

    @app.route('/questions', methods=['GET'])
    def retrive_all_questions_by_page():
        nums_per_page = 10
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * nums_per_page
        end = start + nums_per_page
        questions = Question.query.all()

        if questions is None:
            abort(404)

        else:
            formatted_questions = [question.format() for question in questions]

            return jsonify({
                'success': True,
                'questions': formatted_questions[start:end],
                'total_nums': len(formatted_questions),
                'current_page': page
            })

    '''
  @TODO: 
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

    '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

    @app.router('/questions/<int:question_id>', methods=['DELETE'])
    def delete_specific_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
            abort(404)
        else:
            return jsonify({
                'success': True,
                'question': question.format()
            })

    '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

    @app.router('/questions', methods=['POST'])
    def post_new_question():
        body = request.get_json()

        new_content = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_score = body.get('score', None)

        search_term = body.get('search', None)

        if search_term is None:
            try:
                question = Question(question=new_content, answer=new_answer, category=new_category,
                                    difficulty=new_score)
                question.insert()
                return jsonify({
                    'success': True,
                    'created': question.id,
                    'question': question,
                    'total_questions': len(Question.query.all())
                })

            except:
                abort(422)

        else:
            questions = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()

            if questions is None:
                abort(404)
            else:
                formatted_questions = [question.format() for question in questions]

                return jsonify({
                    'success': True,
                    'questions': formatted_questions
                })

    '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

    '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

    @app.router('/questions/categories/<string:category_name>', methods=['GET'])
    def retrive_questions_for_specific_category(category_name):
        questions = Question.query.filter(Question.category == category_name).all()

        if questions is None:
            abort(404)

        else:
            formatted_questions = [question.format() for question in questions]
            return jsonify({
                'success': True,
                'category': category_name,
                'questions': formatted_questions,
                'total_nums': len(formatted_questions)
            })

    '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

    @app.router('/questions/random', methods=['POST'])
    def get_random_question():
        body = request.get_json()
        previous_questions_id = body.get('previous_questions', None)
        category = body.get('category', None)
        if category is None:
            abort(404)
        else:
            questions = Question.query.filter(Question.category == category,
                                              ~Question.id.in_(previous_questions_id)).all()

            if questions is None:
                abort(404)
            else:
                formatted_questions = [question.format() for question in questions]
                formatted_previous_questions_ids = [question.id for question in previous_questions_id]
                length = len(formatted_questions)
                index = random.randint(0, length - 1)
                formatted_previous_questions_ids.append({id: index})
                return jsonify({
                    'success': True,
                    'question': formatted_questions[index],
                    'previous_questions': formatted_previous_questions_ids
                })

    '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
    @app.errorhandler(404)
    def not_fount(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Not Found'
        }), 404

    @app.errorhandler(422)
    def not_fount(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable Entity'
        }), 422

    return app

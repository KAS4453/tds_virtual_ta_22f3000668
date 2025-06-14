from flask import Blueprint, request, jsonify
import base64
import time
import json
import logging
from ai_assistant_simple import answer_question, initialize_simple_data
from scraper import initialize_scraped_data
from app import db
from models import QuestionAnswer

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize on first import
initialize_scraped_data()
initialize_simple_data()


@api_bp.route('/', methods=['POST'])
def handle_question():
    """
    Main API endpoint to handle student questions.
    Expected JSON format:
    {
        "question": "What model should I use?",
        "image": "base64_encoded_image_data"  # optional
    }
    """
    start_time = time.time()
    
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "No JSON data provided"
            }), 400
        
        question = data.get('question', '').strip()
        if not question:
            return jsonify({
                "error": "Question is required"
            }), 400
        
        image_base64 = data.get('image')
        
        # Validate image if provided
        if image_base64:
            try:
                # Validate base64 format
                base64.b64decode(image_base64)
            except Exception:
                return jsonify({
                    "error": "Invalid base64 image data"
                }), 400
        
        logger.info(f"Processing question: {question[:100]}...")
        
        # Get answer from AI assistant
        result = answer_question(question, image_base64)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Store in database for analytics
        try:
            qa_record = QuestionAnswer(
                question=question,
                answer=result['answer'],
                links=json.dumps(result['links']),
                has_image=bool(image_base64),
                response_time=response_time
            )
            db.session.add(qa_record)
            db.session.commit()
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
        
        logger.info(f"Question answered in {response_time:.2f} seconds")
        
        return jsonify(result)
        
    except Exception as e:
        error_msg = f"Internal server error: {str(e)}"
        logger.error(error_msg)
        
        return jsonify({
            "error": error_msg
        }), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    """
    return jsonify({
        "status": "healthy",
        "message": "TDS Virtual TA API is running"
    })


@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get API usage statistics.
    """
    try:
        total_questions = QuestionAnswer.query.count()
        avg_response_time = db.session.query(db.func.avg(QuestionAnswer.response_time)).scalar() or 0
        questions_with_images = QuestionAnswer.query.filter_by(has_image=True).count()
        
        return jsonify({
            "total_questions": total_questions,
            "average_response_time": round(avg_response_time, 2),
            "questions_with_images": questions_with_images
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

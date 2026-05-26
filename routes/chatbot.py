from flask import Blueprint, request, jsonify
from utils.chatbot_ai import ChatbotAI
from models import db

chatbot_bp = Blueprint('chatbot', __name__)
bot = ChatbotAI()


@chatbot_bp.route('/api/chat', methods=['POST'])
def chat():
    """Process a chatbot message and return response."""
    data = request.get_json()

    if not data or not data.get('message'):
        return jsonify({
            'response': 'Please type a message!',
            'type': 'error'
        }), 400

    message = data['message'].strip()
    result = bot.process_message(message, db.session)

    return jsonify(result)

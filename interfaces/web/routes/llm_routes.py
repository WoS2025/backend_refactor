from flask import Blueprint, request, jsonify
import openai
import os

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

llm_bp = Blueprint('llm', __name__)

@llm_bp.route('/ask', methods=['POST'])
def llm_ask():
    data = request.json
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=512,
            temperature=0.7
        )
        answer = response.choices[0].message.content
        return jsonify({'result': answer}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

from flask import Flask, request, jsonify
import openai
import os
from flask_cors import CORS
import traceback  # for full error logs

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.get_json()
    prompt = data.get('prompt', '')
    print(f"Received prompt: {prompt}")

    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        print("OpenAI response:", response)
        image_url = response['data'][0]['url']
        return jsonify({'imageUrl': image_url})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Render sets PORT automatically
    app.run(host='0.0.0.0', port=port, debug=True)


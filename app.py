from flask import Flask, request, jsonify
import os
import traceback
from flask_cors import CORS
from openai import OpenAI

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize OpenAI client (uses OPENAI_API_KEY from environment)
client = OpenAI()

@app.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.get_json()
    prompt = data.get('prompt', '')
    print(f"Received prompt: {prompt}")

    try:
        response = client.images.generate(
            model="dall-e-2",  # or "dall-e-3" if you're approved for it
            prompt=prompt,
            size="512x512",
            n=1
        )
        print("OpenAI response:", response)
        image_url = response.data[0].url
        return jsonify({'imageUrl': image_url})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)

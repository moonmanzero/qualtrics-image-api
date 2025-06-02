from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import traceback

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize OpenAI client (automatically uses OPENAI_API_KEY from environment)
client = OpenAI()

@app.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.get_json()
    prompt = data.get('prompt', '')
    print(f"Received prompt: {prompt}")

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        print("OpenAI response:", response)
        image_url = response.data[0].url
        return jsonify({'imageUrl': image_url})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)

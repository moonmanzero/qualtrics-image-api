from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import traceback

app = Flask(__name__)
CORS(app)

client = OpenAI()

@app.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.get_json()
    prompt = data.get('prompt', '')
    print(f"Received prompt: {prompt}")

    try:
        # Send the request using chat/completions and gpt-image-1
        response = client.chat.completions.create(
            model="gpt-image-1",
            messages=[
                {"role": "user", "content": f"Generate an image of: {prompt}"}
            ]
        )

        # Extract image URL from the message content
        content = response.choices[0].message.content
        print("GPT response content:", content)

        # Assume content is just the image URL (which it typically is)
        return jsonify({'imageUrl': content.strip()})

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)

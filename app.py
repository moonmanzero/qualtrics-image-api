@app.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.get_json()
    prompt = data.get('prompt', '')
    print(f"Received prompt: {prompt}")  # Log the prompt

    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        print("OpenAI response:", response)  # Log raw response
        image_url = response['data'][0]['url']
        return jsonify({'imageUrl': image_url})
    except Exception as e:
        print("Error during OpenAI image generation:", e)  # Log the error
        return jsonify({'error': str(e)}), 500

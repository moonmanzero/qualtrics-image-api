from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import requests
import boto3
import time

# --- CONFIGURATION ---
app = Flask(__name__)
CORS(app)  # Allows calls from Qualtrics

# 1. OpenAI Configuration
# Note: The 'openai' library version > 1.0.0 uses a client, which is best practice.
# Your original code might use an older version, but this is the modern way.
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 2. AWS S3 Configuration (reads from Render Environment Variables)
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_S3_REGION')
)
S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')


# --- THE MAIN API ENDPOINT ---
@app.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.get_json()
    prompt = data.get('prompt', '')

    if not prompt:
        return jsonify({'error': 'Prompt is required.'}), 400

    try:
        # STEP 1: Call OpenAI to generate the image and get the temporary URL
        print(f"Generating image for prompt: '{prompt}'")
        response = client.images.generate(
            model="dall-e-3", # Using dall-e-3 for higher quality
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format='url'
        )
        temp_image_url = response.data[0].url
        print("Received temporary URL from OpenAI.")

        # STEP 2: Download the image data from the temporary URL
        image_response = requests.get(temp_image_url)
        # Raise an error if the download failed
        image_response.raise_for_status() 
        image_data = image_response.content
        print("Successfully downloaded image data.")

        # STEP 3: Upload the image data to your S3 bucket
        # Create a unique file name to avoid overwriting files
        file_name = f"image-{int(time.time())}.png" 
        
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=file_name,
            Body=image_data,
            ContentType='image/png',
            ACL='public-read'  # CRITICAL: This makes the uploaded image publicly viewable
        )
        print("Successfully uploaded image to S3.")

        # STEP 4: Construct the permanent, public URL for the image in S3
        aws_region = os.getenv('AWS_S3_REGION')
        permanent_url = f"https://{S3_BUCKET_NAME}.s3.{aws_region}.amazonaws.com/{file_name}"

        # STEP 5: Send the permanent URL back to Qualtrics
        return jsonify({'imageUrl': permanent_url})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500


# --- SERVER STARTUP ---
if __name__ == '__main__':
    # Render provides the PORT environment variable, so we use that.
    port = int(os.environ.get('PORT', 10000)) 
    app.run(host='0.0.0.0', port=port)
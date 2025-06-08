from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
import requests
import boto3
import time
import logging
import traceback

# --- ROBUST LOGGING CONFIGURATION ---
# This ensures all our log messages show up in Render
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- STANDARD CONFIGURATION ---
app = Flask(__name__)
CORS(app)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    logging.info("--- Received new request for /generate-image ---")
    data = request.get_json()
    prompt = data.get('prompt', '')

    if not prompt:
        logging.warning("Request failed: Prompt was empty.")
        return jsonify({'error': 'Prompt is required.'}), 400

    try:
        # STEP 1: OpenAI
        logging.info(f"STEP 1: Calling OpenAI with prompt: '{prompt[:50]}...'")
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format='url'
        )
        temp_image_url = response.data[0].url
        logging.info("STEP 1 SUCCESS: Received temporary URL from OpenAI.")

        # STEP 2: Download
        logging.info("STEP 2: Downloading image from temporary URL...")
        image_response = requests.get(temp_image_url)
        image_response.raise_for_status() 
        image_data = image_response.content
        logging.info("STEP 2 SUCCESS: Image data downloaded.")

        # STEP 3: S3 Upload
        file_name = f"image-{int(time.time())}.png" 
        logging.info(f"STEP 3: Uploading to S3 as '{file_name}'...")
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=file_name,
            Body=image_data,
            ContentType='image/png'
        )
        logging.info("STEP 3 SUCCESS: Image uploaded to S3.")

        # STEP 4: Construct URL
        aws_region = os.getenv('AWS_S3_REGION')
        permanent_url = f"https://{S3_BUCKET_NAME}.s3.{aws_region}.amazonaws.com/{file_name}"
        logging.info(f"STEP 4: Constructed permanent URL: {permanent_url}")

        # STEP 5: Success
        logging.info("--- Request finished successfully. ---")
        return jsonify({'imageUrl': permanent_url})

    except Exception as e:
        # THIS IS THE CRITICAL PART THAT WILL NOW WORK
        logging.error("---!!! AN ERROR OCCURRED !!!---")
        # This line will log the full, detailed error traceback
        logging.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


# --- SERVER STARTUP ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000)) 
    app.run(host='0.0.0.0', port=port)
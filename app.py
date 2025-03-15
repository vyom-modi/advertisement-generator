import os
import json
import uuid
import ast
import requests
from flask import Flask, request, render_template_string, jsonify, redirect, url_for
from groq import Groq

app = Flask(__name__)

# Initialize the Groq client with your API key
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Global dictionary to store generated results keyed by a unique submission ID
results = {}

# HTML template for the form page using Bootstrap
form_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Create Advertisement</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body { padding-top: 50px; }
    </style>
</head>
<body>
    <div class="container">
        <h2 class="mb-4 text-center">Create Your Advertisement</h2>
        <form method="post" action="{{ url_for('generate_ad') }}">
            <div class="form-group">
                <label for="brand_name">Brand Name:</label>
                <input type="text" class="form-control" id="brand_name" name="brand_name" required>
            </div>
            <div class="form-group">
                <label for="company_type">Company Type:</label>
                <select class="form-control" id="company_type" name="company_type" required>
                    <option value="Product">Product</option>
                    <option value="Service">Service</option>
                </select>
            </div>
            <div class="form-group">
                <label for="description">Description:</label>
                <textarea class="form-control" id="description" name="description" rows="3" required></textarea>
            </div>
            <div class="form-group">
                <label for="target_audience">Target Audience:</label>
                <textarea class="form-control" id="target_audience" name="target_audience" rows="2" required></textarea>
            </div>
            <div class="form-group">
                <label for="tone">Desired Tone for Ad:</label>
                <select class="form-control" id="tone" name="tone" required>
                    <option value="Professional">Professional</option>
                    <option value="Casual">Casual</option>
                    <option value="Enthusiastic">Enthusiastic</option>
                    <option value="Friendly">Friendly</option>
                </select>
            </div>
            <button type="submit" class="btn btn-primary btn-block">Generate Advertisement</button>
        </form>
    </div>
</body>
</html>
"""

# HTML template for the result page using Bootstrap, with a loading spinner placeholder for text and image
result_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Your Advertisement</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        body { padding-top: 50px; }
        .spinner {
            width: 3rem;
            height: 3rem;
            border: 0.4em solid rgba(0, 0, 0, 0.1);
            border-top: 0.4em solid #007bff;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin: auto;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .image-placeholder {
            position: relative;
            width: 512px;
            height: 512px;
            background-color: #f0f0f0;
        }
        .image-placeholder .img-spinner {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
    </style>
</head>
<body>
    <div class="container">
        <div id="loading" class="text-center">
            <h2>Generating your advertisement, please wait...</h2>
            <div class="spinner"></div>
        </div>
        
        <div id="result" style="display: none;">
            <h2 class="mb-4 text-center">Your Generated Advertisement</h2>
            <div class="card mb-4">
                <div class="card-body">
                    <h5 class="card-title">Ad Headline: </h5> 
                    <p id="ad_headline"></p>
                    <button class="btn btn-outline-secondary btn-sm" onclick="copyText('ad_headline')">Copy</button>
                </div>
            </div>
            <div class="card mb-4">
                <div class="card-body">
                    <h5 class="card-title">Ad Description:</h5>
                    <p id="ad_description"></p>
                    <button class="btn btn-outline-secondary btn-sm" onclick="copyText('ad_description')">Copy</button>
                </div>
            </div>
            <div class="card mb-4">
                <div class="card-body">
                    <h5 class="card-title">Relevant Hashtags:</h5>
                    <p id="relevant_hashtags"></p>
                    <button class="btn btn-outline-secondary btn-sm" onclick="copyText('relevant_hashtags')">Copy</button>
                </div>
            </div>
            <div class="card mb-4">
                <div class="card-body text-center">
                    <h5 class="card-title">Ad Image:</h5>
                    <div class="image-placeholder mx-auto mb-2">
                        <div id="img_spinner" class="img-spinner">
                            <div class="spinner"></div>
                        </div>
                        <img id="ad_image" src="" alt="Generated Ad Image" style="width: 512px; height: 512px; display: none;" onload="hideImgSpinner()">
                    </div>
                    <button id="download_btn" class="btn btn-success" onclick="downloadImage()">Download Image</button>
                </div>
            </div>
            <div class="text-center">
                <a href="{{ url_for('index') }}" class="btn btn-primary">Back to Home</a>
            </div>
        </div>
    </div>
    
    <script>
        function copyText(elementId) {
            const text = document.getElementById(elementId).innerText;
            navigator.clipboard.writeText(text).then(function() {
                alert("Copied: " + text);
            });
        }
        
        function hideImgSpinner() {
            document.getElementById("img_spinner").style.display = "none";
            document.getElementById("ad_image").style.display = "block";
        }
        
        function downloadImage() {
            const imageUrl = document.getElementById("ad_image").src;
            fetch(imageUrl)
                .then(response => response.blob())
                .then(blob => {
                    const a = document.createElement('a');
                    const objectUrl = URL.createObjectURL(blob);
                    a.href = objectUrl;
                    a.download = "generated_image.jpg";
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                })
                .catch(err => console.error("Download failed:", err));
        }
        
        function fetchResult() {
            fetch("/get_result?submission_id={{ submission_id }}")
                .then(response => response.json())
                .then(data => {
                    if(data.status === "processing") {
                        setTimeout(fetchResult, 2000);
                    } else if (data.status === "error") {
                        alert("Error: " + data.error);
                    } else {
                        // Populate the fields with returned data
                        document.getElementById("ad_headline").innerText = data.ad_headline;
                        document.getElementById("ad_description").innerText = data.ad_description;
                        document.getElementById("relevant_hashtags").innerText = data.relevant_hashtags;
                        document.getElementById("ad_image").src = data.image_url;
                        
                        // Hide loading and show result
                        document.getElementById("loading").style.display = "none";
                        document.getElementById("result").style.display = "block";
                    }
                })
                .catch(err => {
                    console.error(err);
                    setTimeout(fetchResult, 2000);
                });
        }
        
        window.onload = fetchResult;
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(form_html)

@app.route("/generate", methods=["POST"])
def generate_ad():
    # Retrieve form inputs
    brand_name = request.form.get("brand_name")
    company_type = request.form.get("company_type")
    description = request.form.get("description")
    target_audience = request.form.get("target_audience")
    tone = request.form.get("tone")

    # Construct the system prompt with the given variables.
    system_prompt = (
        "You are an experienced and expert digital marketing manager who is expert in crafting perfect relatable ads by linking the context of the product with human psychology. "
        "Now, generate and return the following in JSON format exactly following the schema provided below (ensure that the JSON keys match exactly and do not vary): "
        "{{\"ad_headline\": \"relevant Catchy, engaging and short headline for the ad\", "
        "\"ad_description\": \"2-3 sentences highlighting the product\", "
        "\"relevant_hashtags\": \"relevant hashtags for the ad followed by a comma like #cool, #new, #fun\", "
        "\"ad_image_prompt\": \"an ad image prompt, a complete, accurate, relevant and descriptive prompt to generate an image for this advertisement, based on provided details. Do not include any text or writing inside the image.\"}}. "
        "For a company named {brand_name}, who has this {company_type} and does {description} in a {tone} tone and is targeting {target_audience}."
    ).format(
        brand_name=brand_name,
        company_type=company_type,
        description=description,
        tone=tone,
        target_audience=target_audience,
    )

    # Generate a unique submission ID to track this job
    submission_id = str(uuid.uuid4())
    results[submission_id] = {"status": "processing"}

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt}],
            model="llama3-70b-8192",  # adjust model as needed
            temperature=0,
            stream=False,
            response_format={"type": "json_object"},
        )
        response_json = json.loads(chat_completion.choices[0].message.content)
        print("DEBUG response:", response_json)
    except Exception as e:
        error_msg = f"Error communicating with Groq API: {str(e)}"
        results[submission_id] = {"status": "error", "error": error_msg}
        return redirect(url_for("result_page", submission_id=submission_id))

    # Extract fields from the JSON response
    ad_headline = response_json.get("ad_headline", "")
    ad_description = response_json.get("ad_description", "")
    relevant_hashtags = response_json.get("relevant_hashtags", "")
    ad_image_prompt = response_json.get("ad_image_prompt", "")
    
    print("DEBUG ad_headline:", ad_headline)
    print("DEBUG ad_description:", ad_description)
    print("DEBUG relevant_hashtags:", relevant_hashtags)
    print("DEBUG ad_image_prompt:", ad_image_prompt)

    # Process the relevant hashtags to a comma-separated string
    if isinstance(relevant_hashtags, list):
        hashtags_str = ' '.join(relevant_hashtags)
    elif isinstance(relevant_hashtags, str) and relevant_hashtags.startswith("["):
        try:
            hashtags_list = ast.literal_eval(relevant_hashtags)
            if isinstance(hashtags_list, list):
                hashtags_str = ' '.join(hashtags_list)
            else:
                hashtags_str = relevant_hashtags
        except Exception:
            hashtags_str = relevant_hashtags
    else:
        hashtags_str = relevant_hashtags

    # Only update the result if all required fields have been generated
    if ad_headline and ad_description and ad_image_prompt:
        # Process the ad image prompt for pollinations.ai (replace spaces with underscores)
        processed_prompt = ad_image_prompt.replace(" ", "_")
        # Build the image URL; setting width and height to 512 for a square image
        image_url = f"https://image.pollinations.ai/prompt/{processed_prompt}?width=512&height=512"

        results[submission_id] = {
            "status": "ready",
            "ad_headline": ad_headline,
            "ad_description": ad_description,
            "relevant_hashtags": hashtags_str,
            "image_url": image_url
        }
        print("DEBUG final result:", results[submission_id])
    else:
        results[submission_id] = {"status": "processing"}
        print("DEBUG: Missing required fields, status remains processing.")

    return redirect(url_for("result_page", submission_id=submission_id))

@app.route("/result", methods=["GET"])
def result_page():
    submission_id = request.args.get("submission_id")
    # If submission_id is missing or not found, redirect to home page.
    if not submission_id or submission_id not in results:
        return redirect(url_for("index"))
    return render_template_string(result_html, submission_id=submission_id)

@app.route("/get_result", methods=["GET"])
def get_result():
    submission_id = request.args.get("submission_id")
    data = results.get(submission_id, {"status": "processing"})
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)

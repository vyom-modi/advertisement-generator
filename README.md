# Advertisement Generator Web App

This is a Flask-based web application that generates advertisements using a Groq-based LLM and the pollinations.ai image generation API. The app accepts user input (brand name, company type, description, target audience, and desired tone) and produces an advertisement with a catchy headline, marketing description, relevant hashtags, and an ad image.

## Features

- **User Input Form:** Collects details such as brand name, company type, description, target audience, and desired tone.
- **Ad Generation:** Uses a Groq-based LLM (llama3-70b-8192) to generate a JSON output that includes:
  - Ad headline
  - Ad description
  - Relevant hashtags
  - Ad image prompt
- **Image Generation:** Generates an ad image via the pollinations.ai API.
- **Direct Download:** Provides a button to directly download the generated image without redirecting.
- **Modern UI:** Built with Bootstrap for a responsive, modern look.
- **Loading Animations:** Displays spinners while waiting for ad content and image generation.
- **Back to Home:** A “Back to Home” button allows users to return to the main form page.

## Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vyom-modi/advertisement-generator.git
   cd advertisement-generator
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # For Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```


3. **Set your Groq API key:**
   Export your API key as an environment variable:
   ```bash
   export GROQ_API_KEY=your_api_key_here
   ```
   *(On Windows, use `set GROQ_API_KEY=your_api_key_here`)*

4. **Run the application:**
   ```bash
   python app.py
   ```
   Open your browser and navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Usage

1. Fill out the advertisement details in the form.
2. Click "Generate Advertisement".
3. Wait for the ad content and image to load (loading spinners will be displayed).
4. Once generated, review the ad details and use the "Copy" buttons to copy text fields.
5. Click "Download Image" to directly download the generated ad image.
6. Use the "Back to Home" button to return to the form page.

## Notes

- Ensure you have a stable internet connection as the app interacts with external APIs.
- Before running the app, ensure that pollinations.ai API is working by visiting the following link: https://pollinations.ai. If it is not working, the app will not work. Please wait for some time till the api is working again and then retry running the app.
- Modify model names, API URLs, or other configuration parameters in `app.py` as needed.

## License

This project is licensed under the MIT License.

from flask import Flask, render_template, jsonify, request
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import os
import requests
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure Flask app
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS')
app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
app.config['TIME_LIMIT'] = 30  # Time limit in minutes
app.config['SLEEP_TIME'] = datetime.time(22, 0)  # 10 PM

# Initialize Flask-Mail
mail = Mail(app)

# OpenAI API Key
openai.api_key = app.config['OPENAI_API_KEY']

# Global variable to store smoke reminders
smoke_times = []

def send_email(subject, body):
    """Send an email reminder."""
    with app.app_context():
        msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[app.config['MAIL_USERNAME']])
        msg.body = body
        mail.send(msg)

def remind_smoke():
    """Remind the user to smoke."""
    current_time = datetime.datetime.now()
    if current_time.time() < app.config['SLEEP_TIME']:
        smoke_times.append(current_time)
        send_email("Smoke Reminder", f"Time to smoke! Current time: {current_time}")
    else:
        send_email("Good Night", "It's time to sleep. No more smoking today!")

# Scheduler for smoke reminders
scheduler = BackgroundScheduler()
scheduler.add_job(remind_smoke, 'interval', minutes=app.config['TIME_LIMIT'])
scheduler.start()

@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

@app.route('/smoke_times', methods=['GET'])
def get_smoke_times():
    """Display the smoke reminder times."""
    return render_template('smoke_times.html', smoke_times=smoke_times)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """Chat with the AI."""
    if request.method == 'POST':
        user_message = request.form['message']
        try:
            # Updated to work with OpenAI's new API interface
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_message}
                ]
            )
            ai_reply = response.choices[0].message['content']  # Fixed key access for compatibility
        except Exception as e:
            ai_reply = f"An error occurred: {e}"
        return render_template('chat.html', user_message=user_message, ai_reply=ai_reply)
    return render_template('chat.html')

@app.route('/ask', methods=['POST'])
def ask_ai():
    """Handle AI queries via JSON."""
    user_input = request.json.get('message', '')
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional smoking cessation consultant."},
                {"role": "user", "content": user_input}
            ]
        )
        ai_response = response.choices[0].message['content'].strip()  # Updated to correct key access
        return jsonify({"response": ai_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add a new route for health data
@app.route('/health-data', methods=['GET'])
def get_health_data():
    """Fetch and return real-time world health data."""
    API_URL = "https://disease.sh/v3/covid-19/all"  # Replace with your desired API
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # Raise error for bad responses
        data = response.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/health_news', methods=['GET'])
def health_news():
    API_URL = "https://newsapi.org/v2/top-headlines"
    API_KEY = os.getenv('NEWS_API_KEY')
    params = {
        'category': 'health',
        'language': 'en',
        'apiKey': API_KEY
    }
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        articles = response.json().get('articles', [])
        if articles:
            top_article = articles[0]
            return jsonify({
                "title": top_article['title'],
                "description": top_article['description'],
                "source": top_article['source']['name']
            })
        else:
            return jsonify({"error": "No health news available"}), 404
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

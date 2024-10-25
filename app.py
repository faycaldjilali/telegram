from flask import Flask, request, Response
import cohere
import os
from dotenv import load_dotenv
import requests

# Init the Flask App
app = Flask(__name__)

# Load environment variables from the .env file
load_dotenv()

# Get the API key from the environment variable
COHERE_API_KEY = os.getenv('COHERE_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Initialize the Cohere client with the hidden API key
client = cohere.Client(COHERE_API_KEY)

# Function to generate a response using Cohere with the custom prompt
def generate_cohere_answer(question):
    prompt = (f"Q: {question}\n"
              "A: Please provide a detailed and comprehensive answer explaining the concept in depth.\n")
    try:
        response = client.generate(
            model='command-r-plus-08-2024',
            prompt=prompt,
            max_tokens=300,  # You can adjust the token limit as needed
            temperature=0.7,  # Control randomness in generation
        )
        answer = response.generations[0].text.strip()
        return answer
    except Exception as e:
        print(f"Error generating Cohere response: {e}")
        return "Sorry, I couldn't process your request at the moment."

# To get Chat ID and message sent by the user
def message_parser(message):
    chat_id = message['message']['chat']['id']
    text = message['message']['text']
    print("Chat ID:", chat_id)
    print("Message:", text)
    return chat_id, text

# To send message using the Telegram Bot API
def send_message_telegram(chat_id, text):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(url, json=payload)
    return response

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        msg = request.get_json()
        chat_id, incoming_que = message_parser(msg)
        answer = generate_cohere_answer(incoming_que)
        send_message_telegram(chat_id, answer)
        return Response('ok', status=200)
    else:
        return "<h1>Server is running!</h1>"

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=5000)

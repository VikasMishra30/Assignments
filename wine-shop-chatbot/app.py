from flask import Flask, request, jsonify, render_template, send_from_directory
import openai
import json
import os

app = Flask(__name__)

# Your OpenAI API key
openai.api_key = 'OpenAI-API-KEY'

# Load corpus from JSON file
with open('corpus.json', 'r') as f:
    corpus = json.load(f)

conversation_history = []

@app.route('/')
def serve_index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    conversation_history.append({"role": "user", "content": user_input})
    
    answer = get_answer_from_corpus(user_input, corpus)
    if answer:
        response = answer
    else:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation_history,
            max_tokens=50
        )['choices'][0]['message']['content'].strip()
        
        if 'wine' in user_input.lower():
            response = response
        else:
            response = "For more information, please contact us directly."
        
        conversation_history.append({"role": "assistant", "content": response})
    
    return jsonify({"message": response})

def get_answer_from_corpus(question, corpus):
    for qa in corpus:
        if qa["question"].lower() in question.lower():
            return qa["answer"]
    return None

if __name__ == '__main__':
    app.run(debug=True)

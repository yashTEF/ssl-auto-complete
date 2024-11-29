from flask import Flask, request, jsonify, send_from_directory
import tensorflow as tf
import numpy as np
import re
import random
import string
import os
import pickle

model = tf.keras.models.load_model('best_model.keras')

app = Flask(__name__, static_folder='frontend')

def custom_tokenize(code):
    tokens = re.findall(r'\w+|[^\w\s]', code)
    return tokens

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

with open('tokenizer.pkl', 'rb') as f:
    tokenizer = pickle.load(f)

max_sequence_length = 100

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    input_text = data.get('text', '')
    
    token_list = custom_tokenize(input_text)
    token_list = tokenizer.texts_to_sequences([' '.join(token_list)])[0]
    token_list = tf.keras.preprocessing.sequence.pad_sequences(
        [token_list], maxlen=max_sequence_length - 1, padding='pre'
    )
    
    predicted = model.predict(token_list, verbose=0)[0]

    top_n = 5
    top_indices = np.argsort(predicted)[-top_n:][::-1]

    predicted_words = [tokenizer.index_word.get(idx, '') for idx in top_indices]
    print(predicted_words)
    return jsonify({'suggested_words': predicted_words})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

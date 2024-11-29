import pickle
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import re

model = tf.keras.models.load_model('best_model_lstm.keras')

with open('tokenizer.pkl', 'rb') as f:
    tokenizer = pickle.load(f)

max_sequence_length = 100

app = Flask(__name__)
CORS(app)

def custom_tokenize(code):
    tokens = re.findall(r'\w+|[^\w\s]', code)
    return tokens

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    input_text = data.get('text', '')
    
    token_list = custom_tokenize(input_text)
    token_list = tokenizer.texts_to_sequences([' '.join(token_list)])[0]
    token_list = tf.keras.preprocessing.sequence.pad_sequences(
        [token_list], maxlen=max_sequence_length - 1, padding='pre'
    )
    
    predicted = model.predict(token_list, verbose=0)
    predicted_word_index = np.argmax(predicted, axis=-1)
    predicted_word = tokenizer.index_word.get(predicted_word_index[0], '')
    
    return jsonify({'suggested_word': predicted_word})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)

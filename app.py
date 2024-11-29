import pickle
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import re
import random
import string

model = tf.keras.models.load_model('best_model_lstm.keras')

with open('tokenizer.pkl', 'rb') as f:
    tokenizer = pickle.load(f)

max_sequence_length = 100

app = Flask(__name__)
CORS(app)

def custom_tokenize(code):
    tokens = re.findall(r'\w+|[^\w\s]', code)
    return tokens

def generate_random_variable_name():
    chars = string.ascii_lowercase
    random_name = 'var_' + ''.join(random.choice(chars) for _ in range(5))
    return random_name

def get_variables_in_scope(code):
    variable_names = []
    variable_regex = re.compile(r'\b(?:int|float|boolean|char|string|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)')
    matches = variable_regex.findall(code)
    variable_names.extend(matches)
    return variable_names

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    input_text = data.get('text', '')
    
    token_list = custom_tokenize(input_text)
    token_list = [tokenizer.word_index.get(word, 0) for word in token_list]
    token_list = [0] * (max_sequence_length - 1 - len(token_list)) + token_list[-(max_sequence_length - 1):]
    
    token_list = np.array(token_list).reshape(1, -1)
    
    predicted = model.predict(token_list, verbose=0)
    predicted_word_index = np.argmax(predicted, axis=-1)
    predicted_word = tokenizer.index_word.get(predicted_word_index[0], '')
    
    reserved_words = [
        'alignas', 'alignof', 'and', 'and_eq', 'asm', 'atomic_cancel', 'atomic_commit', 'atomic_noexcept',
        'auto', 'bitand', 'bitor', 'bool', 'break', 'case', 'catch', 'char', 'char8_t', 'char16_t', 'char32_t',
        'class', 'compl', 'concept', 'const', 'consteval', 'constexpr', 'constinit', 'const_cast', 'continue',
        'co_await', 'co_return', 'co_yield', 'decltype', 'default', 'delete', 'do', 'double', 'dynamic_cast',
        'else', 'enum', 'explicit', 'export', 'extern', 'false', 'float', 'for', 'friend', 'goto', 'if', 'inline',
        'int', 'long', 'mutable', 'namespace', 'new', 'noexcept', 'not', 'not_eq', 'nullptr', 'operator', 'or',
        'or_eq', 'private', 'protected', 'public', 'reflexpr', 'register', 'reinterpret_cast', 'requires', 'return',
        'short', 'signed', 'sizeof', 'static', 'static_assert', 'static_cast', 'struct', 'switch', 'synchronized',
        'template', 'this', 'thread_local', 'throw', 'true', 'try', 'typedef', 'typeid', 'typename', 'union',
        'unsigned', 'using', 'virtual', 'void', 'volatile', 'wchar_t', 'while', 'xor', 'xor_eq'
    ]
    variable_names_in_scope = get_variables_in_scope(input_text)
    
    if predicted_word in reserved_words or predicted_word in variable_names_in_scope:
        predicted_word = generate_random_variable_name()
    
    return jsonify({'suggested_word': predicted_word})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)

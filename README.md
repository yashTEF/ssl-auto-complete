# ssl-auto-complete

## Project Overview

`ssl-auto-complete` is a machine learning project aimed at predicting the next word in a given code snippet. The project leverages Recurrent Neural Networks (RNN) and Long Short-Term Memory (LSTM) networks to achieve accurate code completion.

## Features

- Custom tokenization to handle code-specific syntax.
- Model training with early stopping and checkpointing.
- Prediction function to suggest the next word in a code snippet.
- Example usage for quick testing.

## Installation

To install the required dependencies, run:

```bash
pip install -r requirements.txt
```

## Usage

1. **Prepare the Dataset**: Load and preprocess the dataset.
2. **Train the Model**: Train the RNN or LSTM model with the provided training script.
3. **Predict the Next Word**: Use the trained model to predict the next word in a code snippet.

## Example

```python
input_text = 'int main(void a, int i'
predicted_word = predict_next_word(model, tokenizer, input_text)
print(f'Next word prediction: {predicted_word}')
```

## Requirements

- Flask==2.3.3
- flask-sqlalchemy==3.0.5
- flask-migrate==4.0.4
- flask-login==0.6.2
- flask-wtf==1.1.1
- Jupyter==1.0.0
- notebook==7.0.3
- ipykernel==6.25.2
- numpy==1.26.0
- pandas==2.1.2
- matplotlib==3.8.0
- seaborn==0.13.0

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas.

## License

This project is licensed under the MIT License.

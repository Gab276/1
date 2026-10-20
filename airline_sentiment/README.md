# Airline tweet sentiment: Naive Bayes and a neural network

`Airline_Sentiment_NLP_Pipeline.ipynb` runs the two airline files through the
methods from the Naive Bayes notebook and Neural Networks Lecture 1:

- `airline_train_900.csv`: 900 tweets for training (300 negative, 300 neutral, 300 positive)
- `airline_test_60.csv`: 60 tweets for testing (20 of each label)

The notebook is saved with its outputs, so you can read the results before
running it.

## Run it on Google Colab

1. Download the notebook and both CSV files from this folder.
2. Open [colab.research.google.com](https://colab.research.google.com), choose
   `File → Upload notebook`, and pick `Airline_Sentiment_NLP_Pipeline.ipynb`.
3. Choose `Runtime → Run all`. When the upload button appears under
   "1. Load the Data", select both CSV files.

Colab already has spaCy, its `en_core_web_sm` model, scikit-learn, PyTorch and
matplotlib. The first cell installs any that are missing. The whole notebook
runs on the CPU in about a minute.

## Run it on your own computer

```sh
pip install spacy scikit-learn pandas torch matplotlib notebook
python -m spacy download en_core_web_sm
jupyter notebook Airline_Sentiment_NLP_Pipeline.ipynb
```

Keep the two CSV files in the same folder as the notebook.

## What the notebook does

1. Loads both files and prints some tweets from each label
2. Pre-processes each tweet: `re` removes handles (`@united`) and links, then
   spaCy lowercases the text and removes stopwords. It also turns HTML codes
   like `&amp;` back into characters and undoes the dataset's
   "Cancelled Flightled" / "Late Flightr" find-and-replace error.
3. Builds a bag of words with `CountVectorizer`, fit on the training tweets only
4. Trains Naive Bayes from scratch (`train_naive_bayes` / `test_naive_bayes`)
5. Trains `Pipeline(CountVectorizer, MultinomialNB(alpha=1))` and checks that it
   learns the same numbers as the scratch version
6. Predicts the 60 test tweets: accuracy, classification report, confusion
   matrix, and the tweets it got wrong
7. Lists the words that push a tweet toward each label (log-likelihood ratios)
8. Compares five pre-processing versions with 5-fold cross-validation on the
   training set
9. Trains a PyTorch network (`Linear → ReLU → Linear`, cross-entropy, Adam) on
   the same bag of words, using a validation split to pick the number of
   steps, and tries different learning rates, activations and hidden sizes
10. Learns a 2-D vector for every word with `EmbeddingBag` and plots them
11. Predicts new tweets that you type in

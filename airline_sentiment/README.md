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

Colab already has spaCy, scikit-learn, PyTorch and matplotlib. The first cell
installs any missing package, and the next cell downloads spaCy's
`en_core_web_sm` model if it is not there. The whole notebook runs on the CPU
in a minute or two.

## Run it on your own computer

```sh
pip install spacy scikit-learn pandas torch matplotlib notebook
python -m spacy download en_core_web_sm
jupyter notebook Airline_Sentiment_NLP_Pipeline.ipynb
```

Keep the two CSV files in the same folder as the notebook.

## What the notebook does

1. Loads both files
2. Prints some tweets from each label
3. Pre-processes each tweet: `re` removes handles (`@united`) and links, then
   spaCy lowercases the text and removes stopwords. It also turns HTML codes
   like `&amp;` back into characters and undoes the dataset's
   "Cancelled Flightled" / "Late Flightr" find-and-replace error.
4. Builds a bag of words with `CountVectorizer`, fit on the training tweets only
5. Trains Naive Bayes from scratch (`train_naive_bayes` / `test_naive_bayes`)
6. Trains `Pipeline(CountVectorizer, MultinomialNB(alpha=1))` and checks that it
   learns the same numbers as the scratch version
7. Predicts the 60 test tweets: accuracy, classification report, confusion
   matrix, and the tweets it got wrong
8. Lists the words that push a tweet toward each label (log-likelihood ratios)
9. Compares five pre-processing versions with 5-fold cross-validation on the
   training set
10. Trains a PyTorch network (`Linear → ReLU → Linear`, cross-entropy, Adam) on
    the same bag of words. A validation split picks the number of steps and
    compares learning rates, activations and hidden sizes. The final network is
    then retrained with 5 random seeds to show how much its accuracy varies.
11. Learns a 2-D vector for every word with `EmbeddingBag` and plots the 10
    strongest words of each label
12. Compares all the models in one table
13. Predicts new tweets that you type in

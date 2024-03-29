import nltk
from nltk.stem.lancaster import LancasterStemmer

stemmer = LancasterStemmer()

import numpy as np
import tensorflow as tf
import json
import random
import pickle
import os  # Import os module to check for file existence

# Load data
with open("intents.json") as file:
    data = json.load(file)
print(data)

# Initialize lists for data processing
try:
    with open("data.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)
except:
    words = []
    labels = []
    docs_x = []
    docs_y = []

    # Process data
    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])

        if intent["tag"] not in labels:
            labels.append(intent["tag"])

    # Stem and lower case our words and remove duplicates
    words = [stemmer.stem(w.lower()) for w in words if w not in ["?", "!", "."]]
    words = sorted(list(set(words)))
    labels = sorted(labels)

    # Prepare training and testing data
    training = []
    output = []
    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []
        wrds = [stemmer.stem(w.lower()) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)

    training = np.array(training)
    output = np.array(output)

    with open("data.pickle", "wb") as f:
        pickle.dump((words, labels, training, output), f)

model_file = "model.h5"

# Define the model
model = tf.keras.Sequential(
    [
        tf.keras.layers.Dense(8, activation="relu", input_shape=(len(training[0]),)),
        tf.keras.layers.Dense(8, activation="relu"),
        tf.keras.layers.Dense(len(output[0]), activation="softmax"),
    ]
)

# Compile the model
model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

if os.path.exists(model_file):
    print("Loading existing model...")
    model = tf.keras.models.load_model(model_file)
else:
    print("Training a new model...")
    model.fit(training, output, epochs=1000, batch_size=8)
    model.save(model_file)
    print("Model trained and saved.")

# Your bag_of_words function and chat function remain the same


def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1

    return np.array(bag)


def chat():
    print("Start talking with the bot (type quit to stop)!")
    while True:
        inp = input("You: ")
        if inp.lower() == "quit":
            break

        bag = bag_of_words(inp, words)
        results = model.predict(bag[np.newaxis, :])
        results_index = np.argmax(results)
        tag = labels[results_index]

        for tg in data["intents"]:
            if tg["tag"] == tag:
                responses = tg["responses"]

        print(random.choice(responses))


chat()

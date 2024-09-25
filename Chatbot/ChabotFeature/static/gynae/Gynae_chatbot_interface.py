import random
import json
import pickle
import numpy as np
import nltk

from nltk.stem import WordNetLemmatizer
from keras.models import load_model
from fuzzywuzzy import process  # For spell correction

lemmatizer = WordNetLemmatizer()
intents = json.loads(open('gynae/intents_gynae.json').read())

words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('gynae/gynae_chatbot_model_new.h5')

# Dictionary of medical terms for spell correction
medical_terms = words  # You can also add custom medical terms here

current_context = None  # To track the context of the conversation


def correct_spelling(sentence):
    """ Correct user input spelling using fuzzy matching """
    tokens = sentence.split()
    corrected_tokens = []
    for token in tokens:
        match, score = process.extractOne(token, medical_terms)
        if score > 80:  # 80% match threshold
            corrected_tokens.append(match)
        else:
            corrected_tokens.append(token)
    return ' '.join(corrected_tokens)


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words


def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)


def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list


def get_response(intents_list, intents_json):
    global current_context  # Access global context
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']

    for i in list_of_intents:
        if i['tag'] == tag:
            # Check if context filter matches current context
            if 'context_filter' in i and i['context_filter'] != current_context:
                continue  # Skip intents that don't match the current context

            # Set new context if available
            if 'context_set' in i:
                current_context = i['context_set']
            else:
                current_context = None  # Reset context if none is set

            result = random.choice(i['responses'])
            return result

    return "Oops, I don't understand you! Try using different words."


print("GO! Bot is running!")

while True:
    message = input("")

    # message = correct_spelling(message)  # Correct spelling mistakes
    # print(message)
    ints = predict_class(message)
    res = get_response(ints, intents)
    print(res)
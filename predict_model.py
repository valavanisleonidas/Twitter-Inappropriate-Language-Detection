import pickle
import sys
from os.path import abspath
from nltk.stem.porter import *
import warnings
warnings.filterwarnings("ignore")

FINAL_VECT = abspath("model/final_count_vect.pkl")
FINAL_TFIDF = abspath("model/final_tf_transformer.pkl")
FINAL_MODEL = abspath("model/final_model.pkl")

stemmer = PorterStemmer()


class preprocess_data():

    def preprocess(self, text_string):
        space_pattern = '\s+'
        giant_url_regex = ('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|'
                           '[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        mention_regex = '@[\w\-]+'
        retweet_regex = '^[! ]*RT'
        parsed_text = re.sub(space_pattern, ' ', text_string)
        parsed_text = re.sub(giant_url_regex, '', parsed_text)
        parsed_text = re.sub(mention_regex, '', parsed_text)
        parsed_text = re.sub(retweet_regex, '', parsed_text)
        stemmed_words = [stemmer.stem(word) for word in parsed_text.split()]
        parsed_text = ' '.join(stemmed_words)
        return parsed_text


sys.modules['data.preprocess_data'] = preprocess_data()

with open(FINAL_VECT, 'rb') as final_count_vect:
    count_vect = pickle.load(final_count_vect)
with open(FINAL_TFIDF, 'rb') as final_tf_transformer:
    tf_transformer = pickle.load(final_tf_transformer)
with open(FINAL_MODEL, 'rb') as final_model:
    lr_clf = pickle.load(final_model)
obj = [count_vect, tf_transformer, lr_clf]


def predict(input_text):
    input_counts = obj[0].transform(input_text)
    input_tfidf = obj[1].transform(input_counts)
    predicted = obj[2].predict(input_tfidf)
    return predicted


if __name__ == '__main__':

    while True:
        input_words = input("Enter input text: ")
        predicted_class = predict([input_words])
        print(['Hate speech', 'Offensive', 'Clean'][predicted_class[0]])

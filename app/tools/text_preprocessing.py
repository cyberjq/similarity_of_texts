import os
from typing import List, Tuple
import re
from gensim.models import doc2vec
from nltk.tokenize import sent_tokenize, word_tokenize
import pymorphy2


class TextPreprocessing:
    __punctuation = "!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~»«–“”—"

    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()
        self.stop_words = self.__read_custom_stop_words()
        self.my_stop_words = self.__read_stop_words()
        self.__filter_str = "1234567890_.№"

    @staticmethod
    def __read_stop_words():
        with open(f"{os.path.dirname(os.path.abspath(__file__))}/data/my_stop_words.txt", "r", encoding="utf-8") as f:
            return [item for item in f.read().splitlines()]

    @staticmethod
    def __read_custom_stop_words():
        with open(f"{os.path.dirname(os.path.abspath(__file__))}/data/custom_stop_words.txt", "r", encoding="utf-8") as f:
            return [item for item in f.read().splitlines()]

    def text_preprocessing(self, text: str,
                           is_lower: bool = True,
                           delete_punctuation: bool = True,
                           delete_stopwords: bool = True,
                           lemmatization: bool = True) -> Tuple[List[str], str]:
        if is_lower:
            text = text.lower()

        text = re.sub(r"https?://[^,\s]+,?", "", text)  # Удаление URL

        words = word_tokenize(text, language="russian")

        cleaned_words = []

        for word in words:

            word = "".join(filter(lambda a: a not in self.__filter_str, [a for a in word])).strip()

            if not word:
                continue

            if delete_punctuation and word in self.__punctuation:
                continue

            if word in self.my_stop_words:
                continue

            if lemmatization:
                word = self.morph.parse(word)[0].normal_form

            if delete_stopwords and word in self.stop_words:
                continue

            cleaned_words.append(word)

        return cleaned_words, text

    def get_filter_documents(self, texts, is_sentences: bool = False):
        if is_sentences:
            texts = [sentence for text in texts for sentence in sent_tokenize(text, language="russian")]

        filter_documents = [(index, self.text_preprocessing(text)[0]) for index, text in enumerate(texts)]
        filter_documents = list(filter(lambda x: x[1], filter_documents))
        return filter_documents, texts

    # def d2v_text_preprocessing(text: str,
    #                            is_lower: bool = True,
    #                            delete_punctuation: bool = True):
    #     words = text_preprocessing(text, is_lower, delete_punctuation)
    #     return doc2vec.TaggedDocument(words, [i])

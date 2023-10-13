import json
import re
import string
from loguru import logger

from langdetect import detect, DetectorFactory
from munch import DefaultMunch

as_class = DefaultMunch.fromDict
DetectorFactory.seed = 0

from application.parser.nlps import Nlps


class Phrase:
    exact = 0
    exact_lemmed = 0
    participant = 0
    imprecise = 0
    matches = []

    def __init__(self, text):
        self.text: str = text
        # self.__lang = detect(text)
        self.__lang: str = 'en'  # TODO: fix language detection
        self.__nlp = Nlps().__getattribute__(self.__lang)
        self.lemma: str = " ".join([token.lemma_ for token in self.__nlp(text)]).lower()

    def __repr__(self):
        return f"Phrase:{self.__lang}:{len(self.text.split())}"

    def values(self):
        reply = self.matches
        self.matches = []

        return reply


class Text:
    def __init__(self, text: str):
        self.lang = detect(text)
        self.text = text.replace('\n', '.')
        self.sentences = [Sentence(s_id, x, self.lang) for s_id, x in enumerate(re.split(r'(?<=[.!?])\s+', text))]

    def __repr__(self):
        return f"Text:{self.lang}:{len(self.sentences)}"


class Sentence:

    def __init__(self, sent_id, text, lang):
        self.sentence_id = sent_id
        self.lang = lang
        self.text: str = text
        self.__nlp = Nlps().__getattribute__(lang)
        self.lemmatized = None

    def __repr__(self):
        return f"Sentence:{self.lang}:{len(self.text.split())}"

    def clear_full_sentence(self):
        return self.text.translate(str.maketrans('', '', string.punctuation)).lower()

    def lemmatize(self, text) -> str:
        return " ".join([token.lemma_ for token in self.__nlp(text)]).lower()

    def get_matches(self, phrase: Phrase):
        return as_class(dict(
            exact=self.__match_exact(phrase),
            exact_lemmed=self.__match_exactlemmed(phrase),
            participant=self.__match_participant(phrase),
            imprecise=self.__match_imprecise(phrase),
        ))

    def __match_exact(self, phrase: Phrase) -> DefaultMunch:
        logger.debug(f"Phrase: {phrase.text}")

        sentence = self.clear_full_sentence()
        matches = re.findall(phrase.text, sentence)

        modified_sentence = re.sub(r'\b' + re.escape(phrase.text) + r'\b', '', sentence)
        self.lemmatized = self.lemmatize(modified_sentence)
        logger.debug(f'Исходный: {sentence}')
        logger.debug(f'Лемма: {self.lemmatized}')

        return as_class(dict(phrase=phrase.text,
                             sentence_id=self.sentence_id,
                             sentence=self.text,
                             count=len(matches)))

    def __match_exactlemmed(self, phrase: Phrase) -> DefaultMunch:
        sentence = self.lemmatized

        logger.debug(f"Phrase: {phrase.lemma}")

        matches = re.findall(r'\b' + re.escape(phrase.lemma) + r'\b', sentence)
        self.lemmatized = re.sub(r'\b' + re.escape(phrase.lemma) + r'\b', '', sentence)
        logger.debug(f'Лемма: {self.lemmatized}')
        return as_class(dict(phrase=phrase.text,
                             sentence_id=self.sentence_id,
                             sentence=self.text,
                             count=len(matches)))

    def __match_participant(self, phrase: Phrase) -> DefaultMunch:
        sentence = self.lemmatized
        logger.debug(f"Phrase: {phrase.lemma}")
        str_pattern = r'\b' + r'\b.*?\b'.join(map(re.escape, phrase.lemma.split())) + r'\b'
        return self.__re_search_lemmed(phrase, sentence, str_pattern)

    def __match_imprecise(self, phrase: Phrase) -> DefaultMunch:
        lemma_phrase = phrase.lemma.replace(' ', '|')
        sentence = self.lemmatized
        str_pattern = r'\w*?(' + lemma_phrase + ')'

        return self.__re_search_lemmed(phrase, sentence, str_pattern)

    def __re_search_lemmed(self, phrase, sentence, str_pattern):
        pattern = re.compile(str_pattern)
        matches = re.findall(pattern, sentence)
        self.lemmatized = re.sub(r'\b' + re.escape(phrase.lemma) + r'\b', '', sentence)
        logger.debug(f'Лемма: {self.lemmatized}')
        return as_class(dict(phrase=phrase.text,
                             sentence_id=self.sentence_id,
                             sentence=self.text,
                             count=len(matches)))

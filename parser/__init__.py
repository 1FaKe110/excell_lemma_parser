import re
import string
from typing import Dict, List
from loguru import logger

from langdetect import detect, DetectorFactory
from munch import DefaultMunch

as_class = DefaultMunch.fromDict
DetectorFactory.seed = 0

from parser.nlps import Nlps


class Sentence:

    def __init__(self, text):
        self.lang = detect(text)

        self.text: str = text
        self.clear_sentence = text.translate(
            str.maketrans('', '', string.punctuation)).lower()  # Удаление знаков препинания
        self.__nlp = Nlps().__getattribute__(self.lang)

        self.lemmatized = self.lemmatize(text)

    def lemmatize(self, text) -> str:
        return " ".join([token.lemma_ for token in self.__nlp(text)])

    def match_exact(self, phrase: str) -> DefaultMunch:
        count = 0
        words = self.clear_sentence.split()  # Разбиваем предложение на отдельные слова
        phrase_length = len(phrase.split())  # Получаем длину словосочетания

        # Проходим по всем словам в предложении
        for i in range(len(words) - phrase_length + 1):
            part = ' '.join(words[i:i + phrase_length])
            if part == phrase.lower():
                count += 1

        # Вернем словарь, где будет ключом будет словосочетание, а значением кол-во
        return as_class(dict(phrase=phrase, count=count))

    def match_exactlemmed(self, phrase: str) -> DefaultMunch:
        count = 0
        words = self.lemmatized.split()
        lemma_phrase = self.lemmatize(phrase).lower()
        phrase_length = len(lemma_phrase.split())

        for i in range(len(words) - phrase_length + 1):
            if ' '.join(words[i:i + phrase_length]) == lemma_phrase:
                count += 1

        return as_class(
            dict(phrase=phrase,
                 count=count)
        )

    def match_participant(self, phrase: str) -> DefaultMunch:
        lemma_phrase = self.lemmatize(phrase).lower()
        str_pattern = r'\b' + r'\b.*?\b'.join(map(re.escape, lemma_phrase.split())) + r'\b'
        pattern = re.compile(str_pattern)
        logger.debug(f'Result: {re.findall(pattern, self.lemmatized)}')
        return as_class(
            dict(phrase=phrase,
                 count=len(re.findall(pattern, self.lemmatized)))
        )

    def match_imprecise(self, phrase: str) -> DefaultMunch:
        lemma_phrase = self.lemmatize(phrase).lower().replace(' ', '|')
        str_pattern = r'\w*?(' + lemma_phrase + ')'
        pattern = re.compile(str_pattern)
        return as_class(
            dict(phrase=phrase,
                 count=len(re.findall(pattern, self.lemmatized)))
        )

def main():
    # sentence = Sentence("This is the sentence with given sentence word phrases,"
    #                     " so it sentence can be found word phrase")
    sentence = Sentence("This is the sentence with given sentence phrases")
    phrase = "sentence word phrase"

    print(f'Первоначальный текст:   {sentence.text}')
    print(f'Лемма теста:            {sentence.lemmatized}')

    print(f'Первоначальный запрос:  {phrase}')

    print(f"Супер точное вхождение: {sentence.match_exact(phrase).count}")
    print(f"Точное вхождение:       {sentence.match_exactlemmed(phrase).count}")
    print(f"Разбитое вхождение:     {sentence.match_participant(phrase).count}")
    print(f"Частичное вхождение:    {sentence.match_imprecise(phrase).count}")


if __name__ == '__main__':
    main()

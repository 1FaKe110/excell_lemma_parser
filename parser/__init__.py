import re
import string
from typing import Dict, List
from loguru import logger

from langdetect import detect, DetectorFactory
from munch import DefaultMunch

as_class = DefaultMunch.fromDict
DetectorFactory.seed = 0

from parser.nlps import Nlps


class Text:

    def __init__(self, text: str):
        self.text = text
        self.sentences = [Sentence(x) for x in re.split(r'(?<=[.!?])\s+', text)]


class Sentence:

    def __init__(self, text):
        self.lang = detect(text)

        self.text: str = text
        self.__nlp = Nlps().__getattribute__(self.lang)
        self.lemmatized = None

    def clear_full_sentence(self):
        return self.text.translate(str.maketrans('', '', string.punctuation)).lower()

    def lemmatize(self, text) -> str:
        return " ".join([token.lemma_ for token in self.__nlp(text)]).lower()

    def match_exact(self, phrase: str) -> DefaultMunch:
        phrase = phrase.lower()
        logger.debug(f"Phrase: {phrase}")

        sentence = self.clear_full_sentence()
        matches = re.findall(phrase, sentence)

        modified_sentence = re.sub(r'\b' + re.escape(phrase) + r'\b', '', sentence)
        self.lemmatized = self.lemmatize(modified_sentence)
        logger.debug(f'Исходный: {sentence}')
        logger.debug(f'Лемма: {self.lemmatized}')

        # Вернем словарь, где будет ключом будет словосочетание, а значением кол-во
        return as_class(dict(phrase=phrase, count=len(matches)))

    def match_exactlemmed(self, phrase: str) -> DefaultMunch:
        lemma_phrase = self.lemmatize(phrase)
        sentence = self.lemmatized

        logger.debug(f"Phrase: {lemma_phrase}")

        matches = re.findall(r'\b' + re.escape(lemma_phrase) + r'\b', sentence)
        self.lemmatized = re.sub(r'\b' + re.escape(phrase.lower()) + r'\b', '', sentence)
        logger.debug(f'Лемма: {self.lemmatized}')
        # Вернем словарь, где будет ключом будет словосочетание, а значением кол-во
        return as_class(dict(phrase=phrase, count=len(matches)))

    def match_participant(self, phrase: str) -> DefaultMunch:
        lemma_phrase = self.lemmatize(phrase)
        sentence = self.lemmatized
        logger.debug(f"Phrase: {lemma_phrase}")
        str_pattern = r'\b' + r'\b.*?\b'.join(map(re.escape, lemma_phrase.split())) + r'\b'

        return self.re_search_lemmed(lemma_phrase, phrase, sentence, str_pattern)

    def match_imprecise(self, phrase: str) -> DefaultMunch:
        lemma_phrase = self.lemmatize(phrase).replace(' ', '|')
        sentence = self.lemmatized

        logger.debug(f"Phrase: {lemma_phrase}")
        str_pattern = r'\w*?(' + lemma_phrase + ')'

        return self.re_search_lemmed(lemma_phrase, phrase, sentence, str_pattern)

    def re_search_lemmed(self, lemma_phrase, phrase, sentence, str_pattern):
        pattern = re.compile(str_pattern)
        matches = re.findall(pattern, sentence)
        self.lemmatized = re.sub(r'\b' + re.escape(lemma_phrase) + r'\b', '', sentence)
        logger.debug(f'Лемма: {self.lemmatized}')
        return as_class(dict(phrase=phrase, count=len(matches)))


def main():
    text = Text("""Bitcoin is the world’s first successful decentralized cryptocurrency and payment system, launched in 2009 by a mysterious creator known only as Satoshi Nakamoto. The word “cryptocurrency” refers to a group of digital assets where transactions are secured and verified using cryptography – a scientific practice of encoding and decoding data. Those transactions are often stored on computers distributed all over the world via a distributed ledger technology called blockchain (see below.)
Bitcoin can be divided into smaller units known as “satoshis” (up to 8 decimal places) and used for payments, but it’s also considered a store of value like gold. This is because the price of a single bitcoin has increased considerably since its inception – from less than a cent to tens of thousands of dollars. When discussed as a market asset, bitcoin is represented by the ticker symbol BTC.
The term “decentralized” is used often when discussing cryptocurrency, and simply means something that is widely distributed and has no single, centralized location or controlling authority. In the case of bitcoin, and indeed many other cryptocurrencies, the technology and infrastructure that govern the creation, supply, and security of it do not rely on centralized entities, like banks and governments, to manage it.
Ethereum network
colorful pins on board
Instead, Bitcoin is designed in such a way that users can exchange value with one another directly through a peer-to-peer network; a type of network where all users have equal power and are connected directly to each other without a central server or intermediary company acting in the middle. This allows data to be shared and stored, or bitcoin payments to be sent and received seamlessly between parties.
The Bitcoin network (capital “B”, when referring to the network and technology, lower-case “b” when referring to the actual currency, bitcoin) is completely public, meaning anyone in the world with an internet connection and a device that can connect to it can participate without restriction. It’s also open-source, meaning anyone can view or share the source code Bitcoin was built upon.
Perhaps the easiest way to understand bitcoin is to think of it like the internet for money. The internet is purely digital, no single person owns or controls it, it’s borderless (meaning anyone with electricity and a device can connect to it), it runs 24/7, and people who use it can easily share data between one another. Now imagine if there was an ‘internet currency’ where everyone who used the internet could help to secure it, issue it and pay each other directly with it without having to involve a bank. That’s what bitcoin essentially is.""")

    for sentence in text.sentences:
        phrase = "decentralized cryptocurrency"

        logger.info(f'Первоначальный текст:   {sentence.text}')

        logger.info(f"Супер точное вхождение: {sentence.match_exact(phrase).count}")
        logger.info(f"Точное вхождение:       {sentence.match_exactlemmed(phrase).count}")
        logger.info(f"Разбитое вхождение:     {sentence.match_participant(phrase).count}")
        logger.info(f"Частичное вхождение:    {sentence.match_imprecise(phrase).count}")
        logger.info('-' * 50)


if __name__ == '__main__':
    main()

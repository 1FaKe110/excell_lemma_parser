"""
1. Английский ("en") - модель "en_core_web_sm"
2. Немецкий ("de") - модель "de_core_news_sm"
3. Французский ("fr") - модель "fr_core_news_sm"
4. Испанский ("es") - модель "es_core_news_sm"
5. Итальянский ("it") - модель "it_core_news_sm"
6. Португальский ("pt") - модель "pt_core_news_sm"
7. Русский ("ru") - модель "ru_core_news_sm"
python -m spacy download en_core_web_sm
"""
import os
import spacy


class Nlps:
    # os.system("python -m spacy download ru_core_news_sm")
    ru = spacy.load("ru_core_news_sm")

    # os.system("python -m spacy download en_core_web_sm")
    en = spacy.load("en_core_web_sm")


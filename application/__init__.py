import pandas as pd
import json
from application.parser import Text, Phrase
from loguru import logger


class Application:

    def __init__(self, xlsx_filepath: str):
        self.xlsx = pd.ExcelFile(xlsx_filepath)
        self.texts = [Text(raw) for raw in pd.read_excel(self.xlsx, 'Текст', header=None)[0]]
        self.keys = [Phrase(raw) for raw in pd.read_excel(self.xlsx, 'Ключи', header=None)[0]]

    def run(self):
        results = {}
        for text_id, text in enumerate(self.texts, start=1):
            results[text_id] = {}
            for phrase in self.keys:
                for sentence in text.sentences:
                    matches = sentence.get_matches(phrase)
                    for row in matches:
                        if row.count <= 0:
                            continue
                    phrase.matches += matches
                results[text_id][phrase.text] = phrase.values()
        logger.info(json.dumps(results, indent=2, ensure_ascii=False))
        result_df = pd.DataFrame().from_dict(results)
        pass

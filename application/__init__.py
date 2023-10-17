import pandas as pd
import json
from application.parser import Text, Phrase
from loguru import logger


class Application:

    def __init__(self, xlsx_filepath: str, save_path: str):
        self.save_path = save_path
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
                        if matches.__dict__[row]['count'] <= 0:
                            continue

                        phrase.__dict__[row].append(
                            matches.__dict__[row]['id_']
                        )

                results[text_id][phrase.text] = phrase.values()

        for text_id, values in results.items():
            logger.info(json.dumps(values, indent=2, ensure_ascii=False))
            with pd.ExcelWriter(f'{self.save_path}/{text_id}.xlsx') as writer:
                keys_df = pd.DataFrame().from_dict(values).T
                keys_df.to_excel(writer, sheet_name='Ключи', index=True)

                sentences = dict(
                    id=[i + 1 for i in range(len(self.texts[text_id - 1].sentences))],
                    text=[t.text for t in self.texts[text_id - 1].sentences]
                )
                sentences_df = pd.DataFrame().from_dict(sentences)
                sentences_df.to_excel(writer, sheet_name='Пассажи', index=False)


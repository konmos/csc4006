import string

from flair.data import Sentence
from flair.models import SequenceTagger


TAGGER = SequenceTagger.load('ner-large')


def clean_text(text: str) -> str:
    text = text.translate(
        str.maketrans({
            '”': '"', '“': '"',
            '’': '\'',
            '…': '...'
        })
    )

    return [x.strip() for x in text.split('.')]  # extract sentences


def extract_entities(text):
    sentences, entities = clean_text(text), []

    for s in sentences:
        sent = Sentence(s)
        TAGGER.predict(sent)

        for entity in sent.to_dict(tag_type='ner')['entities']:
            entities.append(entity['text'])

    return set([
        x.translate(str.maketrans('', '', string.punctuation)) for x in entities
    ])


if __name__ == '__main__':
    with open('byzantine.txt') as fd:
        print(extract_entities(fd.read()))

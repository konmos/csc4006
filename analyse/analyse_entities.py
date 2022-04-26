# This file is a part of the final year project "Story and Software" (CSC4006).
# Author: Konrad Mosoczy (Queen's University Belfast - QUB)
# https://github.com/konmos/csc4006 (also available on GitLab)
# ------------------------------------------------------------------------------
# Perform NER on a piece of text using `extract_entities`.

import string

from flair.data import Sentence
from flair.models import SequenceTagger


# Load the dataset.
# 'ner-large' gives best results.
TAGGER = SequenceTagger.load('ner-large')


def clean_text(text: str) -> str:
    """
    Remove any symbols which may brake the NER step.
    """
    # Replace any bad characters with suitable alternatives.
    text = text.translate(
        str.maketrans({
            '”': '"', '“': '"',
            '’': '\'',
            '…': '...'
        })
    )

    return [x.strip() for x in text.split('.')]  # extract sentences


def extract_entities(text):
    """
    Extract any named entities from the given text.
    Returns the set of extracted entities (could be empty).
    """
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

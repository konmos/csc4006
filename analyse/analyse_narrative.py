from collections import defaultdict

import click, spacy
from narcy import document_factory
from narcy import doc_to_relations_df, doc_to_svos_df, doc_to_tokens_df


def perform_analysis(text: str, **kwargs) -> dict:
    # Load NLP object with language model.
    nlp = spacy.load('en_core_web_sm')

    # Create function for converting texts to documents
    make_doc = document_factory(nlp)

    # Create document for analysis
    doc = make_doc(text)

    return {
        'relations': None if 'relations' not in kwargs else doc_to_relations_df(doc),
        'relations_r': None if 'relations_r' not in kwargs else doc_to_relations_df(doc, reduced=True),
        'svos': None if 'svos' not in kwargs else doc_to_svos_df(doc),
        'tokens': None if 'tokens' not in kwargs else doc_to_tokens_df(doc)
    }


def extract_nouns(analysis: dict) -> list:
    nouns = []
    num_items = analysis['tokens'].shape[0]

    for i in range(num_items):
        token = analysis['tokens'].iloc[i]

        if token['pos'] in ('NOUN', 'PROPN'):  # Noun or proper noun
            nouns.append({
                'token': token['token'],
                'lead': token['lead'],
                'lemma': token['lemma'],
                'tense': token['tense']
            })

    return nouns


def simple_relationships(text, nouns):
    # A very naive and inaccurate method of establishing the relationships
    # between a collection of nouns in a piece of text. It works by simply
    # identifying which nouns appear together in a sentence.
    relationships = defaultdict(set)
    sentences = [x.strip() for x in text.split('.')]

    for n1 in nouns:
        for n2 in nouns:
            for sentence in sentences:
                if not sentence or n1['lemma'] == n2['lemma']:
                    continue

                if n1['token'] in sentence and n2['token'] in sentence:
                    relationships[n1['lemma']].add(n2['lemma'])

    return relationships


@click.command()
@click.option('-d', 'dump_data', default=False, help='dump data to csv', is_flag=True)
@click.option('-n', 'get_nouns', default=False, help='extract nouns', is_flag=True)
@click.option('-sr', 's_rel', default=False, help='extract simple relationships', is_flag=True)
@click.argument('fname')
def main(dump_data, fname, get_nouns, s_rel):
    with open(fname, 'r') as fd:
        text = fd.read()

    analysis = {}

    if dump_data:
        analysis = perform_analysis(
            text,
            tokens=True,
            relations=True,
            svos=True,
            relations_r=True
        )

        for x in analysis:
            analysis[x].to_csv(f'{x}.csv')


    if get_nouns:
        if analysis.get('tokens') is None:
            analysis = perform_analysis(
                text,
                tokens=True
            )

        nouns = extract_nouns(analysis)
        click.echo(nouns)

    if s_rel:
        if analysis.get('tokens') is None:
            analysis = perform_analysis(
                text,
                tokens=True
            )

        nouns = extract_nouns(analysis)
        rel = simple_relationships(text, nouns)
        click.echo(rel)


if __name__ == '__main__':
    main()

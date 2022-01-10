from collections import defaultdict

import click
import spacy
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

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
@click.option('-g', 'graph', default=False, help='draw a node graph', is_flag=True)
@click.argument('fname')
def main(dump_data, fname, get_nouns, s_rel, graph):
    with open(fname, 'r') as fd:
        text = fd.read()

    analysis = perform_analysis(
        text,
        tokens=any([dump_data, graph, get_nouns, s_rel]),
        relations=dump_data,
        svos=dump_data,
        relations_r=dump_data
    )

    if dump_data:
        for x in analysis:
            analysis[x].to_csv(f'{x}.csv')

    if any([graph, get_nouns, s_rel]):
        nouns = extract_nouns(analysis)
        rel = simple_relationships(text, nouns)

        if graph:
            G = nx.Graph()
            G.add_nodes_from({x['lemma'].replace(' ', '\n') for x in nouns})
            G.add_edges_from([(x.replace(' ', '\n'), y.replace(' ', '\n')) for x in rel for y in rel[x]])

            cmap = plt.get_cmap('Set3')
            colors = cmap(np.linspace(0, 1, len(rel)))

            nx.draw(
                G,
                with_labels=True,
                font_size=8,
                node_size=2000,
                font_weight="bold",
                width=0.75,
                edgecolors='gray',
                node_color=colors
            )

            # Scale axis to prevent nodes getting cut off
            axis = plt.gca()
            axis.set_xlim([1.1*x for x in axis.get_xlim()])
            axis.set_ylim([1.1*y for y in axis.get_ylim()])
            plt.savefig(f'{fname}.graph.png', format='PNG')

        if get_nouns:
            click.echo(nouns)

        if s_rel:
            click.echo(rel)


if __name__ == '__main__':
    main()

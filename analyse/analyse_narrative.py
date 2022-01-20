from collections import defaultdict

import yake
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
        'sentences': [str(s).lower() for s in doc.sents],
        'relations': None if 'relations' not in kwargs else doc_to_relations_df(doc),
        'relations_r': None if 'relations_r' not in kwargs else doc_to_relations_df(doc, reduced=True),
        'svos': None if 'svos' not in kwargs else doc_to_svos_df(doc),
        'tokens': None if 'tokens' not in kwargs else doc_to_tokens_df(doc)
    }


def extract_nouns(analysis: dict, nsubj=False) -> list:
    nouns = []
    num_items = analysis['tokens'].shape[0]

    for i in range(num_items):
        token = analysis['tokens'].iloc[i]

        if token['pos'] in ('NOUN', 'PROPN'):  # Noun or proper noun
            if not nsubj or nsubj and token['dep'] in ('nsubj', 'nsubjpass'):
                nouns.append({
                    'token': token['token'],
                    'lead': token['lead'],
                    'lemma': token['lemma'],
                    'tense': token['tense']
                })

    return nouns


def simple_relationships(text, nouns, sentences=None):
    # A very naive and inaccurate method of establishing the relationships
    # between a collection of nouns in a piece of text. It works by simply
    # identifying which nouns appear together in a sentence.
    relationships = defaultdict(set)

    if sentences is None:
        sentences = [x.strip() for x in text.split('.')]

    for n1 in nouns:
        for n2 in nouns:
            for sentence in sentences:
                if not sentence or n1['lemma'] == n2['lemma']:
                    continue

                if n1['token'] in sentence and n2['token'] in sentence:
                    relationships[n1['lemma']].add(n2['lemma'])

    return relationships


@click.group(invoke_without_command=True)
@click.argument('fname')
@click.pass_context
def cli(ctx, fname):
    with open(fname, 'r') as fd:
        text = fd.read()

    ctx.ensure_object(dict)
    ctx.obj['fname'] = fname
    ctx.obj['text'] = text


@cli.command()
@click.option('-nsubj', default=False, help='filter nouns to contain only nominal subjects', is_flag=True)
@click.option('-kw', default=-1, help='filter nouns to only the X most common keywords')
@click.option('-avg', default=False, help='filter nouns to only those with an above average occurrence', is_flag=True)
@click.pass_context
def draw_graph(ctx, nsubj, kw, avg):
    '''
    Draw a graph by extracting entities from a piece of text
    '''
    analysis = perform_analysis(
        ctx.obj['text'],
        tokens=True
    )

    nouns = extract_nouns(analysis, nsubj=nsubj)

    if avg:
        noun_counts = defaultdict(int)

        for n in nouns:
            noun_counts[n['lemma']] += 1

        average_occurrence = len(nouns) / len(noun_counts)
        nouns = [n for n in nouns if noun_counts[n['lemma']] >= average_occurrence]

    if kw != -1:
        kw_extractor = yake.KeywordExtractor(lan='en', n=3, dedupLim=0.9, top=kw, features=None)
        kw = {k[0].lower() for k in kw_extractor.extract_keywords(ctx.obj['text'])}
        nouns = [n for n in nouns if n['token'] in kw or n['lemma'] in kw]

    _nouns = {x['lemma'].replace(' ', '\n') for x in nouns}
    rel = simple_relationships(ctx.obj['text'], nouns, analysis['sentences'])

    G = nx.Graph()
    G.add_nodes_from(_nouns)
    G.add_edges_from([(x.replace(' ', '\n'), y.replace(' ', '\n')) for x in rel for y in rel[x]])

    cmap = plt.get_cmap('Set3')
    colors = cmap(np.linspace(0, 1, len(_nouns)))

    pos = nx.nx_pydot.graphviz_layout(G)

    nx.draw(
        G,
        pos,
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
    plt.savefig(f'{ctx.obj["fname"]}.graph.png', format='PNG')


@cli.command()
@click.pass_context
def dump_data(ctx):
    analysis = perform_analysis(
        ctx.obj['text'],
        tokens=True,
        relations=True,
        svos=True,
        relations_r=True
    )

    for x in analysis:
        analysis[x].to_csv(f'{x}.csv')


if __name__ == '__main__':
    cli(obj={})

# This file is a part of the final year project "Story and Software" (CSC4006).
# Author: Konrad Mosoczy (Queen's University Belfast - QUB)
# https://github.com/konmos/csc4006 (also available on GitLab)
# ------------------------------------------------------------------------------
# Perform comprehensive narrative analysis on a piece of text.

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
    """
    Use Narcy to perform narrative analysis on a piece of text.

    Specify which outputs you want using *kwargs.
    For example, if we are interested in tokens only, we can do:
        perform_analysis(text, tokens=True)

    Acceptable options are (these get returned as pandas frames):
        tokens, relations, relations_r, svos

    Sentences are always returned.
    See https://github.com/sztal/narcy for more details.
    """
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
    """
    Extract all nouns from a piece of text.
    This uses the tokens from the analysis step.

    Optionally, we can also filter the output to contain only nominal subjects.
    We do this by setting the `nsubj` parameter to True.
    """
    nouns = []
    num_items = analysis['tokens'].shape[0]

    for i in range(num_items):
        token = analysis['tokens'].iloc[i]

        if token['pos'] in ('NOUN', 'PROPN'):  # Noun or proper noun
            # Nominal subject filtering.
            if not nsubj or nsubj and token['dep'] in ('nsubj', 'nsubjpass'):
                nouns.append({
                    'token': token['token'],
                    'lead': token['lead'],
                    'lemma': token['lemma'],
                    'tense': token['tense']
                })

    return nouns


def simple_relationships(text, nouns, sentences=None):
    """
    A very naive and inaccurate method of establishing the relationships
    between a collection of nouns in a piece of text. It works by simply
    identifying which nouns appear together in a sentence.

    We can override the sentences by passing the `sentences` parameter.
    Otherwise, they get automatically extracted by splitting at full stops ('.').

    Returns a dict of the form {A: set(B, C, D)} where A has a relationship with B, C, D.
    """
    relationships = defaultdict(set)

    if sentences is None:
        sentences = [x.strip() for x in text.split('.')]

    for n1 in nouns:
        for n2 in nouns:
            for sentence in sentences:
                if not sentence or n1['lemma'] == n2['lemma']:
                    continue

                # If the two tokens occur in the sentence, there is a relationship.
                if n1['token'] in sentence and n2['token'] in sentence:
                    # We add the lemma form of the token.
                    # See the spacy/narcy docs for the differences.
                    relationships[n1['lemma']].add(n2['lemma'])

    return relationships


@click.group(invoke_without_command=True)
@click.argument('fname')
@click.pass_context
def cli(ctx, fname):
    """
    CLI entry point.
    fname is the filename of the text we want to analyse.
    """
    with open(fname, 'r') as fd:
        text = fd.read()

    ctx.ensure_object(dict)
    ctx.obj['fname'] = fname
    ctx.obj['text'] = text


@cli.command()
@click.option('-nsubj', default=False, help='filter nouns to contain only nominal subjects', is_flag=True)
@click.option('-kw', default=-1, help='filter nouns to only the X most common keywords')
@click.option('-avg', default=False, help='filter nouns to only those with an above average occurrence', is_flag=True)
@click.option('-layout', help='node positioning algorithm',
              type=click.Choice(['circular', 'kawai','random', 'shell', 'spring', 'spectral', 'spiral', 'graphviz']))
@click.option('-scale', default=1.1, help='axis scaling factor to prevent nodes being cut off')
@click.pass_context
def draw_graph(ctx, nsubj, kw, avg, layout=None, scale=1.1):
    '''
    Draw a graph by extracting entities from a piece of text.
    '''
    # Analysis step.
    analysis = perform_analysis(
        ctx.obj['text'],
        tokens=True
    )

    # Extract nouns.
    nouns = extract_nouns(analysis, nsubj=nsubj)

    if avg:
        # Filter out nouns with a less than average occurence.
        noun_counts = defaultdict(int)

        for n in nouns:
            noun_counts[n['lemma']] += 1

        average_occurrence = len(nouns) / len(noun_counts)
        nouns = [n for n in nouns if noun_counts[n['lemma']] >= average_occurrence]

    if kw != -1:
        # Filter out non-keyword nouns.
        # See https://github.com/LIAAD/yake
        kw_extractor = yake.KeywordExtractor(lan='en', n=3, dedupLim=0.9, top=kw, features=None)
        kw = {k[0].lower() for k in kw_extractor.extract_keywords(ctx.obj['text'])}
        nouns = [n for n in nouns if n['token'] in kw or n['lemma'] in kw]

    # Break text at spaces; this results in cleaner output.
    _nouns = {x['lemma'].replace(' ', '\n') for x in nouns}
    rel = simple_relationships(ctx.obj['text'], nouns, analysis['sentences'])

    # Set up the graph.
    G = nx.Graph()
    G.add_nodes_from(_nouns)
    G.add_edges_from([(x.replace(' ', '\n'), y.replace(' ', '\n')) for x in rel for y in rel[x]])

    # Uniformly spread out the colors of each node.
    cmap = plt.get_cmap('Set3')
    colors = cmap(np.linspace(0, 1, len(_nouns)))

    # Differnet possible graph layout algorithms.
    # Generally, the kamada kawai algorithm works best.
    graph_layout = {
        'circular': nx.circular_layout,
        'kawai': nx.kamada_kawai_layout,
        'random': nx.random_layout,
        'shell': nx.shell_layout,
        'spring': nx.spring_layout,
        'spectral': nx.spectral_layout,
        'spiral': nx.spiral_layout
    }

    pos = graph_layout.get(layout, nx.nx_pydot.graphviz_layout)(G)

    # Draw the graph.
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
    axis.set_xlim([scale*x for x in axis.get_xlim()])
    axis.set_ylim([scale*y for y in axis.get_ylim()])
    plt.savefig(f'{ctx.obj["fname"]}.graph.png', format='PNG')


@cli.command()
@click.pass_context
def dump_data(ctx):
    '''
    Dump analysis data to CSV files.
    '''
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

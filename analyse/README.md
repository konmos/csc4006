## NER

After being inspired by [this study](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0226025), the idea was to programmatically analyse a story (which is to act as a software specification) and extract the named entities (see [this](https://github.com/flairNLP/flair) and [this](https://home.aveek.io/blog/post/finding-main-characters/)). The idea was that once these were extracted, a model could be developed representing the relationships between each of these entities, with the hope of the end result being something similar to an ER diagram. Think of it as a pre-ER step. Perhaps it could be useful for comparing with the actual ER diagram which gets drawn up during the development stage. This could be taken even further by analyzing text to try and extract any "actions" that each entity performs....

... Unfortunately, the results of the first test (analyse.py) were disappointing in that the NER was not as accurate as expected. For example, it would have been ideal to get something along the lines of

`
extract_entities(fd.read()) -> {General, Messenger}
`

where, instead, an empty set gets returned. It's possible that the code is inadequate or the required technology for NLP is simply not here yet.


## Narrative Analysis

Following from the above, a more comprehensive approach was employed where, instead of simply relying on NER, narrative analysis was employed with the help of [Narcy](https://github.com/sztal/narcy#readme). The results of this are far more promising.

### Script Usage

```
$ python analyse_narrative --help

Usage: analyse_narrative.py [OPTIONS] FNAME

Options:
  -d      dump data to csv
  -n      extract nouns
  -sr     extract simple relationships
  --help  Show this message and exit.
```

### Example Results

```
$ python analyse_narrative -n -sr byzantine.txt

[{'token': 'divisions', 'lead': 'divisions', 'lemma': 'division', 'tense': 'PAST'}, {'token': 'army', 'lead': 'army', 'lemma': 'army', 'tense': 'PAST'}, {'token': 'enemy city', 'lead': 'enemy city', 'lemma': 'enemy city', 'tense': 'PAST'}, {'token': 'division', 'lead': 'division', 'lemma': 'division', 'tense': 'PAST'}, {'token': 'general', 'lead': 'general', 'lemma': 'general', 'tense': 'PAST'}, {'token': 'generals', 'lead': 'generals', 'lemma': 'general', 'tense': 'PRESENT'}, {'token': 'messenger', 'lead': 'messenger', 'lemma': 'messenger', 'tense': 'PRESENT'}, {'token': 'enemy', 'lead': 'enemy', 'lemma': 'enemy', 'tense': 'PRESENT'}, {'token': 'plan', 'lead': 'plan', 'lemma': 'plan', 'tense': 'PRESENT'}, {'token': 'action', 'lead': 'action', 'lemma': 'action', 'tense': 'PRESENT'}, {'token': 'generals', 'lead': 'generals', 'lemma': 'general', 'tense': 'PRESENT'}, {'token': 'traitors', 'lead': 'traitors', 'lemma': 'traitor', 'tense': 'PRESENT'}, {'token': 'generals', 'lead': 'generals', 'lemma': 'general', 'tense': 'FUTURE'}, {'token': 'agreement', 'lead': 'agreement', 'lemma': 'agreement', 'tense': 'PRESENT'}, {'token': 'generals', 'lead': 'generals', 'lemma': 'general', 'tense': 'PRESENT'}, {'token': 'plan', 'lead': 'plan', 'lemma': 'plan', 'tense': 'PRESENT'}, {'token': 'action', 'lead': 'action', 'lemma': 'action', 'tense': 'PRESENT'}, {'token': 'traitors', 'lead': 'traitors', 'lemma': 'traitor', 'tense': 'PRESENT'}, {'token': 'generals', 'lead': 'generals', 'lemma': 'general', 'tense': 'PRESENT'}, {'token': 'agreement', 'lead': 'agreement', 'lemma': 'agreement', 'tense': 'PRESENT'}, {'token': 'plan', 'lead': 'plan', 'lemma': 'plan', 'tense': 'PRESENT'}]

defaultdict(<class 'set'>, {'division': {'general', 'enemy city', 'army', 'enemy'}, 'army': {'enemy city', 'general', 'enemy', 'division'}, 'enemy city': {'general', 'army', 'enemy', 'division'}, 'general': {'enemy city', 'agreement', 'traitor', 'plan', 'action', 'enemy', 'division', 'messenger', 'army'}, 'messenger': {'general'}, 'enemy': {'enemy city', 'plan', 'general', 'action', 'division', 'army'}, 'plan': {'action', 'agreement', 'general', 'enemy'}, 'action': {'general', 'enemy', 'plan'}, 'traitor': {'agreement', 'general'}, 'agreement': {'traitor', 'general', 'plan'}})
```

### TODO

* Extract better relationships
* Extract verbs for each noun
* Represent the data as a diagram

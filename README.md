# Automatic Classification of Persuasive Arguments
Term project for ENGL 681 _Introduction to Natural Language Processing_ at RIT, 2017.

[@jdberlinski](https://github.com/jdberlinski)
[@glebpro](https://github.com/glebpro)

## Abstract:
Public web forums allow for massive online debate, especially on the community platform Reddit. The language of persuasive arguments can be found on the sub-community [/r/ChangeMyView](https://reddit.com/ChangeMyView), which encourages sharing views and discourse in a moderated public forum. To determine if there are any similarities between persuasive comments that were successful in changing a user's view we organized and labeled sets of argument examples, and found valuable features for classifying novel arguments through language modeling. Our model results saw 6% improved accuracy over the baseline, concluding that there are identifiable stylistic and topic features in effective arguments.

[[Slides](slides.pdf)][[Paper](paper.pdf)]

## Technicals

#### Downloads
To download code: `$ git clone https://github.com/glebpro/nlptermproject2017`

To download corpus: [download link](https://drive.google.com/drive/folders/1Ki65wjOoVgLENWK1xgRMPaxdBrx5v8n9?usp=sharing). Data format explained [here](/corpus_utils/data_format.txt).

#### Scripts

To generate your own corpus, gathering posts backwards in time from now:
1. Populate [`corpus_utils/reddit.auth.json`](corpus_utils/reddit.auth.json) with your reddit credentials
2. Run `$ python corpus_utils/download.py num_posts_to_collect`

To generate comment pairs, use:
1. `$ python corpus_utils/comment_pairs.py CMV_##.jsonlist`

For the classifier:
1. To extract features: `$ python model_files/get_features.py comment_pairs.jsonlist`
2. To train new model: `$ python model_files/model.py`
  - steps 1 and 2 might take hours
3. To explore results: `$ python model_files/explore.py`
  - to print results from included model

Additional utility scrips included for parsing [posts](corpus_utils/parse_jsonlist.py) and [comments](corpus_utils/parse_comments.py)

#### Requirements
[python](https://www.python.org/) >= 3.4, [praw](https://praw.readthedocs.io/en/latest/index.html) >= 5.2, [spacy](https://spacy.io/) >= 2.0.3, [sklearn](http://scikit-learn.org/stable/) >= 0.18.1, [numpy](http://www.numpy.org/) >= 1.13.3, [nltk](http://www.nltk.org/) >= 3.2.5

#### License
MIT licensed. See the bundled [LICENSE](/LICENSE) file for more details.

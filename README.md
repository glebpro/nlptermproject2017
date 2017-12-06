# Automatic Classification of Persuasive Arguments
Term project for ENGL 681 _Introduction to Natural Language Processing_ at RIT, 2017.

[@josuhaberlinski](https://github.com/user/jdberlinski)
[@glebpro](https://github.com/user/glebpro)

## Abstract:
Public web forums allow for massive online debate, especially on the community platform Reddit. The language of persuasive arguments can be found on the sub-community [/r/ChangeMyView](https://reddit.com/ChangeMyView), which encourages sharing views and discourse in a moderated public forum. To determine if there are any similarities between persuasive comments that were successful in changing a user's view we organized and labeled sets of argument examples, and found valuable features for classifying novel arguments through language modeling. Our model results saw 32% improved accuracy over the baseline, concluding that there are identifiable stylistic and topic features in effective arguments.

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
1. To train new model: `python CLASSIFIER.py -train CMV_##.jsonlist`
1. To evaluate: `python CLASSIFIER.py -evaluate CMV_##.jsonlist`
1. To make prediction: `python CLASSIFIER.py -predict "Text to predict"`

#### Requirements
[python](https://www.python.org/) >= 3.4, [praw](https://praw.readthedocs.io/en/latest/index.html) >= 5.2, [spacy](https://spacy.io/) >= 2.0.3 

#### License
MIT licensed. See the bundled [LICENSE](/LICENSE) file for more details.

<hr>
<b>1</b> <i>Citations go here</i>

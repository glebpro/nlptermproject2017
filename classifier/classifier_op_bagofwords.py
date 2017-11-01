import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LogisticRegressionCV
from sklearn.metrics.scorer import roc_auc_scorer
import numpy as np

def evaluate(model, test_data):
    vect = TfidfVectorizer(use_idf=False, norm='l1')
    X_test = vect.transform([post["selftext"] for post in test_data])
    test_deltas = np.array([post["delta_label"] for post in test_data])
    test_roc = roc_auc_scorer(model, X_test, test_deltas)
    print("Test ROC AUC score: {:.3f}".format(test_roc))

def train(train_data):
    deltas = np.array([post["delta_label"] for post in train_data])
    vect = TfidfVectorizer(use_idf=False, norm='l1')
    X_train = vect.fit_transform([post["selftext"] for post in train_data])
    lr = LogisticRegressionCV(Cs=10, class_weight='balanced',
                          scoring='roc_auc', solver='sag',
                          tol=0.001, max_iter=500,
                          random_state=0)
    lr.fit(X_train, deltas)

    return lr

def cleanpost(text):
    lines = [line for line in text.splitlines()
             if not line.lstrip().startswith("&gt;")
             and not line.lstrip().startswith("____")
             and "edit" not in " ".join(line.lower().split()[:2])
            ]
    return "\n".join(lines)

def parse_json(fname):
    corpus = open(fname)
    output = [ json.loads(line) for line in corpus ]
    corpus.close()
    return output

def main():

    train_data = parse_json("data/train_op_data.jsonlist")
    test_data = parse_json("data/train_op_data.jsonlist")

    for post in train_data:
        post['selftext'] = cleanpost(post['selftext'])
    for post in test_data:
        post['selftext'] = cleanpost(post['selftext'])

    model = train(train_data)
    evaluate(model, test_data)

if __name__ == "__main__":
    main()

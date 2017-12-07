import numpy as np
from sklearn import linear_model
from sklearn.metrics import confusion_matrix
import pickle

def main():

    print("loading model and data...")
    lasso = pickle.load(open("model2.sav", "rb"))
    X_test = pickle.load(open("reduced_xtest2.sav", "rb"))
    y_test = pickle.load(open("ytest2.sav", "rb"))

    print("model info:")
    print(lasso)

    print("model score:")
    print(lasso.score(X_test, y_test))

    print("confusion matrix:")
    print(confusion_matrix(y_test, lasso.predict(X_test)))

    feat_list = ["CD","EX","FW","JJR","JJS","LS","MD","NNP","NNPS","PDT","POS","PRP", "PRP$","RBR","RBS","RP","TO","UH","VB","VBD","VBG","VBN","VBP",
    "VBZ","WDT",
    "WP",
    "WP$",
    "WRB",
    "positive",
    "italic",
    "bold",
    "block",
    "edu",
    "com",
    "pdf",
    "topic0",
    "topic1",
    "topic2",
    "topic3",
    "topic4",
    "topic5",
    "topic6",
    "topic7",
    "topic8"
    ]

    odds_ratios = []
    for i in range(len(feat_list)):
        if lasso.coef_[0][i] != 0:
            odds_ratios.append((feat_list[i], np.exp(lasso.coef_[0][i])))

    print("odds ratios:")
    print(odds_ratios)

if __name__ == "__main__":
    main()

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

if __name__ == "__main__":
    main()

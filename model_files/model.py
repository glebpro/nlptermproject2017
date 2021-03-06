from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn import linear_model
from sklearn.model_selection import StratifiedShuffleSplit
import numpy as np
import pickle, re, nltk, os

file_prefix = os.path.dirname(os.path.realpath(__file__))

def recode_topics(vec):
    out = [0 for i in range(0, len(vec))]
    out[np.argmax(vec)] = 1

    return out[:(len(out) - 1)]

def main():

    # load in the data from get_features.py
    X_full = pickle.load(open(file_prefix+"/undersampled_X2.sav", "rb"))
    y_full = pickle.load(open(file_prefix+"/undersampled_deltas2.sav", "rb"))
    c_full = pickle.load(open(file_prefix+"/undersampled_comments2.sav", "rb"))

    sss = StratifiedShuffleSplit(n_splits = 1, test_size = 0.2, random_state = 20171205)
    for train_i, test_i in sss.split(X_full, y_full):
        X_train, X_test = list(np.array(X_full)[train_i]), list(np.array(X_full)[test_i])
        y_train, y_test = list(np.array(y_full)[train_i]), list(np.array(y_full)[test_i])
        c_train, c_test = list(np.array(c_full)[train_i]), list(np.array(c_full)[test_i])

    # for further analysis of correlation in R, save X_train
    np.savetxt(file_prefix+"/correlation.csv", np.array(X_train), delimiter = ",")

    # remove the POS tags and correlated features
    out_features = [0, 2, 5, 6, 11, 12, 19, 37]

    X_test = [np.delete(np.array(vec), out_features).tolist() for vec in X_test]
    X_train = [np.delete(np.array(vec), out_features).tolist() for vec in X_train]

    # recode all of the comments for the topic model
    new_X_train = [re.sub("[_>\*∆]", "", comment) for comment in c_train]
    new_X_train = [re.sub("(\n)+", " ", comment) for comment in new_X_train]
    new_X_train = [re.sub(" +", " ", comment) for comment in new_X_train]
    new_X_train = [re.sub("(www|https?|org)", "", comment) for comment in new_X_train]

    new_X_test = [re.sub("[_>\*∆]", "", comment) for comment in c_test]
    new_X_test = [re.sub("(\n)+", " ", comment) for comment in new_X_test]
    new_X_test = [re.sub(" +", " ", comment) for comment in new_X_test]
    new_X_test = [re.sub("(www|https?|org)", "", comment) for comment in new_X_test]

    tf_vectorizer = CountVectorizer(max_df = 0.95, min_df = 2, max_features = 1000, stop_words = 'english')
    tf = tf_vectorizer.fit_transform(new_X_train)
    tf_feature_names = tf_vectorizer.get_feature_names()

    lda = LatentDirichletAllocation(n_topics = 10, learning_method = "online")
    lda.fit(tf)

    train_topics = lda.transform(tf)
    train_topics = [recode_topics(vec) for vec in train_topics]
    for i in range(0, len(X_train)):
        X_train[i].extend(train_topics[i])

    test_topics = lda.transform(tf_vectorizer.transform(new_X_test))
    test_topics = [recode_topics(vec) for vec in test_topics]
    for i in range(0, len(X_test)):
        X_test[i].extend(test_topics[i])

    pickle.dump(X_train, open(file_prefix+"/reduced_xtrain2.sav", "wb"))
    pickle.dump(X_test, open(file_prefix+"/reduced_xtest2.sav", "wb"))

    pickle.dump(y_train, open(file_prefix+"/ytrain2.sav", "wb"))
    pickle.dump(y_test, open(file_prefix+"/ytest2.sav", "wb"))

    # cost chosen via 60/20 train/test split then rerun on full train data
    lasso = linear_model.LogisticRegression(penalty = "l1", C = 5)
    lasso.fit(X_train, y_train)

    # save all models
    pickle.dump(lasso, open(file_prefix+"/model2.sav", "wb"))
    pickle.dump(lda, open(file_prefix+"/lda2.sav", "wb"))
    pickle.dump(tf_vectorizer, open(file_prefix+"/tf2.sav", "wb"))

if __name__ == "__main__":
    main()

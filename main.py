'''
This program is a ML classifier used to identify the features with greatest influence on currents off
Red Hill / Puu Olai, Maui
'''
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score
import pandas as pd
import numpy as np

def main():
    # data = load_breast_cancer()
    # label_names = data['target_names']
    # labels = data['target']
    # feature_names = data['feature_names']
    # features = data['data']
    # print('label_names:', label_names)
    # print('Class label = ', labels[0])
    # print('feature_names:', feature_names)
    # print('features[0]:', features[0])
    # train, test, train_labels, test_labels = train_test_split(features, labels, test_size=0.33, random_state=42)
    # print('train', train)
    # print('train labels', train_labels)
    # gnb = GaussianNB()
    # model = gnb.fit(train, train_labels)
    # preds = gnb.predict(test)
    # print('pred:', preds)
    # print('accuracy_score', accuracy_score(test_labels, preds))


    # data cleaning
    df = pd.read_csv('data-features.csv')
    # remove the end label and drop columns that aren't features
    labels = df["desired"]
    to_drop = ['date', 'time', 'desired']
    df.drop(to_drop, inplace=True, axis=1)
    print(df)
    print(labels)
    # convert string columns to numeric categories
    df["strength"] = df["strength"].astype(float)
    print(df)

    # train
    train, test, train_labels, test_labels = train_test_split(df, labels, test_size=0.2, random_state=42)
    print('train', train)
    print('train labels', train_labels)
    gnb = GaussianNB()
    model = gnb.fit(train, train_labels)
    preds = gnb.predict(test)
    print('pred:', preds)
    print('accuracy_score', accuracy_score(test_labels, preds))


if __name__ == '__main__':
    main()

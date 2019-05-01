
# coding: utf-8

# In[1]:

import numpy as np
import csv
import random
import pickle

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from catboost import CatBoostClassifier


# In[2]:

f = open('./vectorized_large.csv')
data_0 = list()
data_1 = list()


# In[3]:

csvreader = csv.reader(f)
for row in csvreader:
    row = [float(r) for r in row]
    if row[0] == 0:
        data_0.append(row)
    else:
        data_1.append(row)
f.close()


# In[4]:

assert(len(data_0) == len(data_1))
print(len(data_0))


# In[5]:

training_set = np.array(data_0[:5000] + data_1[:5000])
dev_set = np.array(data_0[5000:] + data_1[5000:])

training_labels = training_set[:, 0].astype(int)
training_data = training_set[:, 1:].astype('float32')
dev_labels = dev_set[:, 0].astype(int)
dev_data = dev_set[:, 1:].astype('float32')


# In[6]:

# normalize features
_mean = np.mean(training_data, axis=0)
_std = np.std(training_data, axis=0)
training_data = (training_data - _mean) / _std
dev_data = (dev_data - _mean) / _std
print(_mean.tolist())
print(_std.tolist())
print(np.amin(training_data, axis=0).tolist())
print(np.amax(dev_data, axis=0).tolist())


# In[8]:

clf = LogisticRegression()
clf.fit(training_data, training_labels)
clf.score(dev_data, dev_labels)


# In[9]:

clf = AdaBoostClassifier()
clf.fit(training_data, training_labels)
clf.score(dev_data, dev_labels)


# In[10]:

clf = CatBoostClassifier(iterations=10, learning_rate=1, depth=10)
clf.fit(training_data, training_labels, verbose=False)
clf.score(dev_data, dev_labels)


# In[11]:

clf = MLPClassifier()
clf.fit(training_data, training_labels)
clf.score(dev_data, dev_labels)


# In[12]:

clf = RandomForestClassifier()
clf.fit(training_data, training_labels)
clf.score(dev_data, dev_labels)


# In[13]:

outf = open("final_model.pickle", 'wb')
pickle.dump(clf, outf)
outf.close()


# In[ ]:




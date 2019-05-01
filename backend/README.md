# Gingko
BigCo Team 14 - SP 2019

Our dataset in SQL format: https://drive.google.com/file/d/1ebdN6rQYocJof_cKpVyLPCq2DR729ekh/view?usp=sharing

You can install Mysql and build the gingko database in the following parameters:

```
(host='127.0.0.1',port=3306,user='root',password='root',db='gingko')
```

in order to extract the crawled data

## Filter

We apply basic news and non-news filter and English filter on the input to ensure the validity.

## Feature Extractors

All the feature extractors can be found in `extractor_accelerated.py`.

## Text Extractor
* API:
  * `te = TextExtractor(url, local)`
  * `te.getText()`
* Parameters:
  `url`: string
  `local`: `True` by default. For online sites, use `False` instead.

```python
    # Online request example
    url = 'https://www.nytimes.com/2019/03/14/us/politics/mueller-report-public.html?action=click&module=Top%20Stories&pgtype=Homepage'
    te = TextExtractor(url, local=False)
    print(te.getText())
    
    # Local html file example
    dir = './html_samples/legit/DNA leads to man\'s arrest.htm'
    te = TextExtractor(dir)
    print(te.getText())
```

## Vectorization

We get vectorized training and testing dataset from `vectorize.py`

## Training

We tried several sklearn models in `training.py` and save our final model as pickle file for future use


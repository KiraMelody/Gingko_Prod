
# coding: utf-8

# In[ ]:

import pymysql
import pymysql.cursors
from extractor_accelerated import *
import random


# In[ ]:

conn = pymysql.connect(host='127.0.0.1',port=3306,user='root',password='root',db='gingko')
cursor = conn.cursor()
cursor.execute('select count(*) from web_pages')


# In[ ]:

values = cursor.fetchall()
values


# In[ ]:

cursor.execute('select site, is_fake, html from web_pages')
webs = cursor.fetchall()
len(webs)


# In[ ]:

one_webs = []
zero_webs = []
for w in webs:
    if w[1] == 0:
        zero_webs.append(w)
    else:
        one_webs.append(w)

random.shuffle(zero_webs)
zero_webs = zero_webs[:len(one_webs)]
print(zero_webs)


# In[ ]:

for section in range(4):
    imgs = [[], []]
    ads = [[], []]
    _reading_level = [[], []]
    _social_media_score = [[], []]
    _citation_score = [[], []]
    _sentiment = [[], []]
    for i in range(1600):
        if i % 100 == 0:
            print(i)
        soup = BeautifulSoup(one_webs[section*1600 + i][2], 'html.parser')
        imgs[1].append(get_img_number(soup))
        ads[1].append(get_ads_number(soup))
        _reading_level[1].append(get_reading_level(one_webs[section*1600 + i][2]))
        _social_media_score[1].append(social_media_score(soup))
        _citation_score[1].append(citation_score(soup))
        _sentiment[1].append(sentiment_analysis(one_webs[section*1600 + i][2]))
    for i in range(1600):
        if i % 100 == 0:
            print(i)
        soup = BeautifulSoup(zero_webs[section*1600 + i][2], 'html.parser')
        imgs[0].append(get_img_number(soup))
        ads[0].append(get_ads_number(soup))
        _reading_level[0].append(get_reading_level(zero_webs[section*1600 + i][2]))
        _social_media_score[0].append(social_media_score(soup))
        _citation_score[0].append(citation_score(soup))
        _sentiment[0].append(sentiment_analysis(zero_webs[section*1600 + i][2]))
    
    outf = open("vectorized" + str(section) + ".csv", 'w')
    for i in range(len(imgs[0])):
        outf.write("0,"+str(imgs[0][i])+","+str(ads[0][i])+","+str(_reading_level[0][i])+",")
        outf.write(str(_social_media_score[0][i])+","+str(_citation_score[0][i])+","+str(_sentiment[0][i])+"\n")
    for i in range(len(imgs[1])):
        outf.write("1,"+str(imgs[1][i])+","+str(ads[1][i])+","+str(_reading_level[1][i])+",")
        outf.write(str(_social_media_score[1][i])+","+str(_citation_score[1][i])+","+str(_sentiment[1][i])+"\n")
    outf.close()


# In[ ]:




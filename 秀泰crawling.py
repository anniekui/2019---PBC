#!/usr/bin/env python
# coding: utf-8

# ## 引入模組

# In[ ]:


import requests, re, time, json, random
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup


# ## 秀泰影城

# In[ ]:


# 抓電影ID

# Other way to crawl
## import chardet
## import urllib
## rawdata = urllib.request.urlopen('https://capi.showtimes.com.tw/1/programs/listPopularForStore/1?nocache=0').read()
## chardet.detect(rawdata)

## 根據抓取下來的byte進行解碼形成可以觀看的字串
## rawdata=rawdata.decode('utf-8','ignore')

## ==============================================================

url = 'https://capi.showtimes.com.tw/1/programs/listPopularForStore/1?nocache=0'
headers = {'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
rawdata = requests.get(url, headers=headers).text


# In[ ]:


# 只留下需要的電影資訊
movie_name_js = json.loads(rawdata)
movie_name_js = movie_name_js["payload"]["programs"]  


# In[ ]:


# 找出電影名稱 以及 movie id
movie_name = []
movie_id = []
for i in range(len(movie_name_js)):
    movie_name.append(movie_name_js[i]["name"])  # 電影名稱
    movie_id.append(str(movie_name_js[i]["id"]))  # 電影id

data = zip(movie_id, movie_name)
movie_id_df = pd.DataFrame(data, columns = ["movie_id", "movie_name"])


# In[ ]:


# 抓取戲院以及電影時刻的相關資訊

movie_times_all = []
movie_date_all = []
movie_venue_all = []
movie_name_all = []
movie_version_all = []

prefix = "https://capi.showtimes.com.tw/1/events/listForProgram/"
for k in range(len(movie_id)):
    rawdata_i = json.loads(requests.get((prefix + movie_id[k]), headers=headers).text)
    
    # 抓取戲院資訊
    venue = rawdata_i['payload']['venues']
    venue_name = []
    # venue_addr = []
    venue_id = []
    for i in range(len(venue)):
        venue_name.append(venue[i]["name"])  # 戲院名稱
        # venue_addr.append(venue[i]["address"])  # 戲院地址
        venue_id.append(venue[i]["id"])  # 戲院id

    # 抓取場次資訊
    events = rawdata_i['payload']['events']
    for i in range(len(events)):
        
        # 抓取時間
        time_raw = events[i]['startedAt'].split('T')
        date = time_raw[0].replace('-', '/')
        time_i = datetime.datetime.strptime(time_raw[1][0:5], '%H:%M') + datetime.timedelta(hours = 8)
        time_i = time_i.strftime('%H:%M')
        movie_times_all.append(time_i)
        movie_date_all.append(date)
        
        # 抓取戲院 id以及電影 id
        venue_id_i = events[i]['venueId']
        venue_name_i = venue_name[venue_id.index(venue_id_i)]
        movie_venue_all.append(venue_name_i)
        
        movie_id_i = str(events[i]['programId'])
        movie_name_i = movie_name[movie_id.index(movie_id_i)]
        movie_name_all.append(movie_name_i)
        
        # 抓取電影模式
        movie_version_all.append(events[i]["meta"]["format"])
    
    time.sleep(random.randrange(2, 5, 1))


# In[ ]:


# 將電影名稱 和時間資訊 combine 在一起然後再利用pandas pd.merge 合併資料表並且刪除不必要的欄位
movie_ENname_all = [0]*len(movie_name_all)
data = zip(movie_venue_all, movie_date_all, movie_name_all, movie_ENname_all, movie_version_all, movie_times_all)
movie_df = pd.DataFrame(data, columns = ["影城", "日期", "電影(中文)", "電影(英文)", "模式", "時間"])
movie_df.to_csv("E:\pbc\movie_st.csv", index = False, encoding='big5')


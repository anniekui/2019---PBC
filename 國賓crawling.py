#!/usr/bin/env python
# coding: utf-8

# ## 引入模組

# In[ ]:


import requests, re, time, json, random
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup


# ## 國賓影城

# In[ ]:


# 設定 headers
headers = {'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
           'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
           'Referer':'https://www.ambassador.com.tw/home/MovieList?Type=0',
           'Accept-Encoding':'gzip, deflate, br',
           'Accept-Language':'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'}


# In[ ]:


# 開始爬蟲並檢視爬蟲結果
url_gb = "https://www.ambassador.com.tw/home/MovieList?Type=1"
html_gb = requests.get(url_gb, headers=headers)
html_gb.encoding = "utf-8"
## if html_gb.status_code == requests.codes.ok:
##     print(html_gb.text)


# In[ ]:


# 找出各個上映中電影的網址
sp_gb = BeautifulSoup(html_gb.text, "html.parser")
gb_data = sp_gb.find_all("a", {"class":"poster"})  # 找出每個電影的代碼
prefix = 'https://www.ambassador.com.tw/'
gb_movie_url = []
for url in gb_data:
    gb_movie_url.append(prefix + url["href"])


# In[ ]:


# 生成所有可查詢的網址
import datetime
new_gb_movie_url = []
for i in range(len(gb_movie_url)):
    movie_time = datetime.datetime.strptime(gb_movie_url[i][-10:], "%Y/%m/%d")
    prefix_i = gb_movie_url[i][:-10]
    for j in range(5):
        movie_time_i = movie_time + datetime.timedelta(j)  # 生成當日以及五日後的日子
        new_gb_movie_url.append(prefix_i + movie_time_i.strftime("%Y/%m/%d"))  # 形成可搜尋的網址


# In[ ]:


# tag_rating = []
movie_name = []
movie_name_eng = []
movie_data_raw = []
movie_date = []
i=0
for url in new_gb_movie_url:
    html_gbm = requests.get(url, headers=headers)
    html_gb.encoding = "utf-8"
    sp_gb = BeautifulSoup(html_gbm.text, "html.parser")
    # movie_info = sp.find("div",  {"class":"cell small-12 medium-12 large-12 movie-info-box"})  # 找出電影基本資訊
    # tag_rating.append(movie_info.find("span", {"class":"tag-rating-p"}).text)  # 存取分級資料
    gbm_data = sp_gb.find_all("div", {"class":"theater-box"})
    
    if len(gbm_data) == 0:  # 只蒐集有電影時刻的資訊
        continue
    
    movie_name.append(sp_gb.find("h2").text)
    movie_name_eng.append(sp_gb.find("h6").text)
    movie_data_raw.append(gbm_data)
    movie_date.append(url[-10:])


# In[ ]:


movie_time_all = []
movie_date_all = []
movie_name_all = []
movie_version_all = []
movie_venue_all = []
movie_eng_name_all = []
for i in range(len(movie_data_raw)):
    movie_date_i = movie_date[i]
    movie_name_eng_i = movie_name_eng[i]
    movie_data_raw_i = movie_data_raw[i]
    
    # 蒐集時間資訊
    for data in movie_data_raw_i:
        venue_i = data.find("a").text  # 戲院
        # movie_data_raw[0].find_all("span", {"class":"show-for-medium"})  # 地址，電話
        data_i = data.find("p", {"class":"tag-seat"}).text  # 版本，電影名稱
        data_i = data_i.split(')')
        version_i = data_i[0][1:]
        movie_name_i =  data_i[1]
        movie_time_data = data.find_all("h6")  # 時間
        
        for timedata in movie_time_data:
            movie_time_all.append(timedata.text.strip())
            movie_version_all.append(version_i)
            movie_venue_all.append(venue_i)
            movie_name_all.append(movie_name_i)
            movie_eng_name_all.append(movie_name_eng_i)
            movie_date_all.append(movie_date_i)
    


# In[ ]:


# 將電影名稱 和時間資訊 combine 在一起然後再利用pandas pd.merge 合併資料表並且刪除不必要的欄位
data = zip(movie_venue_all, movie_date_all, movie_name_all, movie_eng_name_all, movie_version_all, movie_time_all)
movie_df = pd.DataFrame(data, columns = ["影城", "日期", "電影(中文)", "電影(英文)", "模式", "時間"])
movie_df.to_csv("E:\pbc\movie_gb.csv", index = False, encoding='CP950')


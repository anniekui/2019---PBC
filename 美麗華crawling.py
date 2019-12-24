#!/usr/bin/env python
# coding: utf-8

# ## 引入模組

# In[ ]:


import requests, re, time, json, random
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup


# ## 美麗新影城

# In[ ]:


# 設定 headers
headers = {'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
           'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
           'Referer':'https://www.miranewcinemas.com/Movie/Detail?type=NowShowing&MovieId=1aa49b4d-bfca-411c-b022-ed3cc5f5123b',
           'Accept-Encoding':'gzip, deflate, br',
           'Accept-Language':'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'}


# In[ ]:


# 開始爬蟲並檢視爬蟲結果
url_mn = "https://www.miranewcinemas.com/Booking/Timetable"
html_mn = requests.get(url_mn, headers=headers)
html_mn.encoding = "utf-8"


# In[ ]:


# 找出所需的資訊
start = html_mn.text.find("dash_CinemaList = ")  # 資料開頭引數
end = html_mn.text.find("dash_CinemaList = dash_CinemaList.replace(")  # 資料結尾引數
target = html_mn.text[start:end]


# In[ ]:


movie_time_all = []
movie_date_all = []
movie_name_all = []
movie_version_all = []
movie_venue_all = []
movie_eng_name_all = []

target_clean = target.replace('\\','').replace('\"','') # 清除不必要的符號
target_split = target_clean.split('{CinemaId:') #先切戲院
for i in range(1,len(target_split)):
    venue_start = target_split[i].find(':') + 1
    venue_end = target_split[i].find(',', venue_start)
    venue_name = target_split[i][venue_start:venue_end]
    
    movie_info = target_split[1].split('{PostUrl:')
    for j in range(1,len(movie_info)):
        movie_info_split = movie_info[j].split('{SessionList:')
        
        # 電影中文名稱
        movie_name_start = movie_info_split[0].find(':') + 1
        movie_name_end = movie_info_split[0].find(',', movie_name_start)
        movie_name = movie_info_split[0][movie_name_start:movie_name_end]
        
        # 電影英文名稱
        movie_name_en_start = movie_info_split[0].find(':', movie_name_end) + 1
        movie_name_en_end = movie_info_split[0].find(',', movie_name_en_start)
        movie_name_en = movie_info_split[0][movie_name_en_start:movie_name_en_end]
        
        for k in range(1, len(movie_info_split)):
            
            date_i = re.findall(r'ShowDateISO:[0-9/-]+', movie_info_split[k])
            
            if len(date_i) == 0:
                continue
            
            version_start = movie_info_split[k].find('MovieHallCht:') + 13
            version_end = movie_info_split[k].find(',', version_start)
            version = movie_info_split[k][version_start:version_end]
            
            movie_times_list = re.findall(r'ShowTime:[0-9/:]+', movie_info_split[k])
            for timedata in movie_times_list:
                movie_time_all.append(timedata[-5:])
                movie_version_all.append(version)
                movie_venue_all.append(venue_name)
                movie_name_all.append(movie_name)
                movie_eng_name_all.append(movie_name_en)
                movie_date_all.append(date_i[0][-10:])


# In[ ]:


# 將電影名稱 和時間資訊 combine 在一起然後再利用pandas pd.merge 合併資料表並且刪除不必要的欄位
data = zip(movie_venue_all, movie_date_all, movie_name_all, movie_eng_name_all, movie_version_all, movie_time_all)
movie_df = pd.DataFrame(data, columns = ["影城", "日期", "電影(中文)", "電影(英文)", "模式", "時間"])
movie_df.to_csv("E:\pbc\movie_mn.csv", index = False, encoding='big5')


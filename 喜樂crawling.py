#!/usr/bin/env python
# coding: utf-8

# ## 引入模組

# In[ ]:


import requests, re, time, json, random
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup


# ## 喜樂影城

# In[ ]:


def crawling_sl(prefix, pages):
    
    # 爬取喜樂網站所需 headers
    headers = {'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
           'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
           'Referer':'http://www.centuryasia.com.tw/ticket_online.aspx',
           'Accept-Encoding':'gzip, deflate',
           'Accept-Language':'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'}
    
    movie_date = []
    movie_id = []
    movie_name = []
    movie_name_en = [] 
    for i in range(pages):
        # 開始爬蟲並檢視爬蟲結果
        url_sl = prefix + str(i)
        html_sl = requests.get(url_sl, headers=headers)
        html_sl.encoding = "utf-8" 

        # 找出每個網頁的電影資料
        sp_sl = BeautifulSoup(html_sl.text, "html.parser")
        movie_sl = sp_sl.find_all("section",  {"class":"tickets_movie_time_box"})
        for i in range(len(movie_sl)):
            # 找出電影的播映日期
            movie_date_i = movie_sl[i].find_all("span",  {"class":"tdd_d"})
            for j in range(len(movie_date_i)):  # 只留下日期資訊
                movie_date_i[j] = movie_date_i[j]["value"]
            movie_date.append(movie_date_i)
            movie_id.append(movie_sl[i]["id"])  # 電影 id
            movie_name.append(movie_sl[i].find("div",  {"class":"times_title"}).text)  # 電影中文名稱
            movie_name_en.append(movie_sl[i].find("div",  {"class":"times_title_en"}).text)  # 電影英文名稱
    
    return movie_date, movie_id, movie_name, movie_name_en


# In[ ]:


# 找出兩家戲院的電影 id和名稱等等
movie_date0, movie_id0, movie_name0, movie_name_en0 = crawling_sl("http://www.centuryasia.com.tw/ticket_online.aspx?page=", 4)
movie_date1, movie_id1, movie_name1, movie_name_en1 = crawling_sl("http://beyond.centuryasia.com.tw:81/ticket_online.aspx?page=", 2)


# In[ ]:


def sl_movie_time(movie_date, movie_id, movie_name, movie_name_en, url):
    
    headers_post = {'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
               'Accept':'application/json, text/javascript, */*',
               'Referer':'http://www.centuryasia.com.tw/ticket_online.aspx',
               'Accept-Encoding':'gzip, deflate',
               'Accept-Language':'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'}
    
    movie_time_all = []
    movie_date_all = []
    movie_name_all = []
    movie_version_all = []
    movie_eng_name_all = []

    for i in range(len(movie_id)):
        date_i = movie_date[i]
        for date in date_i:
            payload = {'Date':date, 'ProgramID':movie_id[i]}
            json_sl = requests.post(url, headers=headers_post, data=payload)
            json_sl.encoding = "utf-8"
            movie_time_js = json.loads(json_sl.text)
            
            for i in range(len(movie_time_js)):
                time_list_i = movie_time_js[i]['TimeList']
                sessions_num = len(time_list_i)
                for j in range(sessions_num):
                    time_list_i[j] = time_list_i[j]["Time"]
                movie_time_all.extend(time_list_i)
                movie_version_all.extend([movie_time_js[0]["RoomName_CodeName"].split(' ')[-1]]*sessions_num)  # 找出是甚麼版本的電影
                movie_date_all.extend([date]*sessions_num)
                movie_name_all.extend([movie_name[i]]*sessions_num)
                movie_eng_name_all.extend([movie_name_en[i]]*sessions_num)
    
    return movie_time_all, movie_date_all, movie_name_all, movie_version_all, movie_eng_name_all


# In[ ]:


# 找出兩家戲院的最終目標資訊
url0 = "http://www.centuryasia.com.tw/Ajax/ProgramMovieTime.ashx"
url1 = "http://beyond.centuryasia.com.tw:81/Ajax/ProgramMovieTime.ashx"
movie_time_all0, movie_date_all0, movie_name_all0, movie_version_all0, movie_eng_name_all0 = sl_movie_time(movie_date0, movie_id0, movie_name0, movie_name_en0, url0)
movie_time_all1, movie_date_all1, movie_name_all1, movie_version_all1, movie_eng_name_all1 = sl_movie_time(movie_date1, movie_id1, movie_name1, movie_name_en1, url1)


# In[ ]:


# 生成戲院列表
movie_venue_all0 = ['喜樂時代影城南港店'] * len(movie_time_all0)
movie_venue_all1 = ['喜樂時代影城永和店'] * len(movie_time_all1)

# 合併電影資料
movie_time_all0.extend(movie_time_all1)
movie_date_all0.extend(movie_date_all1)
movie_name_all0.extend(movie_name_all1)
movie_version_all0.extend(movie_version_all1)
movie_venue_all0.extend(movie_venue_all1)
movie_eng_name_all0.extend(movie_eng_name_all1)


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
data = zip(movie_venue_all0, movie_date_all0, movie_name_all0, movie_eng_name_all0, movie_version_all0, movie_time_all0)
movie_df = pd.DataFrame(data, columns = ["影城", "日期", "電影(中文)", "電影(英文)", "模式", "時間"])
movie_df.to_csv("E:\pbc\movie_sl.csv", index = False, encoding='big5')


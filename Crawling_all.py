#!/usr/bin/env python
# coding: utf-8

# In[3]:


import requests, re, csv, datetime, time, json, random
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

def judge3D4D(a):
    if a[0:2] == "3D" or a[0:2] == "4D" or a[0:2] == "數位":
        return True
    else:
        return False


def is_contains_chinese(strs):
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False

def is_contains_english(strs):
    for _char in strs:
        if _char.isalpha():
            return True
    return False

# ==================威秀===================

f = open("vs.csv", "w", encoding = 'cp950', newline="")
writer = csv.writer(f)
writer.writerow(["影城", "日期", "電影(中文)", "電影(英文)", "模式", "時間"])

cinema = ["信義", "京站", "日新", "板橋大遠百", "林口MITSUI OUTLET PARK"]
for i in range(1,6):
    # using requests to "get" a webpage
    url = "https://www.vscinemas.com.tw/vsweb/theater/detail.aspx?id="
    url += str(i)
    r = requests.get(url)

    # using BeautifulSoup to parse the HTML source code: Part 1
    soup = BeautifulSoup(r.text, 'html.parser')
    
    today = datetime.datetime.now()
    for j in range(5):                  # 做五天的結果
        if j != 0:
            x = datetime.timedelta(days = 1)
            today += x
        current_date = str(today.month) + "/" + str(today.day)

        # 找出日期對應到的movieTime，並存在date_id
        a = soup.find_all(href=re.compile("movieTime"))
        for k in range(len(a)):
            a[k] = str(a[k])            # 把它從bs4的資料型態轉成字串
        for date in a:
            if current_date in date:
                b = date.split("\"")
                date_id = b[1][1:]
                break
        current_date = str(today.year) + "/" + str(today.month) + "/" + str(today.day)
        
        # 把不必要的空白和換行去掉
        movie_list = []
        attr = {"id": date_id}
        theaterTime_tags = soup.find("article", attrs = attr)
        line = theaterTime_tags.get_text().strip().split("\n")
        for k in range(len(line)):
            if line[k] != "":
                movie_list.append(line[k])

        # 把資訊寫進csv
        for k in range(1, len(movie_list)):
            if judge3D4D(movie_list[k]):                 # 模式(數位/3D/4D)
                mode = movie_list[k]
            elif movie_list[k][0:2].isdigit() and movie_list[k][3:5].isdigit() and movie_list[k][2] == ":":          # 時間(幾點幾分)
                time = movie_list[k]
                writer.writerow([cinema[i-1], current_date, chinese_name, english_name, mode, time])
            elif is_contains_chinese(movie_list[k]):     # 中文名
                chinese_name = movie_list[k]
            else:                                        # 英文名
                english_name = movie_list[k]
f.close()

# ==================喜滿客===================

f = open("sm.csv", "w", encoding = 'cp950', newline="")
writer = csv.writer(f)
writer.writerow(["影城", "日期", "電影(中文)", "電影(英文)", "模式", "時間"])

today = datetime.datetime.now()
for j in range(5):                  # 做五天的結果
    if j != 0:
        x = datetime.timedelta(days = 1)
        today += x
    current_date = str(today.year) + "/" + str(today.month) + "/" + str(today.day)

    # using requests to "get" a webpage
    url = "https://www.cinemark.com.tw/movie_list?m=1&area=2&date=" + str(today.year)
    url += "-" + str(today.month) + "-" + str(today.day) + "&id="
    r = requests.get(url)

    # using BeautifulSoup to parse the HTML source code: Part 1
    soup = BeautifulSoup(r.text, 'html.parser')
    
    attr = {"class": "col-xs-12 col-md-9 txt"}
    theaterTime_tags = soup.find_all("div", attrs = attr)
    
    # 把不必要的空白和換行去掉(喜滿客的網頁真的很怪，試很多方法才把他的資料變乾淨...)
    information = []
    for k in range(len(theaterTime_tags)):
        line = theaterTime_tags[k].get_text().strip().split("\t")
        for i in range(len(line)):            
            lineline = line[i].split("\n")
            for m in range(len(lineline)):
                if lineline[m] == "":
                    continue
                elif lineline[m][0].isalpha() or lineline[m][0].isdigit() or is_contains_chinese(lineline[m][0]) or lineline[m][0] == "(":
                    information.append(lineline[m])
    
    # 把不必要的資訊去除後，存入result
    result = []
    for i in range(len(information)):
        if (len(information[i]) >= 2) and (information[i][0:2] == "上映" or information[i][0:2] == "電影" or information[i][0:2] == "場次"):
            pass
        else:
            result.append(information[i])

    # 把資訊寫進csv
    time_list = []
    mode = ""
    for i in range(len(result)):
        if is_contains_chinese(result[i]):     # 中文名
            mode = ""
            if result[i][0:3] == "(英)" or result[i][0:3] == "(國)":
                mode = result[i][0:3]
                chinese_name = result[i][3:]
            else:
                chinese_name = result[i]
        elif is_contains_english(result[i]):   # 英文名
            english_name = result[i]
        else:                                  # 時間(幾點幾分)
            time = result[i][0:5]              # (重要)他時間欄後面會有些奇怪的空格，所以只取前5個字元
            time_list.append(time)

            # 把同一天同一部的電影時間排序好(因為喜滿客有分廳，時間會亂掉)
            if (i == len(result) - 1) or (len(result[i+1]) != 5) or not (result[i+1][0:2].isdigit()):
                time_list = sorted(time_list)

                for k in range(len(time_list)):
                    writer.writerow(["絕色", current_date, chinese_name, english_name, mode, time_list[k]])
                time_list = []                                        # (重要)把內容清空

f.close()

# ==================新光===================

f = open("sg.csv", "w", encoding = 'cp950', newline="")
writer = csv.writer(f)
writer.writerow(["影城", "日期", "電影(中文)", "電影(英文)", "模式", "時間"])

# 把五日的日期存進date_list中
today = datetime.datetime.now()
date_list = []
for j in range(5):                  # 做五天的結果
    if j != 0:
        x = datetime.timedelta(days = 1)
        today += x
    
    current_date = str(today.month) + "/" + str(today.day)
    date_list.append(current_date)

# using requests to "get" a webpage
url = "http://www.skcinemas.com/ALLMovie.aspx"
r = requests.get(url)

# using BeautifulSoup to parse the HTML source code: Part 1
soup = BeautifulSoup(r.text, 'html.parser')
    
attr = {"style": "margin-top:-1px;"}
theaterTime_tags = soup.find("div", attrs = attr)
    
# 把不必要的空白和換行去掉，並存進information中
information = []
line = theaterTime_tags.get_text().strip().split("\n")
for i in range(len(line)):
    if line[i] != "":
        information.append(line[i])

for i in range(len(information)):
    if information[i][2] == "/":       # 這行是日期，後面是時刻表
        """
        if information[i][:5] not in date_list:       # 不在要找的日期內
            flag = 1
            continue
        """
        
        date = information[i][:5]      # 儲存日期
        
        for j in range(12, len(information[i])):
            if information[i][j] == ":":
                time = information[i][j-2:j+3]
                writer.writerow(["台北", date, chinese_name, english_name, mode, time])
    # 表示這行是延續上一行的時刻
    elif information[i][2] == ":" or (information[i][0].isdigit() and information[i][1] == "廳"):
        for j in range(len(information[i])):
            if information[i][j] == ":":
                time = information[i][j-2:j+3]
                writer.writerow(["台北", date, chinese_name, english_name, mode, time])
    else:                              # 中英文片名
        # 找出最後一個中文字的位置
        for j in range(len(information[i])):
            if is_contains_chinese(information[i][j]):
                end = j
        
        # 找出最後一個中文字後面的斷點(空格)
        for j in range(end, len(information[i])):
            if information[i][j] == " ":
                end = j
                break
        
        # 處理特別標註中文版或英文版的情況
        if information[i][:3] == "中文版" or information[i][:3] == "英文版":
            mode = information[i][:3]
            begin = 4
        else:
            mode = ""
            begin = 0
    
        chinese_name = information[i][begin:end]
        english_name = information[i][end+1:]

f.close()

# ==================in89===================

f = open("in89.csv", "w", encoding = 'cp950', newline="")
writer = csv.writer(f)
writer.writerow(["影城", "日期", "電影(中文)", "電影(英文)", "模式", "時間"])


today = datetime.datetime.now()
for j in range(5):                  # 做五天的結果
    if j != 0:
        x = datetime.timedelta(days = 1)
        today += x
    current_date = str(today.year) + "/" + str(today.month) + "/" + str(today.day)


    # using requests to "get" a webpage
    if j == 0:
        url = "http://www.atmovies.com.tw/showtime/t02b12/a02/"          # 當天的網址不會有日期
    else:
        url = "http://www.atmovies.com.tw/showtime/t02b12/a02/2019" + str(today.month) + str(today.day) + "/"
    r = requests.get(url)

    # using BeautifulSoup to parse the HTML source code: Part 1
    soup = BeautifulSoup(r.text, 'html.parser')

    attr = {"id": "theaterShowtimeBlock"}
    theaterTime_tags = soup.find("div", attrs = attr)

    # 把不必要的空白、換行以及google ad去掉，並存進information中
    information = []
    line = theaterTime_tags.get_text().strip().split("\n")
    for i in range(len(line)):
        if (line[i] != "") and (line[i][0:2] != "其他") and (line[i][0:3] != " 片長"):
            if (line[i][0:2] != "<!") and (line[i][0:2] != "//"):
                if (line[i][0:2] != "/*") and (line[i][0:2] != "go"):
                    information.append(line[i])
    
    mode = ""          # 有些電影她不會顯示出模式...(所以要用預設空字串處理)
    for i in range(len(information)):
        #information[i] = information[i].replace("\xa0", " ")   # 因為\xa0無法用cp950寫檔

        if (len(information[i]) >= 5) and information[i][0:2].isdigit() and information[i][2] == "：":      # 時刻(他的冒號是中文冒號)
            time = information[i][0:5]
            writer.writerow(["台北西門", current_date, chinese_name, english_name, mode, time])
            mode = ""
        elif "版" in information[i]:                 # 模式(但這種判別方式有點粗糙...如果電影名有"版"就完了)
            a = information[i].split(" ")
            mode = a[0]
            
            if len(a) > 1:                           # 有些「XX版」後面會接一個電影時刻，有些不會...
                time = a[1][0:5]                     # 「時刻」和「請訂票」中間不是空白...(而是\xa0)
                writer.writerow(["台北西門", current_date, chinese_name, english_name, mode, time])
                mode = ""
        elif is_contains_chinese(information[i]):
            chinese_name = information[i]
            english_name = ""                        # 這個網站沒有放上電影的英文名
        else:                                        # (注意)它有些「時刻」前面會有超長一段空格
            for k in range(len(information[i])):
                if information[i][k] == "：":
                    time = information[i][k-2:k+3]
                    writer.writerow(["台北西門", current_date, chinese_name, english_name, mode, time])
                    mode = ""

f.close()

# ==================秀泰===================

url = 'https://capi.showtimes.com.tw/1/programs/listPopularForStore/1?nocache=0'
headers = {'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
rawdata = requests.get(url, headers=headers).text

# 只留下需要的電影資訊
movie_name_js = json.loads(rawdata)
movie_name_js = movie_name_js["payload"]["programs"]  

# 找出電影名稱 以及 movie id
movie_name = []
movie_id = []
for i in range(len(movie_name_js)):
    movie_name.append(movie_name_js[i]["name"])  # 電影名稱
    movie_id.append(str(movie_name_js[i]["id"]))  # 電影id

data = zip(movie_id, movie_name)
movie_id_df = pd.DataFrame(data, columns = ["movie_id", "movie_name"])

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


# 將電影名稱 和時間資訊 combine 在一起然後再利用pandas pd.merge 合併資料表並且刪除不必要的欄位
movie_ENname_all = [0]*len(movie_name_all)
data = zip(movie_venue_all, movie_date_all, movie_name_all, movie_ENname_all, movie_version_all, movie_times_all)
movie_df = pd.DataFrame(data, columns = ["影城", "日期", "電影(中文)", "電影(英文)", "模式", "時間"])
movie_df.to_csv("st.csv", index = False, encoding='cp950')

# ==================美麗華===================

headers = {'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
           'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
           'Referer':'https://www.miranewcinemas.com/Movie/Detail?type=NowShowing&MovieId=1aa49b4d-bfca-411c-b022-ed3cc5f5123b',
           'Accept-Encoding':'gzip, deflate, br',
           'Accept-Language':'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'}

# 開始爬蟲並檢視爬蟲結果
url_mn = "https://www.miranewcinemas.com/Booking/Timetable"
html_mn = requests.get(url_mn, headers=headers)
html_mn.encoding = "utf-8"

# 找出所需的資訊
start = html_mn.text.find("dash_CinemaList = ")  # 資料開頭引數
end = html_mn.text.find("dash_CinemaList = dash_CinemaList.replace(")  # 資料結尾引數
target = html_mn.text[start:end]

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
        movie_name_end = movie_info_split[0].find('(', movie_name_start)
        movie_name = movie_info_split[0][movie_name_start:movie_name_end]
        
        # 電影英文名稱
        movie_name_en_start = movie_info_split[0].find(':', movie_name_end) + 1
        movie_name_en_end = movie_info_split[0].find('(', movie_name_en_start)
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

# 將電影名稱 和時間資訊 combine 在一起然後再利用pandas pd.merge 合併資料表並且刪除不必要的欄位
data = zip(movie_venue_all, movie_date_all, movie_name_all, movie_eng_name_all, movie_version_all, movie_time_all)
movie_df = pd.DataFrame(data, columns = ["影城", "日期", "電影(中文)", "電影(英文)", "模式", "時間"])
movie_df.to_csv("mn.csv", index = False, encoding='cp950')

# ==================國賓===================

# 設定 headers
headers = {'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
           'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
           'Referer':'https://www.ambassador.com.tw/home/MovieList?Type=0',
           'Accept-Encoding':'gzip, deflate, br',
           'Accept-Language':'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'}

# 開始爬蟲並檢視爬蟲結果
url_gb = "https://www.ambassador.com.tw/home/MovieList?Type=1"
html_gb = requests.get(url_gb, headers=headers)
html_gb.encoding = "utf-8"
## if html_gb.status_code == requests.codes.ok:
##     print(html_gb.text)

# 找出各個上映中電影的網址
sp_gb = BeautifulSoup(html_gb.text, "html.parser")
gb_data = sp_gb.find_all("a", {"class":"poster"})  # 找出每個電影的代碼
prefix = 'https://www.ambassador.com.tw/'
gb_movie_url = []
for url in gb_data:
    gb_movie_url.append(prefix + url["href"])

# 生成所有可查詢的網址
import datetime
new_gb_movie_url = []
for i in range(len(gb_movie_url)):
    movie_time = datetime.datetime.strptime(gb_movie_url[i][-10:], "%Y/%m/%d")
    prefix_i = gb_movie_url[i][:-10]
    for j in range(5):
        movie_time_i = movie_time + datetime.timedelta(j)  # 生成當日以及五日後的日子
        new_gb_movie_url.append(prefix_i + movie_time_i.strftime("%Y/%m/%d"))  # 形成可搜尋的網址

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

# 將電影名稱 和時間資訊 combine 在一起然後再利用pandas pd.merge 合併資料表並且刪除不必要的欄位
data = zip(movie_venue_all, movie_date_all, movie_name_all, movie_eng_name_all, movie_version_all, movie_time_all)
movie_df = pd.DataFrame(data, columns = ["影城", "日期", "電影(中文)", "電影(英文)", "模式", "時間"])
movie_df.to_csv("gb.csv", index = False, encoding='cp950')

# ==================喜樂===================

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

# 找出兩家戲院的電影 id和名稱等等
movie_date0, movie_id0, movie_name0, movie_name_en0 = crawling_sl("http://www.centuryasia.com.tw/ticket_online.aspx?page=", 4)
movie_date1, movie_id1, movie_name1, movie_name_en1 = crawling_sl("http://beyond.centuryasia.com.tw:81/ticket_online.aspx?page=", 2)

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

# 找出兩家戲院的最終目標資訊
url0 = "http://www.centuryasia.com.tw/Ajax/ProgramMovieTime.ashx"
url1 = "http://beyond.centuryasia.com.tw:81/Ajax/ProgramMovieTime.ashx"
movie_time_all0, movie_date_all0, movie_name_all0, movie_version_all0, movie_eng_name_all0 = sl_movie_time(movie_date0, movie_id0, movie_name0, movie_name_en0, url0)
movie_time_all1, movie_date_all1, movie_name_all1, movie_version_all1, movie_eng_name_all1 = sl_movie_time(movie_date1, movie_id1, movie_name1, movie_name_en1, url1)

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
    
# 將電影名稱 和時間資訊 combine 在一起然後再利用pandas pd.merge 合併資料表並且刪除不必要的欄位
data = zip(movie_venue_all0, movie_date_all0, movie_name_all0, movie_eng_name_all0, movie_version_all0, movie_time_all0)
movie_df = pd.DataFrame(data, columns = ["影城", "日期", "電影(中文)", "電影(英文)", "模式", "時間"])
movie_df.to_csv("sl.csv", index = False, encoding='cp950')


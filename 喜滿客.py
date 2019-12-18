import requests, re, csv, datetime
from bs4 import BeautifulSoup 


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

f = open("D:\\3.csv", "w", encoding = 'cp950', newline="")
writer = csv.writer(f)
writer.writerow(["喜滿客影城"])      # 第一行為戲院名稱
writer.writerow(["影城", "日期", "電影(中文)", "電影(英文)", "模式", "時間"])

today = datetime.datetime.now()
for j in range(5):                  # 做五天的結果
    if j != 0:
        x = datetime.timedelta(days = 1)
        today += x
    current_date = str(today.month) + "/" + str(today.day)

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
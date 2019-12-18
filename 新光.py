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

f = open("D:\\5.csv", "w", encoding = 'cp950', newline="")
writer = csv.writer(f)
writer.writerow(["新光影城"])      # 第一行為戲院名稱
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
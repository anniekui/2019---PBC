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


f = open("D:\\7.csv", "w", encoding = 'cp950', newline="")
writer = csv.writer(f)
writer.writerow(["in89豪華數位影城"])      # 第一行為戲院名稱
writer.writerow(["影城", "日期", "電影(中文)", "電影(英文)", "模式", "時間"])


today = datetime.datetime.now()
for j in range(5):                  # 做五天的結果
    if j != 0:
        x = datetime.timedelta(days = 1)
        today += x
    current_date = str(today.month) + "/" + str(today.day)


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

    for i in range(len(information)):
        #information[i] = information[i].replace("\xa0", " ")   # 因為\xa0無法用cp950寫檔

        if (len(information[i]) >= 5) and information[i][0:2].isdigit() and information[i][2] == "：":      # 時刻(他的冒號是中文冒號)
            time = information[i][0:5]
            writer.writerow(["台北西門", current_date, chinese_name, english_name, mode, time])
        elif "版" in information[i]:                 # 模式(但這種判別方式有點粗糙...如果電影名有"版"就完了)
            a = information[i].split(" ")
            mode = a[0]
            
            if len(a) > 1:                           # 有些「XX版」後面會接一個電影時刻，有些不會...
                time = a[1][0:5]                     # 「時刻」和「請訂票」中間不是空白...(而是\xa0)
                writer.writerow(["台北西門", current_date, chinese_name, english_name, mode, time])
        elif is_contains_chinese(information[i]):
            chinese_name = information[i]
            english_name = ""                        # 這個網站沒有放上電影的英文名
        else:                                        # (注意)它有些「時刻」前面會有超長一段空格
            for k in range(len(information[i])):
                if information[i][k] == "：":
                    time = information[i][k-2:k+3]
                    writer.writerow(["台北西門", current_date, chinese_name, english_name, mode, time])

f.close()
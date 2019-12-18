import requests, re, csv, datetime
from bs4 import BeautifulSoup 


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


f = open("D:\\1.csv", "w", encoding = 'cp950', newline="")
writer = csv.writer(f)
writer.writerow(["威秀(台北)"])      # 第一行為戲院名稱
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
            elif movie_list[k][0:2].isdigit():          # 時間(幾點幾分)
                time = movie_list[k]
                writer.writerow([cinema[i-1], current_date, chinese_name, english_name, mode, time])
            elif is_contains_chinese(movie_list[k]):     # 中文名
                chinese_name = movie_list[k]
            else:                                        # 英文名
                english_name = movie_list[k]
f.close()
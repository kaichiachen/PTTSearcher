# PttCrawler  
ptt的爬蟲程式，利用[scrapy](http://doc.scrapy.org/en/latest/intro/install.html)套件，根據指定的看板及時間，抓取標題、時間、作者、內文、評論  

### 環境設定
+ python2.7 或 3.3以上
+ 安裝Scrapy  
    利用pip  

        pip install Scrapy
    或是Anaconda  

        conda install -c scrapinghub scrapy

## 抓取資料
根據看板及時間抓取資料後並匯出到json檔

	scrapy crawl ptt -o graduate.json
當然，你也可以客製化匯出到自己的sql等等，另外，設定看板及時間的部分在底下客製化的部分會提到
## 搜索
爬到內容後，看個人興趣想做什麼應用，像我就做了一個簡單的全文檢索

    python search.py -b soft_job.json -k 機器學習 大數據 big\ data

+ -b : 要搜索的檔案
+ -k : 陣列，搜索的關鍵字
+ -h : help

<img src="http://i.imgur.com/1mZg2rV.png" alt="Drawing" width = "600" height = "400" />

另外，在mac的環境下，只要按住Command並點兩下網址就會自動開啟超連結囉！
## 客製化
在專案目錄下的

    /ptt/settings.py
其中
+ DOWNLOAD_DELAY : 延遲時間
+ BOARD : 看板名稱
+ STOP_DATE : 爬到何時停止，例如

        STOP_DATE = {
	        'year': 2016,
	        'month': 07,
	        'day': 10
        }
    就是最新的一篇爬到2016-07-10日的文章為止

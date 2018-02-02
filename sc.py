# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib,urllib2,urlparse,os,time,thread,sys,random
import userLogin
class Scrapy:
    def __init__(self,scrapy_url = 'http://bbs.tianya.cn/',deepth = 1):
        self.scrapy_url = scrapy_url
        self.linksTarget = [scrapy_url]
        self.deepth = deepth
        self.historyLinks = []
        self.locks = [] # 用于存储线程锁
        self.imgHeader = {
            'Host':'img3.laibafile.cn',
            'Referer':'http://bbs.tianya.cn/post-no04-2783444-1.shtml',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        }
        self.userHeader = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
            'Connection': 'keep-alive',
            'Host': 'passport.tianya.cn',
            'Origin':'https://passport.tianya.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
            'Referer': 'https://passport.tianya.cn/register/default.jsp',
        }
        if not os.path.exists('img'):
            os.mkdir('img')
        self.sessionHandl = userLogin.getCookie(self.userHeader)



    def download(self,delay = False,callBack = False,save = "file"):
        while self.linksTarget:
            scrapyLinks = self.linksTarget.pop()
            par = urlparse.urlparse(scrapyLinks)
            baseLink = par.scheme+'://'+par.netloc
            if scrapyLinks in self.historyLinks:
                continue
            request = urllib2.Request(scrapyLinks,headers = self.userHeader)
            try:
                res = urllib2.urlopen(request).read()
                self.historyLinks.append(scrapyLinks)
                self.draw_links(baseLink,res)
                print "download links:"+scrapyLinks+" successed!"
            except urllib2.URLError as e:
                print e.reason
                sys.exit()
            time.sleep(1)

    def draw_links(self,baseLink,res):
        pageLinks = []
        linksBody = BeautifulSoup(res,'html.parser')
        #获取当页文章链接
        tar = linksBody.find_all('td',class_="td-title")
        for t in tar:
            k = t.find('a')
            pageLinks.append(urlparse.urljoin(baseLink,k['href']))
        self.scrapImages(pageLinks)
        # 阻塞主进程,等待子进程结束
        for lock in self.locks:
            while lock.locked():
                pass
        # 获取添加下一页链接
        nextLink = linksBody.find(string="下一页").find_parent('a')
        self.linksTarget.append(urlparse.urljoin(baseLink,nextLink['href']))

    def delay(self):
        pass

    def scrapImages(self,pageLinks):
        for link in pageLinks:
            try:
                lock = thread.allocate_lock()
                lock.acquire()
                self.locks.append(lock)
                thread.start_new_thread(self.scImages,(link,lock,))
            except Exception as e:
                print e.message

    def scImages(self,link,lock):
        try:
            res = urllib2.urlopen(link).read()
        except Exception as e:
            sys.exit(e.message)
        article = BeautifulSoup(res,'html.parser')
        articleBody = article.find_all('div',class_="atl-con-bd clearfix")
        # 找出所有图片
        for bd in articleBody:
            img = bd.find('img')
            if img:
                self.store(img.get('original',''))
        lock.release()
        thread.exit_thread()

    def store(self,imgLink):
        if not imgLink:
            return False
        param = urlparse.urlparse(imgLink)
        fileName = os.path.basename(imgLink)
        try:
            request = urllib2.Request(imgLink, headers=self.imgHeader)
            res = urllib2.urlopen(request).read()
            fileHandle = open('img/'+fileName,'wb+')
            fileHandle.write(res)
            print "download image:"+fileName+" successed!"
        except Exception as e:
            print e.message

    def sendMyMessage(self):
        sendLink = 'http://www.tianya.cn/api/tw?method=tweet.ice.insert&_v=1517384483816'
        sendData = self.getSendData()
        res = self.sessionHandl.post(sendLink, headers=self.userHeader, data=sendData)
        print res.text.encode('utf-8')
    def getSendData(self):
        return {
            'params.appId':'qing',
            'params.sourceName':'天涯随记',
            'params.title':random.randint(1000000,20000000000),
            'params.body':random.randint(1000000,20000000000)
        }
scr = Scrapy('http://bbs.tianya.cn/list.jsp?item=no04&nextid=1517261310000')
# 下载文章图片
# scr.download

# 发心情说说
scr.sendMyMessage()
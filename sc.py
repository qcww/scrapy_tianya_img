# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib,urllib2,urlparse,os,time,random,thread,sys
class Scrapy:
    def __init__(self,scrapy_url = 'http://bbs.tianya.cn/',deepth = 1):
        self.scrapy_url = scrapy_url
        self.linksTarget = [scrapy_url]
        self.deepth = deepth
        self.historyLinks = []
        self.imgHeader = {'Host':'img3.laibafile.cn',
                             'Referer':'http://bbs.tianya.cn/post-no04-2783444-1.shtml',
                             'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
        self.userHeader = {'Cookie':'ADVC=35e6bef4f74027; __cid=25; __cfduid=da38e0c53d9e959f85c798bc21c8fffee1517188166; __auc=652b169f1613f76343eb40904cc; __guid=1644330628; __guid2=1644330628; bc_ids_w=35; ASL=17562,00jjj,73ee686673ee686673ee6866; ADVS=35e851f81e66ec; time=ct=1517361311.276; __ptime=1517361311289; tianya1=12980,1517361251,3,272,18768,1517361305,3,258; Hm_lvt_bc5755e0609123f78d0e816bf7dee255=1517201551,1517275170,1517361312; Hm_lpvt_bc5755e0609123f78d0e816bf7dee255=1517361312',
                           'Host':'bbs.tianya.cn',
                           'Referer':'http://bbs.tianya.cn/list.jsp?item=no04&nextid=1517261310000',
                           'Upgrade-Insecure-Requests':'1',
                           'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
        if not os.path.exists('img'):
            os.mkdir('img')
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
                # self.store(res,str(fileName[0]),dirPath)
                print "download links:"+scrapyLinks+" successed!"
                time.sleep(120)
            except urllib2.URLError as e:
                print e.reason
    def draw_links(self,baseLink,res):
        pageLinks = []
        linksBody = BeautifulSoup(res,'html.parser')
        # 获取下一页链接
        nextLink = linksBody.find(string="下一页").find_parent('a')

        self.linksTarget.append(urlparse.urljoin(baseLink,nextLink['href']))

        #获取当页文章链接
        tar = linksBody.find_all('td',class_="td-title")
        for t in tar:
            k = t.find('a')
            pageLinks.append(urlparse.urljoin(baseLink,k['href']))
        self.scrapImages(pageLinks)
    def delay(self):
        pass
    def scrapImages(self,pageLinks):
        for link in pageLinks:
            try:
                thread.start_new_thread(self.scImages,(link,))
            except:
                print "Error: unable to start thread"
            time.sleep(5)
    def scImages(self,link):
        try:
            res = urllib2.urlopen(link).read()
        except:
            print "download links:"+link+" faild!"
            return False

        article = BeautifulSoup(res,'html.parser')
        articleBody = article.find_all('div',class_="atl-con-bd clearfix")
        # 找出所有图片
        for bd in articleBody:
            img = bd.find('img')
            if img:
                self.store(img.get('original',''))

    def store(self,imgLink):
        if not imgLink:
            return False
        param = urlparse.urlparse(imgLink)
        fileName = param.path.split('/')
        try:
            request = urllib2.Request(imgLink, headers=self.imgHeader)
            res = urllib2.urlopen(request).read()
            fileHandle = open('img/'+fileName[-1:][0],'wb+')
            fileHandle.write(res)
            print "download image:"+fileName[-1:][0]+" successed!"
        except Exception as e:
            print e.message

scr = Scrapy('http://bbs.tianya.cn/list.jsp?item=no04&nextid=1517261310000')
scr.download()
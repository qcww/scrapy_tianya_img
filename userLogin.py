# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re,requests,ConfigParser,sys
def getCookie(userHeader):
    # 1.获取form表单sid
    loginLink = 'https://passport.tianya.cn/login'
    session = requests.session()
    try:
        res = session.get(loginLink)
        sidContent = res.text.encode('utf-8')
        sidBeautiful = BeautifulSoup(sidContent, 'html.parser')
        sid = sidBeautiful.find('div', id='sign_in').find('input', {'name': '__sid'})['value']
    except Exception as e:
        print e.message
    config = ConfigParser.ConfigParser()
    config.read('config.cfg')
    requestData = {
        'fowardURL': '',
        'from': '',
        '__sid': sid,
        'vwriter': config.get('account','user'),
        'action': "",
        'vpassword': config.get('account','password'),
        'rmflag': '1'
    }

    res = session.post(loginLink, headers=userHeader, data=requestData)
    loginRes = res.text.encode('utf-8')
    forwardLink = re.findall("location.href=\"(.*)\"", loginRes)[0]
    forwardCont = session.get(forwardLink, verify=False).text.encode('utf-8')
    # 最终登录在这里,天涯论坛用了多域名登录分别再请求登录的jsp链接保存登录cookie
    jspLink = BeautifulSoup(forwardCont, 'html.parser')
    jspLoginLink = jspLink.find_all('script')
    for sr in jspLoginLink:
        loginTargetLinks = sr.get('src', '')
        if loginTargetLinks:
            session.get(loginTargetLinks)
    return session
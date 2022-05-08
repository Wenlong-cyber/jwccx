import requests
from selenium import webdriver
import time
from datetime import date
from lxml import etree
global headers
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import re
import os
import json
from requests.cookies import RequestsCookieJar
from collections import defaultdict
import streamlit as st

@st.experimental_singleton
def installff():
  os.system('sbase install geckodriver')
  os.system('ln -s /home/appuser/venv/lib/python3.7/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')
    
def get_dict(s):
    ans = {}
    for lst in s.split('\n'):
        key, value = lst.split(': ')
        ans[key] = value
    return ans


def keeptry(xpath):
    while True:
        try:
            btn = bro.find_element(By.XPATH, xpath)
            btn.click()
            break
        except:
            continue

def keepfind(xpath):
    while True:
        try:
            btn = bro.find_element(By.XPATH, xpath)
            return btn
        except:
            continue
def getMycookies(bro, user, psw):
    time.sleep(1)
    btn1 = bro.find_element(By.XPATH, '//*[@id="ampHasNoLogin"]')
    btn1.click()
    id = bro.find_element(By.XPATH, '//*[@id="form1"]/input[1]')
    id.send_keys(user)
    sec = bro.find_element(By.XPATH, '//*[@id="form1"]/input[2]')
    sec.send_keys(psw)
    btn2 = bro.find_element(By.XPATH, '//*[@id="account_login"]')
    btn2.click()
    time.sleep(1)
    cjcx_str = '//*[@id="widget-hot-01"]/div[1]/widget-app-item[%d]/div/div/div[2]/div[1]'
    start = 1
    cjcx = keepfind(format(cjcx_str) % start)
    while cjcx.text != '成绩查询':
        start += 1
        cjcx = keepfind(format(cjcx_str) % start)
    cjcx.click()
    window_handles = bro.window_handles
    try:
        bro.switch_to.window(window_handles[1])
    except:
        temp_btn = bro.find_element(By.XPATH, '//*[@id="ampDetailEnter"]')
        temp_btn.click()
        window_handles = bro.window_handles
        bro.switch_to.window(window_handles[1])
    frame_element = bro.find_element(By.XPATH, "/html/body/iframe")
    bro.switch_to.frame(frame_element) #跳转到新的页面
    btn4 = bro.find_element(By.XPATH, '//*[@id="12aa5b5d-3791-4a69-8fda-6e1768da4d97"]')
    btn4.click() #点击后进入了最近两学期的成绩
    cookie = bro.get_cookies()
    jsonCookies = json.dumps(cookie)
#    with open('anquan.txt', 'w') as f:
#        f.write(jsonCookies)
#     with open('anquan.txt', 'r', encoding='utf8') as f:
#         listCookies = json.loads(f.read())
    return cookie
def crwal_data(cookie):
    # 成绩获取
    url = "http://ehall.xjtu.edu.cn/jwapp/sys/cjcx/modules/cjcx/jddzpjcxcj.do"
    headers = get_dict("""Accept: application/json, text/javascript, */*; q=0.01
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Connection: keep-alive
Content-Length: 583
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Host: ehall.xjtu.edu.cn
Origin: http://ehall.xjtu.edu.cn
Referer: http://ehall.xjtu.edu.cn/jwapp/sys/cjcx/*default/index.do?amp_sec_version_=1&gid_=RDQwUit4dVUvcVhyWG5VK1VnS1QxN1ROV1NMVHlUemFMUU02ZktBcW11dUFhc04vNmlLeW95OG5JY3pYZVRTak9PMjZycGptMDVrSDk4dGxDck9rY2c9PQ&EMAP_LANG=zh&THEME=cherry
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36
X-Requested-With: XMLHttpRequest""")
    # data 用于获取最近成绩
    data = get_dict("""querySetting: [{"name":"XNXQDM","value":"2021-2022-2","linkOpt":"and","builder":"m_value_equal"},{"name":"XH","value":"2193511382","linkOpt":"and","builder":"m_value_equal"},{"name":"SFYX","caption":"是否有效","linkOpt":"AND","builderList":"cbl_m_List","builder":"m_value_equal","value":"1","value_display":"是"}]
*order: KCH,KXH
pageSize: 10
pageNumber: 1""")
    # data1 用于获取过去所有成绩
    data1 = get_dict("""querySetting: [{"name":"SFYX","caption":"是否有效","linkOpt":"AND","builderList":"cbl_m_List","builder":"m_value_equal","value":"1","value_display":"是"},{"name":"XNXQDM","value":"2021-2022-2","builder":"notEqual","linkOpt":"and"}]
pageSize: 1000
pageNumber: 1""")
    session = requests.session()
    jar = RequestsCookieJar()
    for item in cookie:
        jar.set(item['name'], item['value'])
    session.cookies.update(jar)
    text1 = session.post(url=url, headers=headers, data=data).text
    text2 = session.post(url=url, headers=headers, data=data1).text
    # 数据存储1
    data = defaultdict(list)
    for mark in json.loads(text1)['datas']['jddzpjcxcj']['rows']:
    #     print("当前课程", mark['KCM'])
        for item in mark:
            data[item].append(mark[item])
    # 数据存储2
    for mark in json.loads(text2)['datas']['jddzpjcxcj']['rows']:
    #     print("当前课程", mark['KCM'])
        for item in mark:
            data[item].append(mark[item])
    data_frame = pd.DataFrame.from_dict(data)
    data_frame['JQCJ'] = data_frame['XF'].map(float)*data_frame['ZCJ']
    #data_frame.to_csv("./data.csv", encoding="utf-8-sig")
    return data_frame
    # KKDWDM_DISPLAY : 课程学院 (经济与金融学院)
    # XNXQDM : 学年学期 (2021-2022-2)
    # QMCJ : 期末成绩
    # PSCJ : 平时成绩
    # KCM : 课程名
    # KCXZDM_DISPLAY : 课程性质(必修)
    # ZCJ : 总成绩
    # XF : 学分
    # SFZX_DISPLAY : 是否主修
def cal_mean(data, KCXZDM_options, SFXZDM_options, XQ_options):
    # 加权成绩
    data_frame = data[data['XNXQDM'].isin(XQ_options)]
    data_frame = data_frame[data_frame['KCXZDM_DISPLAY'].isin(KCXZDM_options)]
    data_frame = data_frame[data_frame['SFZX_DISPLAY'].isin(SFXZDM_options)]
    ZXF = sum(data_frame['XF'].map(float))
    JF = sum(data_frame['JQCJ']/ZXF)
    return JF,data_frame
def getMessage(user,psw):
    cookie = getMycookies(bro)
    data_frame = crwal_data(cookie)
    #['KKDWDM_DISPLAY','XNXQDM','QMCJ','PSCJ','KCM','KCXZDM_DISPLAY','ZCJ','XF','SFZX_DISPLAY']
    st.dataframe(data_frame[['KCM','ZCJ']])
def form_callback():
    return
if __name__ == "__main__":
    _ = installff()
    sslist = ['login', 'data']
    st.title("XJTU_")
    st.header("Welcome to here!")
    for ss in sslist:
        if ss not in st.session_state:
            st.session_state[ss] = ""
    if st.session_state['login']=="":
        url = 'http://ehall.xjtu.edu.cn/new/index.html?browser=no'
        chrome_options = Options()
        
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        #chrome_options.add_argument('--disable-gpu')
        bro = webdriver.Chrome(options=chrome_options)
        bro.get(url=url)
        bro.maximize_window()
    #     cookie = getMycookies(bro)
        
        user = st.text_input("账号","13178099909")
        psw = st.text_input("密码","",type="password")
        if st.button("登录"):
            cookie = getMycookies(bro, user, psw)
            st.session_state['data'] = crwal_data(cookie)
            st.dataframe(st.session_state['data'][['KCM','ZCJ']])
            st.session_state['login'] = '1'
    if st.session_state['login'] != "":
        KCXZDM_options = st.multiselect('选择课程性质:',['必修','选修'],['必修'])
        SFXZDM_options = st.multiselect('选择课程性质:',['主修','辅修'],['主修'])
        XQlst = st.session_state['data']['XNXQDM'].unique()
        XQ_options = st.multiselect('请选择学期进行成绩查询:',XQlst,XQlst)
        JF,sub_data = cal_mean(st.session_state['data'], KCXZDM_options, SFXZDM_options, XQ_options)    
        st.text(JF)
        #sub_data[['KCM','ZCJ']]
        JFlst = []
        for i in XQlst:
            JFlst.append(cal_mean(st.session_state['data'],KCXZDM_options,SFXZDM_options,[i])[0])
        st.line_chart(pd.DataFrame(JFlst, XQlst))

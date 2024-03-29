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
    """
    初始化环境，修复webdiver无法运行
    """
    os.system('sbase install geckodriver')
    os.system('ln -s /home/appuser/venv/lib/python3.7/site-packages/seleniumbase/drivers/geckodriver /home/appuser/venv/bin/geckodriver')
    
def get_dict(s):
    """
    将浏览器的headers信息转换为dict
    """
    ans = {}
    for lst in s.split('\n'):
        key, value = lst.split(': ')
        ans[key] = value
    return ans

def crwal_course(cookie):
    """
    考试安排获取函数
    """
    url = "http://ehall.xjtu.edu.cn/jwapp/sys/frReport2/show.do"
    headers = get_dict("""Accept: text/html, */*; q=0.01
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Connection: keep-alive
Host: ehall.xjtu.edu.cn
Referer: http://ehall.xjtu.edu.cn/jwapp/sys/frReport2/show.do?reportlet=wdkb/timeTableForStu10.cpt&XH=2193511382&XNXQDM=2022-2023-1&QUERYID=1a2e60647ae348f9b4b65024af2425ca
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36
X-Requested-With: XMLHttpRequest""")
    data3 = get_dict("""_: 1662526786278
__boxModel__: true
op: page_content
sessionID: 6106
pn: 1""")
    session = requests.session()
    jar = RequestsCookieJar()
    for item in cookie:
        jar.set(item['name'], item['value'])
    session.cookies.update(jar)
    text = session.get(url=url, headers=headers, data=data2).text
    # 数据存储
    course_data = defaultdict(list)
    for mark in json.loads(text)['datas']['jddzpjcxcj']['rows']:
        for item in mark:
            arrange_data[item].append(mark[item])
    arrange_data_frame = pd.DataFrame.from_dict(arrange_data)
#     arrange_data_frame.to_csv("./data_考试安排.csv", encoding="utf-8-sig")
    return arrange_data_frame
  
def crwal_arrange(cookie):
    """
    考试安排获取函数
    """
    url = "http://ehall.xjtu.edu.cn/jwapp/sys/studentWdksapApp/modules/wdksap/wdksap.do"
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
    data2 = get_dict("""XNXQDM: 2021-2022-2
*order: -KSRQ,-KSSJMS""")
    session = requests.session()
    jar = RequestsCookieJar()
    for item in cookie:
        jar.set(item['name'], item['value'])
    session.cookies.update(jar)
    text = session.post(url=url, headers=headers, data=data2).text
    # 数据存储
    arrange_data = defaultdict(list)
    for mark in json.loads(text)['datas']['wdksap']['rows']:
        for item in mark:
            arrange_data[item].append(mark[item])
    arrange_data_frame = pd.DataFrame.from_dict(arrange_data)
#     arrange_data_frame.to_csv("./data_考试安排.csv", encoding="utf-8-sig")
    return arrange_data_frame
  
# 关键字说明  
# JASMC 位置
# KCM 课程名
# KSRQ 考试日期
# XF 学分
# ZJJSXM 老师

def keeptry(xpath):
    """
    重复点击函数
    """
    while True:
        try:
            btn = bro.find_element(By.XPATH, xpath)
            btn.click()
            break
        except:
            continue

def keepfind(xpath):
    """
    重复寻找xpath函数
    """
    while True:
        try:
            btn = bro.find_element(By.XPATH, xpath)
            return btn
        except:
            continue
          
def getMycookies(bro, user, psw):
    """
    获取用户cookies
    """
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
    # 获取课表的另一个cookies
    st.session_state.cookies_course = getMycookies_course(bro)
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
    keeptry('//*[@id="12aa5b5d-3791-4a69-8fda-6e1768da4d97"]')
    # btn4 = bro.find_element(By.XPATH, '//*[@id="12aa5b5d-3791-4a69-8fda-6e1768da4d97"]')
    # btn4.click() #点击后进入了最近两学期的成绩
    time.sleep(0.5)
    cookie = bro.get_cookies()
    jsonCookies = json.dumps(cookie)
    return cookie

def getMycookies_course(bro):
    # 定位到本研课表并点击
    cjcx_str = '//*[@id="widget-hot-01"]/div[1]/widget-app-item[%d]/div/div/div[2]/div[1]'
    start = 1
    cjcx = keepfind(format(cjcx_str) % start)
    while cjcx.text != '我的本研课表':
        start += 1
        cjcx = keepfind(format(cjcx_str) % start)
    cjcx.click()
    window_handles = bro.window_handles
    try:
        bro.switch_to.window(window_handles[1])
    except:
        keeptry('//*[@id="ampDetailEnter"]')
        # temp_btn = bro.find_element(By.XPATH, '//*[@id="ampDetailEnter"]')
        # temp_btn.click()
        window_handles = bro.window_handles
        bro.switch_to.window(window_handles[1])
    # 开始获取cookies
    window_handles = bro.window_handles
    bro.switch_to.window(window_handles[1])
    time.sleep(1)
    cookie = bro.get_cookies()
    jsonCookies = json.dumps(cookie)
    keeptry('//*[@id="down_button"]')
    time.sleep(1)
    window_handles = bro.window_handles
    bro.switch_to.window(window_handles[2])
    time.sleep(1)
    st.session_state.png1 = bro.get_screenshot_as_png()
    bro.close()
    bro.switch_to.window(window_handles[1])
    st.session_state.png2 = bro.get_screenshot_as_png()
    bro.close()
    bro.switch_to.window(window_handles[0])
    return cookie

def crwal_data(cookie):
    """
    成绩获取函数
    """
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
    data = get_dict("""querySetting: [{"name":"XNXQDM","linkOpt":"and","builder":"m_value_equal"},{"name":"XH","linkOpt":"and","builder":"m_value_equal"},{"name":"SFYX","caption":"是否有效","linkOpt":"AND","builderList":"cbl_m_List","builder":"m_value_equal","value":"1","value_display":"是"}]
*order: KCH,KXH
pageSize: 10
pageNumber: 1""")
    # data1 用于获取过去所有成绩
    data1 = get_dict("""querySetting: [{"name":"SFYX","caption":"是否有效","linkOpt":"AND","builderList":"cbl_m_List","builder":"m_value_equal","value":"1","value_display":"是"},{"name":"XNXQDM","builder":"notEqual","linkOpt":"and"}]
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
    """
    平均成绩计算
    """
    data_frame = data[data['XNXQDM'].isin(XQ_options)]
    data_frame = data_frame[data_frame['KCXZDM_DISPLAY'].isin(KCXZDM_options)]
    data_frame = data_frame[data_frame['SFZX_DISPLAY'].isin(SFXZDM_options)]
    ZXF = sum(data_frame['XF'].map(float))
    JF = sum(data_frame['JQCJ']/ZXF)
    return JF, data_frame
  
def getMessage(user,psw):
    cookie = getMycookies(bro)
    data_frame = crwal_data(cookie)
    #['KKDWDM_DISPLAY','XNXQDM','QMCJ','PSCJ','KCM','KCXZDM_DISPLAY','ZCJ','XF','SFZX_DISPLAY']
    st.dataframe(data_frame[['KCM','ZCJ']])
    
def form_callback():
    return
  
if __name__ == "__main__":
    # 初始化
    if 'first_in' not in st.session_state:
      _ = installff()
      st.session_state['first_in']=False
    sslist = ['login', 'data','user','psw','bro']
    st.title("XJTU_")
    for ss in sslist:
        if ss not in st.session_state:
            st.session_state[ss] = ""
    # 是否已登录
    if st.session_state['login']=="":
        url = 'http://ehall.xjtu.edu.cn/new/index.html?browser=no'
        st.text("登录说明：输入密码后，点击回车(或任意空白处)再点击登录")
        if st.session_state.user=="":
          st.session_state.user = st.text_input("账号","")
        else:
          user = st.session_state.user
        if st.session_state.psw=="":
          st.session_state.psw = st.text_input("密码","",type="password")
        else:
          psw = st.session_state.psw
        if st.button("登录"):
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            #chrome_options.add_argument('--disable-gpu')
            bro = webdriver.Chrome(options=chrome_options)
            bro.get(url=url)
            bro.maximize_window()
            st.session_state.bro = bro
            #cookie = getMycookies(bro)
            st.text("正在登录并获取信息，请耐心等待,该过程需要20s左右")
            st.text("正在获取cookie")
            st.session_state.cookie = getMycookies(bro, user, psw)
            st.text("正在获取成绩数据")
            st.session_state['data'] = crwal_data(st.session_state.cookie)
            st.session_state['login'] = '1'
            st.text("查询完毕！")
            st.text(st.session_state.cookie)
            st.text(st.session_state.cookies_course)
            st.text(st.session_state.cookie==st.session_state.cookies_course)
            
            
    # 选择功能
    func_option = st.selectbox("选择你想要的功能", ('请选择','成绩查询', '考试安排', '课表','评教'))
    if st.session_state['login']!="":
        if func_option=="成绩查询":
            st.dataframe(st.session_state['data'][['KCM','ZCJ']])
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
        if func_option=="考试安排":
            if "arrange" not in st.session_state:
              st.session_state['arrange']= crwal_arrange(st.session_state.cookie)
            st.dataframe(st.session_state['arrange'][['JASMC' ,'KCM' ,'KSSJMS' ,'XF' ,'ZJJSXM']])
        if func_option=="评教":
            st.text("开发中")
        if func_option=="课表":
            st.image(st.session_state.png1,caption='课表', use_column_width=True)
            st.image(st.session_state.png2,caption='课表', use_column_width=True)

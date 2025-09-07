import streamlit as st
import requests
import time
from datetime import datetime
import subprocess
import json
import pandas as pd
import re

# 初始化session state
if 'running' not in st.session_state:
    st.session_state.running = False
if 'responses' not in st.session_state:
    st.session_state.responses = []
if 'last_fetch' not in st.session_state:
    st.session_state.last_fetch = 0
if 'interval' not in st.session_state:
    st.session_state.interval = 60
if 'url' not in st.session_state:
    st.session_state.url = "https://tools.connect.aws/endpoint-test/?lng=en&autoRun=true&connectInstanceUrl=https://connect-us-1.my.connect.aws&regions=us-east-1"
if 'latency_data' not in st.session_state:
    st.session_state.latency_data = None


def parse_latency_result(content):
    """解析页面内容中的latencyResult"""
    try:
        # 查找 rawResults div 中的 JSON 数据
        pattern = r'<div id="rawResults">([^<]+)</div>'
        match = re.search(pattern, content)
        if match:
            json_data = json.loads(match.group(1))
            latency_result = json_data.get('latencyResult', {})
            if latency_result.get('status', {}).get('phase') == 'complete':
                return latency_result.get('latencyInstanceRegionItems', [])
    except:
        pass
    return None


def fetch_data():
    """使用Playwright获取React动态生成数据的函数"""
    url = st.session_state.url

    current_time = time.time()
    if current_time - st.session_state.last_fetch >= st.session_state.interval:
        try:
            with st.spinner('正在加载React页面并等待所有结果...'):
                result = subprocess.run([
                    'node', '-e', f'''
                    const {{ chromium }} = require('playwright');
                    (async () => {{
                        const browser = await chromium.launch();
                        const page = await browser.newPage();
                        await page.goto('{url}');
                        await page.waitForSelector('.awsui_root_18wu0_14hyh_93', {{ timeout: 60000 }});
                        await page.waitForTimeout(30000);
                        const content = await page.content();
                        console.log(content);
                        await browser.close();
                    }})();
                    '''
                ], capture_output=True, text=True, timeout=120)

                page_content = result.stdout

                # 解析latency数据
                latency_items = parse_latency_result(page_content)
                if latency_items:
                    st.session_state.latency_data = latency_items

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result = {
                'timestamp': timestamp,
                'status_code': 200,
                'content': page_content
            }
            st.session_state.responses.append(result)
        except Exception as e:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.responses.append({
                'timestamp': timestamp,
                'status_code': 'Error',
                'content': str(e)
            })
        st.session_state.last_fetch = current_time


# Streamlit界面
st.title("Amazon Connect Endpoint测试工具")

# 显示延迟结果表格
if st.session_state.latency_data:
    st.subheader("延迟测试结果")
    df_data = []
    for item in st.session_state.latency_data:
        df_data.append({
            'name': item.get('name', ''),
            'minLatency': item.get('minLatency', 0),
            'maxLatency': item.get('maxLatency', 0),
            'averageLatency': item.get('averageLatency', 0)
        })
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True)

# URL输入框
url_input = st.text_input("URL地址", value=st.session_state.url)
st.session_state.url = url_input

# 时间间隔输入框
interval = st.number_input("时间间隔（秒）", min_value=1, max_value=3600, value=60)
st.session_state.interval = interval

# 按钮布局
col1, col2 = st.columns(2)

with col1:
    if st.button("开始", disabled=st.session_state.running):
        st.session_state.running = True
        st.session_state.responses = []
        st.session_state.last_fetch = 0
        st.success("开始定时访问...")

with col2:
    if st.button("结束", disabled=not st.session_state.running):
        st.session_state.running = False
        st.success("已停止访问")

# 显示状态
if st.session_state.running:
    st.info(f"正在运行中... 每{interval}秒访问一次")
    fetch_data()  # 在主线程中执行
else:
    st.info("已停止")

# 显示响应结果
if st.session_state.responses:
    st.subheader("响应结果")
    # 只显示最近10条
    for i, response in enumerate(reversed(st.session_state.responses[-10:])):
        with st.expander(f"{response['timestamp']} - 状态: {response['status_code']}"):
            st.text_area("响应内容", response['content'], height=200,
                         key=f"response_{i}_{response['timestamp']}")

# 自动刷新页面以显示新数据
if st.session_state.running:
    time.sleep(1)
    st.rerun()

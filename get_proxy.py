# -*- encoding: utf-8 -*-
'''
@File      : get_proxy.py
@Time      : 2020/07/01 22:04:05
@Author    : Reid 
@Version   : 1.0
@Contact   : isreid.zhang@outlook.com
@Desc      : 从网站快代理获取免费的公开代理ip
'''

# here put the import lib

import pandas as pd
import requests
import time
import random
import logging
from faker import Faker
from lxml import etree

faker = Faker()
HEADERS= {'User-Agent':faker.user_agent()}


def timing(func):
    """函数运行计时器
    
    Usage:
    @timing
    def func():
        pass
    """

    def wrapper(*args,**kwargs):
        start = time.time()
        print(f'Function {func.__name__} starts...')
        result = func(*args, **kwargs)
        end = time.time()
        print(f'Function {func.__name__} cost time {round(end-start)} sec')
        return result
    return wrapper


@timing
def get_proxy(url):
    """从网站url 获取免费的公开代理

    :param url: 网站url, 例如https://www.kuaidaili.com/free/inha/{}/
    """

    ips =list()
    ports =list()
    locations =list()
    response_times =list()
    for i in range(1,4000):
        url = url.format(i)
        res = requests.get(url,headers=HEADERS)
        time.sleep(random.randint(2,4))
        html = etree.HTML(res.text)
        table = html.xpath('.//table[@class="table table-bordered table-striped"]')[0]
        rows = table.xpath('./tbody/tr')
        for row in rows:
            ip = row.xpath('td[@data-title="IP"]/text()')[0]
            port = row.xpath('td[@data-title="PORT"]/text()')[0]
            location = row.xpath('td[@data-title="位置"]/text()')[0]
            response_time = row.xpath('td[@data-title="响应速度"]/text()')[0]
            if all([ip,port]):
                # if verify_proxy(ip,port):
                ips.append(ip)
                # print(ips)
                ports.append(port)
                locations.append(location if location else None)
                response_times.append(response_time if response_time else None)

    proxy = pd.DataFrame({
        'IP':ips,
        'Port':ports,
        'Location':locations,
        'Response':response_times
    })
    proxy.to_csv('proxy.csv',index=False,encoding='utf-8')

# @timing
def verify_proxy(ip,port):
    """用ip 代理访问https://www.ipip.net/,  验证ip 是否有效

    :param ip: ip 地址
    :param port: ip 的端口
    :return True/False
    """
    
    server = f'{ip}:{port}'
    proxy = {
        'http': f'http://{server}',
        'https': f'https://{server}'
    }
    try:
        res = requests.get('https://www.ipip.net/', proxies=proxy, headers=HEADERS, timeout=3)
        if res.status_code == 200:
            # print(res.url)
            return True
    except:
        # print('failed')
        return False

@timing
def load_ips(path):
    """从下载的ip中读取数据，验证是否为有效代理
    
    :param path: 结构化的ip 的文件路径
    """
    data = pd.read_csv(path,sep=',',encoding='utf-8')
    for row in data.itertuples():
        ip,port = getattr(row,'IP'), getattr(row,'Port')
        if verify_proxy(ip,port):
            print(ip,port)
        else:
            continue


if __name__ == "__main__":
    url = r'https://www.kuaidaili.com/free/inha/{}/'
    # get_proxy(url)
    load_ips('proxy.csv')
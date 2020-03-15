#!/usr/bin/python
# -*- coding:utf-8 -*-

import urllib
import urllib.request as urllib2
import time
import os
import sys
import json
import logging
import logging.config
import configparser
import optparse
import re
import traceback
from prettytable import PrettyTable
from utils.shell_print_helper import set_font_color, set_stock_digit_color, \
            clean_screen, center_printer, print_dataframe, HIDE_CURSOR, SHOW_CURSOR
import pandas as pd


# API_URL
fund_api_url = "https://fundmobapi.eastmoney.com/FundMApi/FundVarietieValuationDetail.ashx"
stock_api_url = "http://hq.sinajs.cn/list=s_{0}"
stock_outland_api_url = "http://hq.sinajs.cn/list={0}"

# 境外指数
OUTLAND_STOCK = ["int_nasdaq", "int_dji", "int_sp500", "int_hangseng"]

def get(url, data):
    var_list = []
    for k in data.keys():
        var_list.append(k + "=" + str(data[k]))
    url += "?" + "&".join(var_list)
    response = urllib2.urlopen(url)
    return response.read()

def get_fund(fund_id):
    data = {
        "FCODE" : fund_id,
        "deviceid" : "wap",
        "plat" : "Wap",
        "product" : "EFund",
        "version" : "2.0.0"
    }
    return get(fund_api_url, data)

def get_stock(stock_id):
    response = None
    if stock_id not in OUTLAND_STOCK:
        response = urllib2.urlopen(stock_api_url.format(stock_id))
    else:
        response = urllib2.urlopen(stock_outland_api_url.format(stock_id))
    return response.read()

def get_all_fund_data(fund_list):
    fund_data_list = []
    for fund_id in fund_list:
        fund_data_list.append(get_fund(fund_id))
    return fund_data_list

def process_all_fund_data(fund_data_list, buy_fund_pair_list):
    fund_dict_list = []
    desc_dict = {
        "name" : "基金名称",
        "dwjz" : "单位价值",
        "gz" : "估值",
        "gszzl" : "估算涨幅(%)",
        "gssy" : "估算收益",
        "gszz" : "昨日总值",
        "gztime" : "更新时间",
        "total" : "总值"
    }

    fund_dict_list.append(desc_dict)
    for fund_data in fund_data_list:
        fund_data = json.loads(fund_data)
        fund_dict = {}
        try:
            fund_dict["name"] = fund_data["Expansion"]["SHORTNAME"]
            fund_dict["gz"] = fund_data["Expansion"]["GZ"]
            fund_dict["dwjz"] = fund_data["Expansion"]["DWJZ"]
            try:
                if float(fund_data["Expansion"]["GSZZL"]) > 0:
                   fund_data["Expansion"]["GSZZL"] = "+" + fund_data["Expansion"]["GSZZL"]
            except:
                pass
            fund_dict["gszzl"] = fund_data["Expansion"]["GSZZL"]
            fund_dict["gztime"] = fund_data["Expansion"]["GZTIME"]
            fund_dict["total"] = 0
            fund_dict["gssy"] = 0
            fund_dict["gszz"] = 0
            for item in buy_fund_pair_list:
                if item[0] == fund_data["Expansion"]["FCODE"]:
                    fund_dict["total"] = float(item[1]) * float(fund_dict["gz"])
                    fund_dict["gszz"] = float(item[1]) * float(fund_dict["dwjz"])
                    fund_dict["gssy"] = float(item[1]) * (float(fund_dict["gz"]) - float(fund_dict["dwjz"]))
                    break
            fund_dict["total"] = "{0:.2f}".format(fund_dict["total"])
            fund_dict["gssy"] = "{0:.2f}".format(fund_dict["gssy"])
            fund_dict["gszz"] = "{0:.2f}".format(fund_dict["gszz"])
            fund_dict_list.append(fund_dict)
        except:
            pass
    df = pd.DataFrame(map(pd.Series, fund_dict_list[1:]))
    df.columns = list(map(desc_dict.get, df.columns.values))
    return df

def get_all_stock_data(stock_id_list):
    stock_data_list = []
    for stock_id in stock_id_list:
        stock_data_list.append(get_stock(stock_id).decode("gbk"))
    return stock_data_list

def process_all_stock_data(stock_data_list):
    stock_dict_list = []
    desc_dict = {
        "name" : "指数名称",
        "index" : "指数",
        "change" : "涨跌额",
        "rate" : "涨跌幅(%)"
    }
    stock_dict_list.append(desc_dict)

    for stock_data in stock_data_list:
        stock_list = re.search(r"=\"([ \S]*)\"", stock_data).group(1).split(",")
        stock_dict = {}
        stock_dict["name"] = stock_list[0]
        stock_dict["index"] = stock_list[1]
        stock_dict["change"] = stock_list[2]

        stock_list[3] = stock_list[3].replace("%", "")
        if float(stock_list[3]) > 0:
            stock_list[3] = "+" + stock_list[3]
        stock_dict["rate"] = stock_list[3]
        stock_dict_list.append(stock_dict)
    df = pd.DataFrame(map(pd.Series, stock_dict_list[1:]))
    df.columns = list(map(desc_dict.get, df.columns.values))
    return df

def main():
    parser = optparse.OptionParser()
    parser.add_option("-d", "--delay", dest="delay", default=60, type=float)
    (options, args) = parser.parse_args()

    cf = configparser.ConfigParser()
    cf.read("./fund.conf")
    fund_id_list = cf.options("fund")
    stock_id_list = cf.options("stock")
    buy_fund_pair_list = cf.items("buy_fund")

    print(HIDE_CURSOR,)
    last_tick_time = 0

    while True:
        now = time.time()
        if now > last_tick_time + int(options.delay):
            stock_data_list = get_all_stock_data(stock_id_list)
            df_stock = process_all_stock_data(stock_data_list)
            fund_data_list = get_all_fund_data(fund_id_list)
            df_fund = process_all_fund_data(fund_data_list, buy_fund_pair_list)
            clean_screen()
            print(center_printer(time.strftime("%Y-%m-%d %H:%M:%S")))
            print()
            print_dataframe(df_stock, color_columns=['涨跌幅(%)'])
            print()
            print_dataframe(df_fund, color_columns=['估算涨幅(%)'])
            last_tick_time = now
        time.sleep(5)

if __name__ == "__main__":
    main()


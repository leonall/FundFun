#!/usr/bin/python
# -*- coding:utf-8 -*-

from prettytable import PrettyTable
import warnings
import pandas as pd

# 控制字符
CLEAR_SCREEN = "\x1B[2J\x1B[3J\x1B[H" # 清除屏幕内容
RESET = "\x1B[0m"
MAGENTA = "\x1B[35m"
HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"

# shell 颜色
SHELL_COLOR = {
    'RED' : "\x1B[31m",
    'GREEN': "\x1B[32m"
}

def set_font_color(string, color=None):
    if not color or not color.upper() in SHELL_COLOR.keys():
        warnings.warn('color not in {}'.format(list(SHELL_COLOR.keys())))
        return string
    return SHELL_COLOR.get(color.upper(), '') + str(string) + RESET

def set_stock_digit_color(digit):
    try:
        digit = float(digit)
        if digit > 0:
            return set_font_color(str(digit), color='red')
        elif digit < 0:
            return set_font_color(str(digit), color='green')
        else:
            return str(digit)
    except:
        return digit

def clean_screen():
    print(CLEAR_SCREEN)


def center_printer(string):
    reture MAGENTA + string + RESET


def print_dataframe(df, color_columns=[]):
    table = PrettyTable()
    table.field_names = df.columns.values.tolist()
    table.align = 'l'
    if color_columns:
        if len(set(color_columns) & set(table.field_names)) != len(set(color_columns)):
            raise ValueError('color_columns has unknown column name, {}'.format(color_columns))
        for c in color_columns:
            df[c] = df[c].map(set_stock_digit_color)
    for i in range(len(df)):
        table.add_row(df.iloc[i].values)
    print(table)

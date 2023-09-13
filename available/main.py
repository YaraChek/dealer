#!/usr/bin/env python3.11

"""
The script indicates which item from the processed price list is in the supplier's main warehouse
"""

import pandas as pd
import datetime
from tqdm import tqdm

DATE_LABEL = datetime.datetime.now().strftime("%Y-%m-%d")


def is_number(arg):
    """Checks if the input is an integer"""
    while True:
        try:
            arg = int(arg)
            return arg
        except ValueError:
            print('Введіть число, будь ласка:')
            arg = input()


def to_continue(arg1, arg2):
    """Clarifies the response from the user if necessary"""
    while True:
        res = input()
        if res in arg1 | arg2:
            return res
        else:
            print('Виберіть "yes" або "no" - y/n')


def stock_availability(name):
    """
    Reads supplier's file, forms pandas DataFrame, items are converts to type "str"
    :param name: goods on supplier's stores (*.xls or *.xlsx)
    :return: items in stock at the supplier's main warehouse (set)
    """
    print('Робота з файлом залишків:')
    goods_df = pd.read_excel(name, index_col=0, skiprows=2)
    items = {str(goods_df.index[i]).strip("'") for i in tqdm(range(goods_df.shape[0])) if
             str(goods_df.values[i][1]).strip() != 'nan'}
    return items


def prepare_customer_price(cust_price):
    """
    Reads dealers price list, forms pandas DataFrame, items are converts to type "str"
    :param cust_price: dealers price list (file MS Excel or OpenDocument Spreadsheets)
    :return: dealers price list (pandas DataFrame)
    """
    print('Який номер стовпчика з артикулами у Вашому прайсі?')
    number = input()
    column = is_number(number) - 1
    print(f'Читання з файла "{cust_price}":')
    cust_price = pd.read_excel(cust_price)

    cust_price[cust_price.columns[column]] = \
        [str(name).strip("' ") for name in tqdm(cust_price[cust_price.columns[column]])]
    cust_price.loc[cust_price[cust_price.columns[column]] == 'nan', cust_price.columns[column]] = ''
    cust_price.set_index(cust_price.columns[column], inplace=True)
    return cust_price


def avail(items, price_df):
    """
    Uses dealer's price list, adds column "Availability"
    :param items: set of the items from the supplier's central warehouse (set)
    :param price_df: dealer's price list (DataFrame)
    :return: pandas DataFrame for the resulting xlsx-file
    """
    print('Перевірка наявності на центральному складі:')
    pbar = tqdm(range(price_df.shape[0]))
    price_df['Наявність'] = ['+' if price_df.index[i] in items else '-'
                             for i in pbar]
    return price_df


def main():
    print('''
Ця програма створює копію Вашого прайсу (xls-, xlsx-, ods-формату) додавши стовпчик "Наявність"
(або відкоригувавши його, якщо він вже є). Маркується знаком "+" позиція, що є на центральному
складі постачальника, знаком "-" - якої нема.
''')
    print('Перетягніть файл залишків у командний рядок. Або введіть його імʼя'
          '(з зазначенням шляху до файла, якщо він не в теці з програмою).')
    goods_file = input().strip(" '")
    goods = stock_availability(goods_file)

    while True:
        print('\nПеретягніть Ваш файл (прайс) у командний рядок. Або введіть його імʼя'
              '(з зазначенням шляху до файла, якщо він не в теці з програмою).')
        customer_price_name = input().strip(" '")
        customer_price = prepare_customer_price(customer_price_name)

        output_filename = '_'.join((customer_price_name[:-4], DATE_LABEL)) + '.xlsx'
        avail(goods, customer_price).to_excel(output_filename)

        positive = {'y', 'yes', 'так'}
        negative = {'n', 'no', 'ні'}

        print('\nОбробити ще файл? Y/n:', end=' ')
        ans = to_continue(positive, negative)
        if ans.lower() in negative:
            print('\nПрограма завершена\n')
            exit()


main()

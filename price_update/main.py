#!/usr/bin/env python3

"""
The program receives 3+ files as input:
1. goods in the supplier's warehouses;
2. the current supplier's price list;
2. custom price list(s).

The program does:
1. indicates which product from the user price list is in the supplier's main warehouse;
2. updates prices, marks goods as "Sale", "Promo" etc., saves a copy of updated user's price list.
"""

import pandas as pd
import numpy as np
import datetime
from tqdm import tqdm

DATE_LABEL_FOR_FILENAME = datetime.datetime.now().strftime("%Y-%m-%d")
DATE_LABEL_FOR_COLUMNNAME = datetime.datetime.now().strftime("%d.%m.%Y")


def greetings():
    print('''
Ця програма створена для оновлення прайса (прайсів) дилера в форматі MS Excel або 
OpenDocument Spreadsheets.
Вона читає 2 файли постачальника, які Ви їй надаєте:
   1. Файл залишків на складі постачальника.
   2. Актуальний прайс постачальника.
Читає Ваш прайс в xls-, xlsx- або ods-форматі.
Аналізує їх, потім зберігає копію прайса дилера з деякими змінами:
   1. Програма створює стовпчик з актуальними на сьогоднішній день цінами.
   2. Якщо на товар актуальна акційна пропозиція - в прайс додається стовпчик с датами її
закінчення.
   3. Якщо товар сьогодні в розпродажу - додается стовпчик "Розпродаж", а відповідні товари -
маркуються.
   4. Останнім додається стовпчик, де позначається знаком "+" наявність товару на центральному
складі постачальника, а знаком "-" - відсутність. 
''')
    print('''В теці з програмою є файл "config.xls".
Перед виконанням програми - подивіться його, якщо потрібно - змініть/заповніть комірки:
   1. Імена файлів.
   2. Номери рядків і стовпчиків.
Якщо зараз у "config.xls" все як треба - введіть "y" (мається на увазі "YES") та програма почне
виконання.
Якщо "config.xls" потребує змін, введіть "n" (це - "NO"), правильно заповніть "config.xls",
обов'язково збережіть, запустіть програму знов.

Бекап файлу "config.xls" має ім'я "config.xls.bak". Якщо в "config.xls" щось раптом "зламається" -
знаєте як повернутися до робочої версії.
''')


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


def global_price_list(current_price, conf_df):
    """
    Reads the supplier's current price list by sheets, forms a common pandas DataFrame
    :param current_price: current supplier's price list (*.xls or *.xlsx)
    :param conf_df: config file with information about filenames, needed columns & rows (DataFrame)
    :return: supplier's current price list (DataFrame)
    """
    table_header = conf_df.loc['table_header']['Індекс']
    standard_price = conf_df.loc['standard_price']['Індекс']
    quart_price = conf_df.loc['quart_price']['Індекс']
    month_price = conf_df.loc['month_price']['Індекс']
    quart_promo_date = conf_df.loc['quart_promo_date']['Індекс']
    month_promo_date = conf_df.loc['month_promo_date']['Індекс']

    sheets = pd.ExcelFile(current_price).sheet_names
    if 'Стенди' in sheets:
        sheets.remove('Стенди')
    df_list = []
    progr_bar = tqdm(sheets)
    for name in progr_bar:
        if name == 'Акції':
            prices = pd.read_excel(current_price, skiprows=table_header,
                                   sheet_name=name).iloc[:, [0, quart_price, quart_promo_date]]
            prices[prices.columns[0]] = \
                [str(name).strip("' ") for name in prices[prices.columns[0]]]
            prices.columns = ['Артикул', 'Ціна з ПДВ, грн', 'Термін акції до']
            prices.set_index(prices.columns[0], inplace=True)
            if 'nan' in prices.index:
                prices = prices.drop(index='nan')
            df_list.append(prices)
        elif name == 'Ціна місяця':
            prices = pd.read_excel(current_price, skiprows=table_header,
                                   sheet_name=name).iloc[:, [0, month_price, month_promo_date]]
            prices.columns = ['Артикул', 'Ціна з ПДВ, грн', 'Термін акції до']
            prices[prices.columns[0]] = \
                [str(name).strip("' ") for name in prices[prices.columns[0]]]
            prices.set_index(prices.columns[0], inplace=True)
            if 'nan' in prices.index:
                prices = prices.drop(index='nan')
            df_list.append(prices)
        elif name == 'Розпродаж':
            prices = pd.read_excel(current_price, skiprows=table_header,
                                   sheet_name=name).iloc[:, [0, standard_price + 1]]

            prices.columns = ['Артикул', 'Ціна з ПДВ, грн']
            prices[prices.columns[0]] = \
                [str(name).strip("' ") for name in prices[prices.columns[0]]]
            prices.set_index(prices.columns[0], inplace=True)
            if 'nan' in prices.index:
                prices = prices.drop(index='nan')
            prices['Ціна з ПДВ, грн'] = round(prices['Ціна з ПДВ, грн'], 2) * 1.2
            prices['Розпродаж'] = 'Розпродаж'
            df_list.append(prices)
        else:
            prices = pd.read_excel(current_price, skiprows=table_header,
                                   sheet_name=name).iloc[:, [0, standard_price]]
            prices[prices.columns[0]] = \
                [str(name).strip("' ") for name in prices[prices.columns[0]]]
            prices.dropna(subset=['Артикул'])
            prices.columns = ['Артикул', 'Ціна з ПДВ, грн']
            prices.set_index(prices.columns[0], inplace=True)
            if 'nan' in prices.index:
                prices = prices.drop(index='nan')
            df_list.append(prices)
        progr_bar.set_description("Опрацьовано аркушів")
    return pd.concat(df_list)  # , verify_integrity=True


def prepare_goods(goods_xls):
    """
    Reads supplier's file, forms pandas DataFrame, items are converts to type "str"
    :param goods_xls: goods on supplier's stores (*.xls or *.xlsx)
    :return: items in stock at the supplier's main warehouse (set)
    """
    print('Робота з файлом залишків:')
    goods_df = pd.read_excel(goods_xls, index_col=0, skiprows=2)
    items = {str(goods_df.index[i]).strip("'") for i in tqdm(range(goods_df.shape[0])) if
             str(goods_df.values[i][1]).strip() != 'nan'}
    return items


def prepare_customer_price(cust_price, column, line):
    """
    Reads dealers price list, forms pandas DataFrame, items are converts to type "str"
    :param cust_price: dealers price list (file MS Excel or OpenDocument Spreadsheets)
    :param column: column for indexes
    :param line: row with column names
    :return: dealers price list (pandas DataFrame)
    """
    print(f'Робота з файлом "{cust_price}":')
    cust_price = pd.read_excel(cust_price, skiprows=line)
    cust_price[cust_price.columns[column]] = \
        [str(name).strip("' ") for name in tqdm(cust_price[cust_price.columns[column]])]
    cust_price.loc[cust_price[cust_price.columns[column]] == 'nan', cust_price.columns[column]] = ''
    cust_price.set_index(cust_price.columns[column], inplace=True)
    return cust_price


def update_price(glob_price, dealers_price, date):
    """
    Adds the current price column to the dealer's price list
    :param glob_price: current supplier's price list (DataFrame)
    :param dealers_price: dealer's price list (DataFrame)
    :param date: current date
    :return: updated dealer's price list (DataFrame)
    """
    print(f'Додавання цін за {date}:')
    glob_items = glob_price.index
    for item in tqdm(dealers_price.index):
        dealers_price.loc[item, ['Ціна ' + date]] = glob_price.loc[item]['Ціна з ПДВ, грн'] \
            if item in glob_items else '-'
    return dealers_price


def update_promo(glob_price, dealers_price):
    """
    Checks if there are promotional goods in the dealer's price list
    :param glob_price: current supplier's price list (DataFrame)
    :param dealers_price: dealer's price list (DataFrame)
    :return: updated dealer's price list (DataFrame)
    """
    print('Перевірка акційних пропозицій:')
    for item in tqdm(dealers_price.index):
        if item in glob_price.index:
            if glob_price.loc[item]['Термін акції до'] != np.nan:
                dealers_price.loc[item, ['Термін акції до']] = \
                    glob_price.loc[item]['Термін акції до']
    return dealers_price


def update_sale(glob_price, dealers_price):
    """
    Checks if the dealer's price list contains sale items
    :param glob_price: current supplier's price list (DataFrame)
    :param dealers_price: dealer's price list (DataFrame)
    :return: updated dealer's price list (DataFrame)
    """
    print('Перевірка пропозицій розпродажу:')
    for item in tqdm(dealers_price.index):
        if item in glob_price.index:
            if glob_price.loc[item]['Розпродаж'] != np.nan:
                dealers_price.loc[item, ['Розпродаж']] = glob_price.loc[item]['Розпродаж']
    return dealers_price


def avail(items, price_df):
    """
    Uses dealer's price list, adds column "Availability"
    :param items: set of the items from the supplier's central warehouse
    :param price_df: dealer's price list (DataFrame)
    :return: pandas DataFrame for the resulting xlsx-file
    """
    print('Перевірка наявності на центральному складі:')
    price_df['Наявність'] = ['+' if str(price_df.index[i]).strip("'") in items else '-'
                             for i in tqdm(range(price_df.shape[0]))]
    return price_df


def main():
    config = pd.read_excel('config.xls', index_col=0, skiprows=4)
    config = config.convert_dtypes()
    goods = config.loc['goods']['Значення']
    goods = prepare_goods(goods)
    supplier_price_list = config.loc['current_price']['Значення']

    print('Зачекайте, будь ласка: програма працює з прайсом постачальника.')

    supplier_price_list = global_price_list(supplier_price_list, config)

    while True:
        print('\nПеретягніть Ваш файл (прайс) у командний рядок. Або введіть його імʼя'
              '(з зазначенням шляху до файла, якщо він не в теці з програмою).')
        customer_price_name = input().strip(" '")

        print('\nВводьте, будь ласка, числа та натискайте <Enter>.\n')
        print('Який номер стовпчика з артикулами у Вашому прайсі?')
        number = input()
        items_column = is_number(number) - 1

        print('У якому рядку Вашого прайсу найменування стовпчиків ("Артикул", "Ціна", тощо)?')
        number = input()
        first_row = is_number(number) - 1

        print('\nЗачекайте, будь ласка: програма працює з файлами.\n')

        customer_price = prepare_customer_price(customer_price_name, items_column, first_row)
        customer_price = update_price(supplier_price_list, customer_price,
                                      DATE_LABEL_FOR_COLUMNNAME)
        customer_price = update_promo(supplier_price_list, customer_price)
        customer_price = update_sale(supplier_price_list, customer_price)
        customer_price = avail(goods, customer_price)

        filename = '_'.join((customer_price_name[:-4], DATE_LABEL_FOR_FILENAME))
        customer_price.to_excel(filename + '.xlsx')
        print(f'Оновлений прайс --> {filename}')

        positive = {'y', 'yes', 'так'}
        negative = {'n', 'no', 'ні'}

        print('\nОбробити ще файл? Y/n:', end=' ')
        ans = to_continue(positive, negative)
        if ans.lower() in negative:
            print('\nПрограма завершена\n')
            exit()


if __name__ == "__main__":
    greetings()
    yes = {'y', 'yes', 'так'}
    no = {'n', 'no', 'ні'}
    print('Далі? Y/n:', end=' ')
    answer = to_continue(yes, no)
    if answer.lower() in yes:
        print('''
Будьте уважні, програма час від часу буде Вас питати про номери рядків і стовпчиків у Вашому
прайсі, який буде оброблятися. Рядки - не так важливі: вкажете менше (хоч і від'ємне число -
прайс буде оброблятися з першого рядочка, вкажете більше - буде оброблено не весь прайс.
А от СТОВПЧИКИ - конче ВАЖЛИВІ: буде зазначено не той стовпчик - програма не "підхопить" артикули.
''')
        main()
    else:
        exit()

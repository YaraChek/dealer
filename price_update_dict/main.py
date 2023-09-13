#!/usr/bin/env python3.11

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


def read_suppliers_price(params):
    """Reads specified sheet from specified file. Cleans data."""
    filename, cur_sheet, price_column, line = params
    print(f'Опрацювання аркушу "{cur_sheet}"')
    df = pd.read_excel(filename, skiprows=line, sheet_name=cur_sheet)
    # prepare the dataframe for deleting rows containing products with an ambiguous price
    dimension = df.shape[0]
    df[price_column] = [0 if (type(df.iloc[i][price_column]) is str or df.iloc[i][price_column] ==
                              np.nan) else df.iloc[i][price_column] for i in range(dimension)]
    # deleting rows containing products without a price
    df = df.loc[df[price_column] != 0]
    # deleting rows contains empty SKU's value
    df = df.loc[df[df.columns[0]] != np.nan]
    return df


def dictionary_creation(params):
    """Final stage converting original xlsx-file to dict"""
    df, cur_price, date, sale = params
    dimension = df.shape[0]
    pbar = tqdm(range(dimension))
    if date:
        date = df.columns[date]
    cur_dict = {str(df.iloc[i][df.columns[0]]): {'price': round(df.iloc[i][cur_price] * 1.2, 2)
    if sale else df.iloc[i][cur_price], 'date': df.iloc[i][date] if date else None}
                for i in pbar}
    res_dict = {df.iloc[i][df.columns[0]]: {'price': round(df.iloc[i][cur_price] * 1.2, 2)
    if sale else df.iloc[i][cur_price], 'date': df.iloc[i][date] if date else None}
                for i in pbar if type(df.iloc[i][df.columns[0]]) is int}
    return cur_dict, res_dict


def global_price_list(current_price, conf_df):
    """
    Reads the supplier's current price list by sheets, forms a common pandas DataFrame
    :param current_price: current supplier's price list (*.xls or *.xlsx)
    :param conf_df: config file with information about filenames, needed columns & rows (DataFrame)
    :return: supplier's current price list (dict)
    """
    promosheet_1 = conf_df.loc['promosheet_1']['Значення']
    promosheet_2 = conf_df.loc['promosheet_2']['Значення']
    sale_sheet = conf_df.loc['sale_sheet']['Значення']
    stand_sheet = conf_df.loc['stand_sheet']['Значення']
    table_header = conf_df.loc['table_header']['Індекс']
    standard_price = conf_df.loc['standard_price']['Індекс']
    promo_price = conf_df.loc['promo_price']['Індекс']
    month_price = conf_df.loc['month_price']['Індекс']
    promo_date = conf_df.loc['promo_date']['Індекс']
    month_promo_date = conf_df.loc['month_promo_date']['Індекс']

    global_dict = {}
    reserve_dict = {}

    sheets = pd.ExcelFile(current_price).sheet_names
    for _ in {promosheet_1, promosheet_2, sale_sheet, stand_sheet}:
        sheets.remove(_)

    # Standard
    for sheet in sheets:
        args = (current_price, sheet, standard_price, table_header)
        prices = read_suppliers_price(args)

        args = (prices, standard_price, None, None)
        full_price_list, numeric_price_list = dictionary_creation(args)
        global_dict.update(full_price_list)
        reserve_dict.update(numeric_price_list)

    # Sale
    args = (current_price, sale_sheet, standard_price + 1, table_header)
    prices = read_suppliers_price(args)
    args = (prices, promo_price + 1, None, True)
    full_price_list, numeric_price_list = dictionary_creation(args)
    for_sale = set(full_price_list.keys())
    global_dict.update(full_price_list)
    reserve_dict.update(numeric_price_list)

    # Promo 1
    args = (current_price, promosheet_1, promo_price, table_header)
    prices = read_suppliers_price(args)
    args = (prices, promo_price, promo_date, None)
    full_price_list, numeric_price_list = dictionary_creation(args)
    global_dict.update(full_price_list)
    reserve_dict.update(numeric_price_list)

    # Promo 2
    args = (current_price, promosheet_2, month_price, table_header)
    prices = read_suppliers_price(args)
    args = (prices, month_price, month_promo_date, None)
    full_price_list, numeric_price_list = dictionary_creation(args)
    global_dict.update(full_price_list)
    reserve_dict.update(numeric_price_list)

    return global_dict, reserve_dict, for_sale


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


def prepare_customer_price(cust_price):
    """
    Reads dealers price list, forms pandas DataFrame, items are converts to type "str"
    :param cust_price: dealers price list (file MS Excel or OpenDocument Spreadsheets)
    :return: dealers price list (pandas DataFrame)
    """
    print('\nВводьте, будь ласка, числа та натискайте <Enter>.\n')
    print('Який номер стовпчика з артикулами у Вашому прайсі?')
    number = input()
    column = is_number(number) - 1

    print('У якому рядку Вашого прайсу найменування стовпчиків ("Артикул", "Ціна", тощо)?')
    number = input()
    line = is_number(number) - 1

    print('\nЗачекайте, будь ласка: програма працює з файлами.\n')
    print(f'Читання з файла "{cust_price}":')
    cust_price = pd.read_excel(cust_price, skiprows=line)

    cust_price[cust_price.columns[column]] = \
        [str(name).strip("' ") for name in tqdm(cust_price[cust_price.columns[column]])]
    cust_price.loc[cust_price[cust_price.columns[column]] == 'nan', cust_price.columns[column]] = ''
    cust_price.set_index(cust_price.columns[column], inplace=True)
    return cust_price


def update_price(glob_price, dealers_price, glob_items, date):
    """
    Adds the current price column to the dealer's price list
    :param glob_price: current supplier's price list (dict)
    :param dealers_price: dealer's price list (DataFrame)
    :param date: current date
    :param glob_items: SKUs from current supplier's price list (set)
    :return: updated dealer's price list (DataFrame)
    """
    print(f'Додавання цін за {date}:')
    pbar = tqdm(dealers_price.index)
    dealers_price['Ціна ' + date] = [glob_price[item]['price'] if item in glob_items else '-'
                                     for item in pbar]


def update_promo(glob_price, dealers_price, items):
    """
    Checks if there are promotional goods in the dealer's price list
    :param glob_price: current supplier's price list (dict)
    :param dealers_price: dealer's price list (DataFrame)
    :param items: SKUs from current supplier's price list (set)
    :return: updated dealer's price list (DataFrame)
    """
    print('Перевірка акційних пропозицій:')
    pbar = tqdm(dealers_price.index)
    dealers_price['Термін акції до'] = [glob_price[item]['date'] if item in items else ''
                                        for item in pbar]


def update_sale(dealers_price, items):
    """
    Checks if the dealer's price list contains sale items
    :param dealers_price: dealer's price list (DataFrame)
    :param items: SKUs in the sale offer
    :return: updated dealer's price list (DataFrame)
    """
    print('Перевірка пропозицій розпродажу:')
    pbar = tqdm(dealers_price.index)
    dealers_price['Розпродаж'] = ['Розпродаж' if item in items else '' for item in pbar]


def avail(items, price_df, date, digital_skus):
    """
    Uses dealer's price list, adds column "Availability" and corrects the price column in case of
    incorrect entries of digital SKUs in the supplier's price list
    :param items: set of the items from the supplier's central warehouse (set)
    :param price_df: dealer's price list (DataFrame)
    :param date: current date
    :param digital_skus: digital SKUs from the supplier's price list (dict)
    :return: pandas DataFrame for the resulting xlsx-file
    """
    print('Перевірка наявності на центральному складі:')
    pbar = tqdm(range(price_df.shape[0]))
    price_df['Наявність'] = ['+' if price_df.index[i] in items else '-'
                             for i in pbar]
    price_df.loc[(price_df['Наявність'] == '+') & (price_df['Ціна ' + date] == '-'),
                 'Ціна ' + date] = 'Постачальник не надає ціну'
    if 'Постачальник не надає ціну' in price_df['Ціна ' + date].values:
        price_df['Ціна ' + date] = [digital_skus[int(price_df.index[i])]['price']
                                    if price_df.index[i].isdigit()
                                       and int(price_df.index[i]) in digital_skus
                                    else price_df['Ціна ' + date][i] for i in pbar]


def main():
    config = pd.read_excel('config.xls', index_col=0, skiprows=4)
    config = config.convert_dtypes()
    goods = config.loc['goods']['Значення']
    goods = prepare_goods(goods)
    supplier_price_list = config.loc['current_price']['Значення']

    print('Зачекайте, будь ласка: програма працює з прайсом постачальника.')

    supplier_price_list, num_skus, sale = global_price_list(supplier_price_list, config)
    skus = set(supplier_price_list.keys())

    while True:
        print('\nПеретягніть Ваш файл (прайс) у командний рядок. Або введіть його імʼя'
              '(з зазначенням шляху до файла, якщо він не в теці з програмою).')
        customer_price_name = input().strip(" '")

        customer_price = prepare_customer_price(customer_price_name)

        update_price(supplier_price_list, customer_price, skus,
                     DATE_LABEL_FOR_COLUMNNAME)
        update_promo(supplier_price_list, customer_price, skus)
        update_sale(customer_price, sale)
        avail(goods, customer_price, DATE_LABEL_FOR_COLUMNNAME, num_skus)

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

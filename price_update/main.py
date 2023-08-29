#!/usr/bin/env python3

"""
The program receives 3 files as input:
1. goods in the supplier's warehouses;
2. the current supplier's price list;
2. custom price list.

The program does:
1. indicates which product from the user price list is in the supplier's main warehouse;
2. updates prices, marks goods as "Sale", "Promo" etc., saves a copy of updated user's price list.
"""

import pandas as pd
import numpy as np
import datetime

DATE_LABEL_FOR_FILENAME = datetime.datetime.now().strftime("%Y-%m-%d")
DATE_LABEL_FOR_COLUMNNAME = datetime.datetime.now().strftime("%d.%m.%Y")


def greetings():
    print('''
Ця програма створена для оновлення прайса (прайсів) дилера в форматі MS Excel.
Вона читає 2 файли постачальника, які Ви їй надаєте:
   1. Файл залишків на складі постачальника.
   2. Актуальний прайс постачальника.
Вона читає Ваш прайс в xls-, xlsx- або ods-форматі.
Аналізує їх, потім зберігає копію прайса дилера з деякими змінами:
   1. Програма створює стовпчик з актуальними на сьогоднішній день цінами.
   2. Якщо на товар актуальна акційна пропозиція - в прайс додається стовпчик с датами її
закінчення.
   3. Якщо товар сьогодні в розпродажу - додается стовпчик "Розпродаж". Відповідні товари -
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
    while True:
        try:
            arg = int(arg)
            return arg
        except ValueError:
            print('Введіть число, будь ласка:')
            arg = input()


def to_continue(arg1, arg2):
    while True:
        res = input()
        if res in arg1 | arg2:
            return res
        else:
            print('Виберіть "yes" або "no" - y/n')


def avail(goods_xls, price_df):
    """
    Uses dealer's price list, adds column "Availability"
    :param goods_xls: supplier's inventory file
    :param price_df: dealer's price list (DataFrame)
    :return: pandas DataFrame for the resulting xlsx-file
    """
    items = pd.read_excel(goods_xls, index_col=0, skiprows=2)
    items = {items.index[i] for i in range(items.shape[0]) if items.values[i][1] != np.nan}
    price_df['Наявність'] = \
        ['+' if price_df.index[i] in items else '-' for i in range(price_df.shape[0])]
    return price_df


def global_price_list(current_price, conf_df):
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
    for name in sheets:
        if name == 'Акції':
            prices = pd.read_excel(current_price, index_col=0, skiprows=table_header,
                                   sheet_name=name).iloc[:, [quart_price, quart_promo_date]]
            if np.nan in prices.index:
                prices = prices.drop(index=np.nan)
            prices.columns = ['Ціна з ПДВ, грн', 'Термін акції до']
            df_list.append(prices)
        elif name == 'Ціна місяця':
            prices = pd.read_excel(current_price, index_col=0, skiprows=table_header,
                                   sheet_name=name).iloc[:, [month_price, month_promo_date]]
            if np.nan in prices.index:
                prices = prices.drop(index=np.nan)
            prices.columns = ['Ціна з ПДВ, грн', 'Термін акції до']
            df_list.append(prices)
        elif name == 'Розпродаж':
            prices = pd.read_excel(current_price, index_col=0, skiprows=table_header,
                                   sheet_name=name).iloc[:, [standard_price + 1]]
            if np.nan in prices.index:
                prices = prices.drop(index=np.nan)
            prices.columns = ['Ціна з ПДВ, грн']
            prices['Ціна з ПДВ, грн'] = round(prices['Ціна з ПДВ, грн'], 2) * 1.2
            prices['Розпродаж'] = 'Розпродаж'
            df_list.append(prices)
        else:
            prices = pd.read_excel(current_price, index_col=0, skiprows=table_header,
                                   sheet_name=name).iloc[:, [standard_price]]
            prices = prices.drop(index=np.nan) if np.nan in prices.index else prices
            prices.columns = ['Ціна з ПДВ, грн']
            df_list.append(prices)

    return pd.concat(df_list)


def update_price(glob_price, dealers_price, date):
    glob_items = glob_price.index
    for item in dealers_price.index:
        dealers_price.loc[item, ['Ціна ' + date]] = glob_price.loc[item]['Ціна з ПДВ, грн'] \
            if item in glob_items else '-'
    return dealers_price


def update_promo(glob_price, dealers_price):
    for item in dealers_price.index:
        if item in glob_price.index:
            if glob_price.loc[item]['Термін акції до'] != np.nan:
                dealers_price.loc[item, ['Термін акції до']] = \
                    glob_price.loc[item]['Термін акції до']
    return dealers_price


def update_sale(glob_price, dealers_price):
    for item in dealers_price.index:
        if item in glob_price.index:
            if glob_price.loc[item]['Розпродаж'] != np.nan:
                dealers_price.loc[item, ['Розпродаж']] = glob_price.loc[item]['Розпродаж']
    return dealers_price


def main():
    config = pd.read_excel('config.xls', index_col=0, skiprows=4)
    config = config.convert_dtypes()
    goods = config.loc['goods']['Значення']
    supplier_price_list = config.loc['current_price']['Значення']

    print('Зачекайте, будь ласка: програма працює з файлами.')

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
        customer_price = pd.read_excel(customer_price_name, index_col=items_column,
                                       skiprows=first_row)

        print('\nЗачекайте, будь ласка: програма працює з файлами.\n')

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

        print('\nОбробити ще файл? Y/n:')
        ans = to_continue(positive, negative)
        if ans.lower() in negative:
            print('\nПрограма завершена\n')
            exit()


if __name__ == "__main__":
    greetings()
    right_answers = {'y', 'yes', 'так'}
    answer = input('Далі? Y/n: ')
    if answer.lower() in right_answers:
        print('''
Будьте уважні, програма час від часу буде Вас питати про номери рядків і стовпчиків у Вашому
прайсі, який буде оброблятися. Рядки - не так важливі: вкажете менше (хоч і від'ємне число -
прайс буде оброблятися з першого рядочка, вкажете більше - буде оброблено не весь прайс.
А от СТОВПЧИКИ - конче ВАЖЛИВІ: буде зазначено не той стовпчик - програма не "підхопить" артикули.
''')
        main()
    else:
        exit()

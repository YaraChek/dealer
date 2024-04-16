#!/usr/bin/env python3.12

"""
The program analyzes the supplier's multi-sheet price list (xls-, xlsx- or ods-file).
Selects retail prices, promotional prices, sale prices. Generates wholesale prices for resale.
"""

import pandas as pd
import datetime
from tqdm import tqdm
from math import ceil

DATE = datetime.datetime.now().strftime("%d.%m.%Y")
COLUMN_NAMES = ('Артикул',
                'Наявність на ' + DATE,
                'ТМЦ',
                'Роздрібна ціна стандартна',
                'Роздр. акційна ціна',
                'Вхідна ціна субдилера',
                'Акція / Розпродаж',
                'Дата закінчення акції')


def prepare_goods(goods_xls):
    """
    Reads supplier's file, forms pandas DataFrame, items are converts to type "str"
    :param goods_xls: goods on supplier's stores (*.xls or *.xlsx)
    :return: items in stock at the supplier's main warehouse (set)
    """
    print('Робота з файлом залишків')
    goods_df = pd.read_excel(goods_xls, index_col=0, skiprows=2)
    items = {str(goods_df.index[i]).strip("'") for i in tqdm(range(goods_df.shape[0])) if
             str(goods_df.values[i][1]).strip() != 'nan'}
    return items


def result(goods_dict, column_names):
    """
    Prepare DataFrame for writing final xlsx-file.
    :param goods_dict: dictionary, where keys are SKUs, values are goods, marks and prices
    :param column_names: table column names
    :return: DataFrame for writing final xlsx-file
    """
    df = pd.DataFrame(columns=column_names)
    print('Формування вихідного файлу')
    for name in column_names:
        df[name] = [goods_dict[sku][name] for sku in goods_dict.keys()]
    df.set_index(df.columns[0], inplace=True)
    return df


def main():
    config = pd.read_excel('config.xls', index_col=0, skiprows=4)
    config = config.convert_dtypes()

    current_price_file = config.loc['current_price']['Значення']
    table_header = config.loc['table_header']['Індекс']
    standard_price = config.loc['standard_price']['Індекс']
    promo_price = config.loc['promo_price']['Індекс']
    promo_date = config.loc['promo_date']['Індекс']
    goods_file = config.loc['goods']['Значення']
    goods = prepare_goods(goods_file)
    sheets = config.loc['sheetnames']['Значення'].split(', ')

    final_dict = {}
    print('Робота з прайсом постачальника')
    pbar = tqdm(sheets)
    for sheet in pbar:
        df = pd.read_excel(current_price_file, skiprows=table_header, sheet_name=sheet)
        dimension = range(df.shape[0])
        for i in dimension:
            if sheet.startswith('Акц'):  # Акції
                entry_price = df.iloc[i][promo_price + 2]
                promo = df.iloc[i][promo_price]
                quotient = entry_price / promo
                if quotient <= 0.8:
                    subdealer = ceil(promo * 90) / 100
                elif 0.8 < quotient <= 0.86:
                    subdealer = ceil(entry_price * 111.753) / 100
                else:
                    subdealer = promo

                key = str(df.iloc[i][0])
                final_dict.setdefault(key, {
                    'Артикул': key,
                    'Наявність на ' + DATE: '+' if key in goods else '-',
                    'ТМЦ': str(df.iloc[i][1]).strip("' "),
                    'Роздрібна ціна стандартна': df.iloc[i][promo_price + 1],
                    'Роздр. акційна ціна': promo,
                    'Вхідна ціна субдилера': subdealer,
                    'Акція / Розпродаж': 'Акція',
                    'Дата закінчення акції': df.iloc[i][promo_date]})
            elif sheet.startswith('Розпрод'):  # Розпродаж
                key = str(df.iloc[i][0])
                final_dict.setdefault(key, {
                    'Артикул': key,
                    'Наявність на ' + DATE: '+' if key in goods else '-',
                    'ТМЦ': str(df.iloc[i][1]).strip("' "),
                    'Роздрібна ціна стандартна': df.iloc[i][standard_price],
                    'Роздр. акційна ціна': None,
                    'Вхідна ціна субдилера': round(df.iloc[i][standard_price + 1] * 1.2, 2),
                    'Акція / Розпродаж': 'Розпродаж',
                    'Дата закінчення акції': None})
            else:
                key = str(df.iloc[i][0])
                final_dict.setdefault(key, {
                    'Артикул': key,
                    'Наявність на ' + DATE: '+' if key in goods else '-',
                    'ТМЦ': str(df.iloc[i][1]).strip("' "),
                    'Роздрібна ціна стандартна': df.iloc[i][standard_price],
                    'Роздр. акційна ціна': None,
                    'Вхідна ціна субдилера': ceil(df.iloc[i][standard_price] * 90) / 100,
                    'Акція / Розпродаж': None,
                    'Дата закінчення акції': None})
            pbar.set_description('Обробка аркушів')

    result_df = result(final_dict, COLUMN_NAMES)
    name = ''.join(('_'.join(('Makita_опт', DATE)), '.xlsx'))
    print('Результуючий файл --->', name)
    result_df.to_excel(name)


main()

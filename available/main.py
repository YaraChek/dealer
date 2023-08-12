#!/usr/bin/env python3

"""
The script indicates which item from the processed price list is in the supplier's main warehouse
"""

import pandas as pd
import datetime


DATE_LABEL = datetime.datetime.now().strftime("%Y-%m-%d")
GOODS_FILE = 'Goods_2023-08-12.xls'
WORKING_FILE = 'working_file.xls'
OUTPUT_FILE = '_'.join((WORKING_FILE[:-4], DATE_LABEL)) + '.xlsx'


def stock_availability(name):
    """
    Uses the supplier's inventory file.
    Returns the set of items in the supplier's main warehouse.
    """
    goods_df = pd.read_excel(name, index_col=0, skiprows=2)
    quantity = goods_df.shape[0]
    articles = {goods_df.index[i] for i in range(quantity) if goods_df.values[i][1] == 'V'}
    return articles


def current_price_list(goods_xls, prise_xls):
    """
    Uses dealer's price list, adds column "Availability"
    :param goods_xls: supplier's inventory file
    :param prise_xls: dealer's price list
    :return: pandas DataFrame for the resulting xlsx-file
    """
    sales_file_df = pd.read_excel(prise_xls, index_col=0, skiprows=8)
    num_rows_sales = sales_file_df.shape[0]
    goods = stock_availability(goods_xls)
    sales_file_df['Наявність'] = \
        ['+' if sales_file_df.index[i] in goods else '-' for i in range(num_rows_sales)]
    return sales_file_df


def main():
    current_price_list(GOODS_FILE, WORKING_FILE).to_excel(OUTPUT_FILE)


if __name__ == "__main__":
    main()

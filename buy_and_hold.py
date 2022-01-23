from datetime import date
import pandas as pd
import yfinance as yf


class Bar:
    def __init__(self):
        self.year = 0
        self.month = 0
        self.day = 0
        self.open = 0
        self.high = 0
        self.low = 0
        self.close = 0


def run(df, start_date, end_date, increment, date_increment, fees):
    """ Основная функция """
    # df = yf.download(ticker)  # Загрузка данных с Yahoo Finance
    # df = df.drop(columns=['Adj Close', 'Volume'])  # Удаляем ненужные колонки
    df = df[start_date:end_date]
    # print(df)
    cur_bar = Bar()
    prev_bar = Bar()
    # print(cur_bar.month, prev_bar.close)
    increment_is_completed = False  # Приращение депо в этом месяце (False-не было, True-было)
    depo = 0  # Брокерский счет в валюте
    sum_depo = 0  # Общая сумма инвестирования (переведено на брокерский счет)
    portfolio = 0  # Количество бумаг

    # Перебор строк DF, как приход нового бара
    for row in df.itertuples():  # Перебор строк DF
        cur_bar.day = date.timetuple(row[0])[2]
        cur_bar.month = date.timetuple(row[0])[1]
        cur_bar.year = date.timetuple(row[0])[0]
        cur_bar.open = row[1]
        cur_bar.high = row[2]
        cur_bar.low = row[3]
        cur_bar.close = row[4]

        if cur_bar.month != prev_bar.month:  # Если месяц предыдущего бара не равен месяцу текущего бара
            increment_is_completed = False
        elif cur_bar.month == prev_bar.month and not increment_is_completed and cur_bar.day >= date_increment:
            depo += increment
            sum_depo += increment
            increment_is_completed = True

        while cur_bar.open + cur_bar.open * fees < depo:
            depo -= cur_bar.open + cur_bar.open * fees
            portfolio += 1

        prev_bar.day = cur_bar.day
        prev_bar.month = cur_bar.month
        prev_bar.year = cur_bar.year
        prev_bar.open = cur_bar.open
        prev_bar.high = cur_bar.high
        prev_bar.low = cur_bar.low
        prev_bar.close = cur_bar.close

    return sum_depo, portfolio * cur_bar.close, depo, portfolio, cur_bar.close


if __name__ == '__main__':
    ticker = 'SPY'  # Тикер финансового инструмента как он отображается на Yahoo Finnce

    df_full = yf.download(ticker)  # Загрузка данных с Yahoo Finance
    df_full = df_full.drop(columns=['Adj Close', 'Volume'])  # Удаляем ненужные колонки

    for year in range(1993, 2022):
        increment: int = 100  # Сумма ежемесячного инвестирования
        date_increment: int = 15  # Дата пополнения(число месяца)
        start_date: date = date(year, 1, 1)  # Дата старта инвестирования(год, месяц, число)
        year_invest: int = 10  # Количество лет инвестирования
        fees = 0.0006  # 0.05% комиссия брокера ВТБ + 0.01% комиссия биржи

        end_date = date(start_date.year + year_invest, start_date.month, start_date.day)

        rez = run(df_full, start_date, end_date, increment, date_increment, fees)

        print(f'Год начала инвестирования: {year}\n'
              f'Всего инвестировано: {rez[0]}\n'
              f'Конечная стоимость портфеля: {rez[1]:.2f}\n'
              f'Остаток денег на брокерском счете: {rez[2]:.2f}\n'
              f'Количество бумаг в портфеле: {rez[3]}\n'
              f'Текущая стоимость одной бумаги: {rez[4]:.2f}\n'
              f'Доход: {rez[1] - rez[0] + rez[2]:.2f}\n'
              f'---------------------------------------------')


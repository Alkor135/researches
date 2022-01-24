from datetime import date
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt


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
    # BRK-B IJH SPY AAPL
    df_rez = pd.DataFrame()
    # ticker_lst = ['AAPL', 'SPY', 'BRK-B', 'IJH']  # Тикер финансовых инструментов как он отображается на Yahoo Finance
    # ticker_lst = ['AAPL', 'BRK-B', 'IJH', 'QQQ']  # Тикер финансовых инструментов как он отображается на Yahoo Finance
    ticker_lst = ['AAPL', 'MSFT', 'NVDA', 'GOOGL']  # Тикер финансовых инструментов как он отображается на Yahoo Finance
    increment: int = 100  # Сумма ежемесячного инвестирования
    date_increment: int = 15  # Дата пополнения(число месяца)
    year_invest: int = 10  # Количество лет инвестирования
    fees = 0.0006  # 0.05% комиссия брокера ВТБ + 0.01% комиссия биржи
    for ticker in ticker_lst:
        df_ticker = yf.download(ticker)  # Загрузка данных с Yahoo Finance
        df_ticker = df_ticker.drop(columns=['Adj Close', 'Volume'])  # Удаляем ненужные колонки

        df_rez_ticker = pd.DataFrame()

        for year in range(1993, 2022):
            start_date: date = date(year, 1, 1)  # Дата старта инвестирования(год, месяц, число)
            end_date = date(start_date.year + year_invest, start_date.month, start_date.day)

            rez = run(df_ticker, start_date, end_date, increment, date_increment, fees)

            dohod = rez[1] - rez[0] + rez[2]

            new_row = {'Год начала': year, f'Доход {ticker}': dohod}
            df_rez_ticker = df_rez_ticker.append(new_row, ignore_index=True)

        # print(df_rez)
        # print(df_rez_ticker)
        if len(df_rez) == 0:
            df_rez = df_rez_ticker
        else:
            df_rez = pd.merge(df_rez, df_rez_ticker)

    index = df_rez['Год начала']
    values0 = df_rez[f'Доход {ticker_lst[0]}']
    values1 = df_rez[f'Доход {ticker_lst[1]}']
    values2 = df_rez[f'Доход {ticker_lst[2]}']
    values3 = df_rez[f'Доход {ticker_lst[3]}']
    bw = 0.2
    plt.title(f'Доход за {year_invest} лет ежемесячного инвестирования по ${increment}')
    plt.bar(index - 0.4, values0, bw, label=f'Доход {ticker_lst[0]}')
    plt.bar(index - 0.2, values1, bw, label=f'Доход {ticker_lst[1]}')
    plt.bar(index, values2, bw, label=f'Доход {ticker_lst[2]}')
    plt.bar(index + 0.2, values3, bw, label=f'Доход {ticker_lst[3]}')
    plt.xticks(index, df_rez['Год начала'])
    plt.xlabel("Год начала инвестирования")
    plt.ylabel("Доход в $")
    plt.legend(loc=2)
    plt.show()

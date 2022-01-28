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

    cur_bar = Bar()
    prev_bar = Bar()

    increment_is_completed = False  # Приращение депо в этом месяце (False-не было, True-было)
    depo = 0  # Брокерский счет в валюте
    sum_depo = 0  # Общая сумма инвестирования (переведено на брокерский счет)
    portfolio = 0  # Количество бумаг в портфеле

    # Перебор строк DF, как приход нового бара
    for row in df.itertuples():  # Перебор строк DF (аналог появления нового бара)
        # Обновляем информацию текущего бара
        cur_bar.day = date.timetuple(row[0])[2]
        cur_bar.month = date.timetuple(row[0])[1]
        cur_bar.year = date.timetuple(row[0])[0]
        cur_bar.open = row[1]
        cur_bar.high = row[2]
        cur_bar.low = row[3]
        cur_bar.close = row[4]

        if cur_bar.month != prev_bar.month:  # Если месяц предыдущего бара не равен месяцу текущего бара
            increment_is_completed = False  # Признак инвестирования в текущем месяце в False
        elif cur_bar.month == prev_bar.month and not increment_is_completed and cur_bar.day >= date_increment:
            depo += increment  # Увеличение брокерского счета на сумму ежемесячных инвестиций
            sum_depo += increment  # Увеличение общей суммы инвестиций
            increment_is_completed = True  # Признак инвестирования в текущем месяце в True

        while cur_bar.open + cur_bar.open * fees < depo:  # Если сумма на счете позволяет купить фин. инструмент
            depo -= cur_bar.open + cur_bar.open * fees  # Списываем с брокерского счета сумму на покупку
            portfolio += 1  # Увеличиваем количество бумаг в портфеле

        # Обновление информации предыдущего бара
        prev_bar.day = cur_bar.day
        prev_bar.month = cur_bar.month
        prev_bar.year = cur_bar.year
        prev_bar.open = cur_bar.open
        prev_bar.high = cur_bar.high
        prev_bar.low = cur_bar.low
        prev_bar.close = cur_bar.close

    return sum_depo, portfolio * cur_bar.close, depo, portfolio, cur_bar.close


if __name__ == '__main__':
    # BRK-B IJH SPY AAPL QQQ
    ticker = 'VGK'  # Тикер финансового инструмента как он отображается на Yahoo Finance
    increment: int = 100  # Сумма ежемесячного инвестирования
    date_increment: int = 15  # Дата пополнения(число месяца)
    year_invest: int = 10  # Количество лет инвестирования
    fees = 0.0006  # 0.05% комиссия брокера ВТБ + 0.01% комиссия биржи

    df_ticker = yf.download(ticker)  # Загрузка данных с Yahoo Finance
    df_ticker = df_ticker.drop(columns=['Adj Close', 'Volume'])  # Удаляем ненужные колонки

    df_rez_ticker = pd.DataFrame()

    for year in range(1993, 2022):
        start_date: date = date(year, 1, 1)  # Дата старта инвестирования(год, месяц, число)
        end_date = date(start_date.year + year_invest, start_date.month, start_date.day)

        rez = run(df_ticker, start_date, end_date, increment, date_increment, fees)

        dohod = rez[1] - rez[0] + rez[2]
        # print(f'Год начала инвестирования: {year}\n'
        #       f'Всего инвестировано: {rez[0]}\n'
        #       f'Конечная стоимость портфеля: {rez[1]:.2f}\n'
        #       f'Остаток денег на брокерском счете: {rez[2]:.2f}\n'
        #       f'Количество бумаг в портфеле: {rez[3]}\n'
        #       f'Текущая стоимость одной бумаги: {rez[4]:.2f}\n'
        #       f'Доход: {dohod:.2f}\n'
        #       f'---------------------------------------------')

        # new_row = {'Год начала': year, 'Инвестировано': rez[0], 'Стоим портфеля': rez[1], 'Деньги': rez[2],
        #            'Бумаги': rez[3], 'Стоимость бумаги': rez[4], 'Доход': dohod}

        new_row = {'Год начала': str(year),
                   'Инвестировано': round(rez[0], 2),
                   'Стоим портфеля': round(rez[1], 2),
                   'Доход': round(dohod, 2)
                   }

        # append row to the dataframe
        df_rez_ticker = df_rez_ticker.append(new_row, ignore_index=True)

    pd.set_option('display.max_columns', None)  # Сброс ограничений на число столбцов
    print(df_rez_ticker)  # Вывод таблицы результата

    # Построение графика
    index = df_rez_ticker['Год начала']
    values = df_rez_ticker['Доход']
    plt.title(f'Доход за {year_invest} лет ежемесячного инвестирования по ${increment} в инструмент {ticker}')
    plt.bar(index, values, label='Доход')
    plt.xticks(index, df_rez_ticker['Год начала'].apply(int), rotation=45)  # Подписи к оси Х переведены в int и повернуты
    plt.xlabel("Год начала инвестирования")
    plt.ylabel("Доход в $")
    plt.legend(loc=2)
    plt.show()

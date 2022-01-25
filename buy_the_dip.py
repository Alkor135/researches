from datetime import date
import pandas as pd
import talib
import yfinance as yf
import matplotlib.pyplot as plt


class Bar:
    def __init__(self):
        self.year = 0
        self.month = 0
        self.day = 0
        self.open = 0
        self.close = 0
        self.std1 = 0
        self.std2 = 0
        self.std3 = 0


def prepare_df(ticker, timeperiod):
    """ Функция подготовки данных """
    df = yf.download(ticker)  # Загрузка данных с Yahoo Finance
    df = df.drop(columns=['Adj Close', 'Volume', 'High', 'Low'])  # Удаляем ненужные колонки

    # Создание series индикатора LINEARREG по данным из dataframe
    df[f'lr{timeperiod}'] = talib.LINEARREG(df['Close'], timeperiod=timeperiod)

    # Создание series индикатора STDDEV по данным из dataframe
    df['stddev1'] = talib.STDDEV(df['Close'], timeperiod=timeperiod, nbdev=1)
    df['stddev2'] = talib.STDDEV(df['Close'], timeperiod=timeperiod, nbdev=2)
    df['stddev3'] = talib.STDDEV(df['Close'], timeperiod=timeperiod, nbdev=3)

    df = df.dropna()  # Убираем данные с пустыми значениями

    # Создаем колонки со значениями -1/-2/-3 STD
    df = df.assign(STD1=lambda x: x[f'lr{timeperiod}'] - x['stddev1'],
                   STD2=lambda x: x[f'lr{timeperiod}'] - x['stddev2'],
                   STD3=lambda x: x[f'lr{timeperiod}'] - x['stddev3'])

    df = df.drop(columns=[f'lr{timeperiod}', 'stddev1', 'stddev2', 'stddev3'])  # Удаляем ненужные колонки
    return df


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
        cur_bar.close = row[2]
        cur_bar.std1 = row[3]
        cur_bar.std2 = row[4]
        cur_bar.std3 = row[4]

        # Приращение depo
        if cur_bar.month != prev_bar.month:  # Если месяц предыдущего бара не равен месяцу текущего бара
            increment_is_completed = False  # Признак инвестирования в текущем месяце в False
        elif cur_bar.month == prev_bar.month and not increment_is_completed and cur_bar.day >= date_increment:
            depo += increment  # Увеличение брокерского счета на сумму ежемесячных инвестиций
            sum_depo += increment  # Увеличение общей суммы инвестиций
            increment_is_completed = True  # Признак инвестирования в текущем месяце в True

        # Покупка
        while cur_bar.open + cur_bar.open * fees < depo and \
                cur_bar.open < cur_bar.std1:  # Условия покупки
            depo -= cur_bar.open + cur_bar.open * fees  # Списываем с брокерского счета сумму на покупку
            portfolio += 1  # Увеличиваем количество бумаг в портфеле

        # Обновление информации предыдущего бара
        prev_bar.day = cur_bar.day
        prev_bar.month = cur_bar.month
        prev_bar.year = cur_bar.year
        prev_bar.open = cur_bar.open
        prev_bar.close = cur_bar.close
        prev_bar.std1 = cur_bar.std1
        prev_bar.std2 = cur_bar.std2
        prev_bar.std3 = cur_bar.std3

    return sum_depo, portfolio * cur_bar.close, depo, portfolio, cur_bar.close


if __name__ == '__main__':
    # BRK-B IJH SPY AAPL QQQ NVDA TSLA
    ticker: str = 'QQQ'  # Тикер финансового инструмента как он отображается на Yahoo Finance
    increment: int = 1000  # Сумма ежемесячного инвестирования
    date_increment: int = 15  # Дата пополнения(число месяца)
    start_date: date = date(1993, 1, 1)  # Дата старта инвестирования(год, месяц, число)
    year_invest: int = 10  # Количество лет инвестирования
    timeperiod: int = 200  # Период для расчета индикаторов (линейная регрессия, стандартное отклонение)
    fees = 0.0006  # 0.05% комиссия брокера ВТБ + 0.01% комиссия биржи

    end_date = date(start_date.year + year_invest, start_date.month, start_date.day)

    df = prepare_df(ticker, timeperiod)

    pd.set_option('display.max_columns', None)  # Сброс ограничений на число столбцов
    print(df)

    # plt.plot(df['Close'], label=ticker)
    # plt.plot(df['STD1'], label='STD1')
    # plt.plot(df['STD2'], label='STD2')
    # plt.plot(df['STD3'], label='STD3')
    # plt.legend(loc='upper left')
    # plt.show()

    df_rez_ticker = pd.DataFrame()

    for year in range(1993, 2022):
        start_date: date = date(year, 1, 1)  # Дата старта инвестирования(год, месяц, число)
        end_date = date(start_date.year + year_invest, start_date.month, start_date.day)

        rez = run(df, start_date, end_date, increment, date_increment, fees)

        dohod = rez[1] - rez[0] + rez[2]

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

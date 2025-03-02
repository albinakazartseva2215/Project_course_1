import json

from src.utils import get_time_for_greeting, get_card_with_spent, get_path_and_period, PATH_TO_FILE, get_date_time, \
    get_top_transactions, get__usd_eur, PATH_TO_FILE_JSON, get_stocks


def main_str(date_time: str):
    """Функция для страницы «Главная» принимает на вход строку с датой и временем в формате
       YYYY-MM-DD HH:MM:SS и возвращающую JSON-ответ"""
    greeting = get_time_for_greeting(date_time)
    time_period = get_date_time(date_time)
    sorted_df = get_path_and_period(PATH_TO_FILE, time_period)
    cards = get_card_with_spent(sorted_df)
    top_transactions = get_top_transactions(sorted_df)
    currency_usd_euro = get__usd_eur(PATH_TO_FILE_JSON)
    stock_prices = get_stocks(PATH_TO_FILE_JSON)
    data = {"greeting": greeting, "cards": cards, "top_transactions": top_transactions, "currency_rates": currency_usd_euro, "stock_prices": stock_prices}
    json_data = json.dumps(data, ensure_ascii=False, indent=4)
    return json_data

if __name__ == "__main__":
    date_now = "2018-05-20 15:30:00"
    print(main_str(date_now))
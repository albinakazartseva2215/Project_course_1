import json
import logging

import pandas as pd

from src.utils import PATH_TO_FILE

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="../logs/example.log",
    filemode="w",
    encoding="utf-8",
)

services_loger = logging.getLogger("services")


def analyze_cashback(file_path: str, year: int, month: int) -> json:
    """
    Анализирует выгодность категорий повышенного кешбэка.
    :return: JSON с суммами кешбэка по категориям.
    """
    services_loger.info(f"Запуск функции spending_by_category с файлом: {file_path}, годом: {year}, месяцем: {month}")
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        services_loger.error(f"Ошибка при чтении файла: {e}")
        return {}

        # Преобразование даты в формат datetime
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    services_loger.info("Преобразование даты в формат datetime")
    # Фильтрация данных по году и месяцу
    filtered_data = df[(df["Дата операции"].dt.year == year) & (df["Дата операции"].dt.month == month)]
    services_loger.info("Фильтрация данных по году и месяцу")
    # Если filtered_data не содержит строк
    if filtered_data.empty:
        services_loger.warning(f"Нет данных за {month}.{year}")
        return {}

    # Фильтрация расходов (отрицательные значения в "Сумма операции")
    filtered_data = filtered_data[filtered_data["Сумма платежа"] < 0]
    services_loger.info("Фильтрация расходов")
    # Группировка по категориям и расчёт суммы расходов
    expenses_by_category = filtered_data.groupby("Категория")["Сумма платежа"].sum()

    # Расчёт кешбэка: сумма расходов // 100
    cashback_by_category = (abs(expenses_by_category) // 100).astype(int)
    services_loger.info("Расчет кэшбэка")
    # Преобразование в словарь
    result = cashback_by_category.to_dict()

    services_loger.info(f"Анализ завершён. Найдено {len(result)} категорий.")
    return json.dumps(result, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    result = analyze_cashback(PATH_TO_FILE, 2018, 5)
    print(result)

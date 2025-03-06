import json
import logging

import pandas as pd

from src.utils import PATH_TO_FILE


logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    filename="../logs/warning.log",
                    filemode="w", encoding="utf-8")


def analyze_cashback(file_path: str, year: int, month: int) -> json:
    """
    Анализирует выгодность категорий повышенного кешбэка.
    :return: JSON с суммами кешбэка по категориям.
    """
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        logging.error(f"Ошибка при чтении файла: {e}")
        return {}

        # Преобразование даты в формат datetime
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%d.%m.%Y %H:%M:%S")

    # Фильтрация данных по году и месяцу
    filtered_data = df[
        (df["Дата операции"].dt.year == year) & (df["Дата операции"].dt.month == month)
        ]
    # Если filtered_data не содержит строк
    if filtered_data.empty:
        logging.warning(f"Нет данных за {month}.{year}")
        return {}

    # Фильтрация расходов (отрицательные значения в "Сумма операции")
    filtered_data = filtered_data[filtered_data["Сумма платежа"] < 0]

    # Группировка по категориям и расчёт суммы расходов
    expenses_by_category = filtered_data.groupby("Категория")["Сумма платежа"].sum()

    # Расчёт кешбэка: сумма расходов // 100
    cashback_by_category = (abs(expenses_by_category) // 100).astype(int)  # astype(int) приводит к целому числу

    # Преобразование в словарь
    result = cashback_by_category.to_dict()

    logging.info(f"Анализ завершён. Найдено {len(result)} категорий.")
    return json.dumps(result, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    result = analyze_cashback(PATH_TO_FILE, 2018, 5)
    print(result)



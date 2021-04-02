from src.accounting import Accounting
from src.to_excel import ExcelReporter


INITIAL_ASSETS = {  # начальные активы
    "50": 3_000,
    "51": 1_000_000
}
INITIAL_LIABILITIES = {  # начальные пассивы
    "80": 1_003_000
}
POSTINGS = {  # проводки
    1: {"Дебит": "50", "Кредит": "51", "Тип": 5, "Сумма": 150_000},

    2: {"Дебит": "70", "Кредит": "50", "Тип": 5, "Сумма": 145_000},

    3: {"Дебит": "51", "Кредит": "50", "Тип": 5, "Сумма": 5_000},

    4: {"Дебит": "50", "Кредит": "51", "Тип": 5, "Сумма": 1_500},

    5: {"Дебит": "50", "Кредит": "51", "Тип": 5, "Сумма": 30_000},

    6: {"Дебит": "73", "Кредит": "50", "Тип": 5, "Сумма": 30_000},

    7: {"Дебит": "71", "Кредит": "50", "Тип": 5, "Сумма": 700},

    8: {"Дебит": "71", "Кредит": "50", "Тип": 5, "Сумма": 600},

    9: {"Дебит": "50", "Кредит": "73", "Тип": 5, "Сумма": 15_000},

    10: {"Дебит": "71", "Кредит": "50", "Тип": 5, "Сумма": 7_000},

    11: {"Дебит": "94", "Кредит": "50", "Тип": 5, "Сумма": 500},

    12: {"Дебит": "51", "Кредит": "62", "Тип": 5, "Сумма": 600_000},

    13: {"Дебит": "70", "Кредит": "51", "Тип": 5, "Сумма": 200_000},

    14: {"Дебит": "51", "Кредит": "75", "Тип": 5, "Сумма": 20_000},

    15: {"Дебит": "60", "Кредит": "51", "Тип": 5, "Сумма": 150_000}
}


if __name__ == '__main__':
    acc = Accounting(INITIAL_ASSETS, INITIAL_LIABILITIES, POSTINGS)

    initial_balance = acc.get_initial_balance()
    postings = acc.get_postings()
    airplanes = acc.get_airplanes()
    final_balance = acc.get_final_balance()
    working_balance_sheet = acc.get_working_balance_sheet()

    reporter = ExcelReporter("KovalevAI_PI19-3.xlsx")

    reporter.write_initial_balance(initial_balance)
    reporter.write_postings(postings)
    reporter.write_airplanes(airplanes)
    reporter.write_final_balance(final_balance)
    reporter.write_working_balance_sheet(working_balance_sheet)

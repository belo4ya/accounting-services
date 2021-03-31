import pandas as pd


class ExcelReporter:

    def __init__(self, path):
        self.path = path

    def write_initial_balance(self, data: pd.DataFrame, sheet_name: str = "Начальный баланс"):
        self._write(data, sheet_name)

    def write_postings(self, data: pd.DataFrame, sheet_name: str = "Проводки"):
        self._write(data, sheet_name)

    def write_airplanes(self, data: pd.DataFrame, sheet_name: str = "Самолетики"):
        self._write(data, sheet_name)

    def write_final_balance(self, data: pd.DataFrame, sheet_name: str = "Конечный баланс"):
        self._write(data, sheet_name)

    def write_working_balance_sheet(self, data: pd.DataFrame, sheet_name: str = "Оборотно сальдовая ведомость"):
        self._write(data, sheet_name)

    def _write(self, data: pd.DataFrame, sheet_name: str):
        try:
            with pd.ExcelWriter(self.path, mode="a") as writer:
                data.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
        except FileNotFoundError:
            with pd.ExcelWriter(self.path, mode="w") as writer:
                data.to_excel(writer, sheet_name=sheet_name, index=False, header=False)

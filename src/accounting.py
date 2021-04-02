import numpy as np
import pandas as pd

from src.transaction_types import TYPES


class Accounting:
    SUM = "Сумма"
    RESULT = "Итог"
    ASSET = "Актив"
    LIABILITY = "Пассив"
    DEBIT = "Дебит"
    CREDIT = "Кредит"
    TURNOVERS = "Обороты"
    TYPE = "Тип"
    INITIAL_BALANCE = "Сальдо начальное"
    FINAL_BALANCE = "Сальдо конечное"

    def __init__(self, initial_assets: dict, initial_liabilities: dict, postings: dict):
        self._initial_assets = self._get_assets(initial_assets)
        self._initial_liabilities = self._get_liabilities(initial_liabilities)

        self._postings = pd.DataFrame(postings.values())
        self._update_transaction_types()

        self._input_validate()

        self._airplanes = self._calc_airplanes()

    def _get_assets(self, assets: dict) -> pd.DataFrame:
        return pd.DataFrame(assets.items(), columns=[self.ASSET, self.SUM])

    def _get_liabilities(self, liabilities: dict) -> pd.DataFrame:
        return pd.DataFrame(liabilities.items(), columns=[self.LIABILITY, self.SUM])

    def _update_transaction_types(self):
        for i, row in self._postings.iterrows():
            if pd.isnull(row.loc[self.TYPE]):
                self._postings.loc[i, self.TYPE] = TYPES.get((row.loc[self.DEBIT], row.loc[self.CREDIT])) or np.nan

    def _input_validate(self):
        assert pd.DataFrame.sum(self._initial_assets.loc[:, self.SUM]) == \
               pd.DataFrame.sum(self._initial_liabilities.loc[:, self.SUM]), (
            "Баланс (Актив) != Баланс (Пассив)"
        )

        assert self._postings.loc[:, self.TYPE].notnull().all(), (
                "Присутствуют неизвестные типы проводок:\n" + str(self._postings)
        )

        print("Валидация успешна!")

    def _get_account_numbers(self) -> list:
        return sorted({
            *self._initial_assets.loc[:, self.ASSET].values,
            *self._initial_liabilities.loc[:, self.LIABILITY].values,
            *self._postings.loc[:, self.DEBIT],
            *self._postings.loc[:, self.CREDIT]
        })

    def _calc_airplanes(self) -> dict:
        airplanes = {}
        for acc in self._get_account_numbers():
            active_accounts = self._initial_assets.loc[:, self.ASSET]
            passive_accounts = self._initial_liabilities.loc[:, self.LIABILITY]
            if acc in active_accounts.values or acc in passive_accounts.values:
                if acc in active_accounts.values:
                    balance_type = self.DEBIT  # сальдо начальное дебетовое
                    initial_balance = self._initial_assets[active_accounts == acc].loc[:, self.SUM].squeeze()
                else:
                    balance_type = self.CREDIT  # сальдо начальное кредитовое
                    initial_balance = self._initial_liabilities[passive_accounts == acc].loc[:, self.SUM].squeeze()
            else:
                balance_type = self.DEBIT  # сальдо начальное дебетовое
                initial_balance = 0

            debit_turnovers = self._postings[self._postings.loc[:, self.DEBIT] == acc].loc[:, self.SUM]  # обороты
            credit_turnovers = self._postings[self._postings.loc[:, self.CREDIT] == acc].loc[:, self.SUM]  # обороты

            debit_turnovers_sum = debit_turnovers.sum()  # сумма по оборотам по дебету
            credit_turnovers_sum = credit_turnovers.sum()  # сумма по оборотам по кредиту

            if balance_type == self.DEBIT:
                final_balance = initial_balance + debit_turnovers_sum - credit_turnovers_sum  # сальдо конечное
            else:
                final_balance = initial_balance + credit_turnovers_sum - debit_turnovers_sum  # сальдо конечное

            if final_balance < 0:
                balance_type = self.CREDIT
                final_balance = -final_balance

            airplane = {
                self.DEBIT: {self.TURNOVERS: debit_turnovers,
                             self.SUM: debit_turnovers_sum},
                self.CREDIT: {self.TURNOVERS: credit_turnovers,
                              self.SUM: credit_turnovers_sum}
            }
            airplane[balance_type][self.INITIAL_BALANCE] = initial_balance
            airplane[balance_type][self.FINAL_BALANCE] = final_balance

            airplanes[acc] = airplane

        return airplanes

    def _get_balance(self, assets: pd.DataFrame, liabilities: pd.DataFrame, header: str) -> pd.DataFrame:
        df = pd.DataFrame(data=None,
                          index=range(1, max(assets.shape[0],
                                             liabilities.shape[0]) + 5),
                          columns=self._alphabetical_range("A", "D"))
        df.loc[1, "A"] = header
        df.loc[2, "A":"D"] = [self.ASSET, self.SUM, self.LIABILITY, self.SUM]

        assets_height = assets.loc[:, self.ASSET].shape[0]
        liabilities_height = liabilities.loc[:, self.LIABILITY].shape[0]
        df.loc[3:assets_height + 2, "A"] = assets.loc[:, self.ASSET].values
        df.loc[3:assets_height + 2, "B"] = assets.loc[:, self.SUM].values
        df.loc[3:liabilities_height + 2, "C"] = liabilities.loc[:, self.LIABILITY].values
        df.loc[3:liabilities_height + 2, "D"] = liabilities.loc[:, self.SUM].values

        height = df.shape[0]
        df.loc[height, "A":"D"] = [self.RESULT,
                                   df.loc[3:height - 2, "B"].sum(),
                                   self.RESULT,
                                   df.loc[3:height - 2, "D"].sum()]
        return df

    def get_initial_balance(self) -> pd.DataFrame:
        """Таблица 'Начальный баланс'"""
        return self._get_balance(self._initial_assets, self._initial_liabilities, "Начальный баланс")

    def get_final_balance(self) -> pd.DataFrame:
        """Таблица 'Конечный баланс'"""
        assets = {}
        liabilities = {}
        for acc_number, airplane in self._airplanes.items():
            debit = airplane[self.DEBIT].get(self.FINAL_BALANCE)
            if debit:
                assets[acc_number] = debit

            credit = airplane[self.CREDIT].get(self.FINAL_BALANCE)
            if credit:
                liabilities[acc_number] = credit

        assets = self._get_assets(assets)
        liabilities = self._get_liabilities(liabilities)

        return self._get_balance(assets, liabilities, "Конечный баланс")

    def get_postings(self) -> pd.DataFrame:
        df = pd.DataFrame(data=None,
                          index=range(1, self._postings.shape[0] + 3),
                          columns=self._alphabetical_range("A", "F"))
        df.loc[1, "A":"C"] = ["№", "Документ и содержание операции", "Корреспондирующие счета"]
        df.loc[1, "E":"F"] = [self.TYPE, self.SUM]
        df.loc[2, "C":"D"] = [self.DEBIT, self.CREDIT]

        df.loc[3:, ["A", "C", "D", "E", "F"]] = pd.DataFrame(data=[self._postings.index + 1,
                                                                   self._postings.loc[:, self.DEBIT],
                                                                   self._postings.loc[:, self.CREDIT],
                                                                   self._postings.loc[:, self.TYPE],
                                                                   self._postings.loc[:, self.SUM]],
                                                             index=["A", "C", "D", "E", "F"],
                                                             columns=df.index[2:]).transpose()

        return df

    def get_airplanes(self) -> pd.DataFrame:
        """Таблицы 'Самолетики'"""
        airplanes = []
        turnovers_height = self._postings.shape[0]
        for acc_number, airplane in self._airplanes.items():
            df = pd.DataFrame(data=None,
                              index=range(1, turnovers_height + 9),
                              columns=self._alphabetical_range("A", "D"))
            df.loc[1, "A"] = acc_number
            df.loc[2, ["A", "C"]] = [self.DEBIT, self.CREDIT]

            debit_airplane = airplane[self.DEBIT]
            credit_airplane = airplane[self.CREDIT]

            is_debit_balance = bool(debit_airplane.get(self.INITIAL_BALANCE) is not None or
                                    debit_airplane.get(self.FINAL_BALANCE) is not None)
            if is_debit_balance:
                df.loc[3, "A":"B"] = [self.INITIAL_BALANCE, debit_airplane.get(self.INITIAL_BALANCE)]
                df.loc[df.shape[0], "A":"B"] = [self.FINAL_BALANCE, debit_airplane.get(self.FINAL_BALANCE)]
            else:
                df.loc[3, "C":"D"] = [self.INITIAL_BALANCE, credit_airplane.get(self.INITIAL_BALANCE)]
                df.loc[df.shape[0], "C":"D"] = [self.FINAL_BALANCE, credit_airplane.get(self.FINAL_BALANCE)]

            debit_airplane[self.TURNOVERS].index = debit_airplane[self.TURNOVERS].index + 5
            credit_airplane[self.TURNOVERS].index = credit_airplane[self.TURNOVERS].index + 5

            df.loc[5:turnovers_height + 4, "A"] = pd.Series(data=debit_airplane[self.TURNOVERS].index - 4,
                                                            index=debit_airplane[self.TURNOVERS].index)
            df.loc[5:turnovers_height + 4, "B"] = debit_airplane[self.TURNOVERS]
            df.loc[5:turnovers_height + 4, "B"].fillna(0, inplace=True)

            df.loc[5:turnovers_height + 4, "C"] = pd.Series(data=credit_airplane[self.TURNOVERS].index - 4,
                                                            index=credit_airplane[self.TURNOVERS].index)
            df.loc[5:turnovers_height + 4, "D"] = credit_airplane[self.TURNOVERS]
            df.loc[5:turnovers_height + 4, "D"].fillna(0, inplace=True)

            df.loc[df.shape[0] - 2, "A":"D"] = [self.SUM, debit_airplane[self.SUM],
                                                self.SUM, credit_airplane[self.SUM]]

            airplanes.append(df)

        airplane_height = airplanes[0].shape[0]
        df = pd.DataFrame(data=None,
                          index=range(1, len(airplanes) * (airplane_height + 3) + 1),
                          columns=self._alphabetical_range("A", "D"))
        for i, airplane in enumerate(airplanes):
            i *= airplane_height + 3
            airplane.index = airplane.index + i
            df.loc[i:i + airplane_height, :] = airplane

        return df

    def get_working_balance_sheet(self):
        """Таблица 'Оборотно-сальдовая ведомость'"""
        df = pd.DataFrame(data=None,
                          index=range(1, len(self._airplanes) + 5),
                          columns=self._alphabetical_range("A", "G"))
        df.loc[1, ["A", "B", "D", "F"]] = ["Счет", self.INITIAL_BALANCE, self.TURNOVERS, self.FINAL_BALANCE]
        df.loc[2, "B":"G"] = [self.DEBIT, self.CREDIT] * 3

        for i, airplane in enumerate(self._airplanes.items()):
            debit = airplane[1][self.DEBIT]
            credit = airplane[1][self.CREDIT]
            df.loc[i + 3, "A":"G"] = [airplane[0],
                                      debit.get(self.INITIAL_BALANCE, 0),
                                      credit.get(self.INITIAL_BALANCE, 0),
                                      debit.get(self.SUM, 0),
                                      credit.get(self.SUM, 0),
                                      debit.get(self.FINAL_BALANCE, 0),
                                      credit.get(self.FINAL_BALANCE, 0)]

        height = df.shape[0]
        df.loc[height, "A":"G"] = [self.RESULT, *df.loc[3:height - 2, "B":"G"].sum(axis=0)]
        return df

    @staticmethod
    def _alphabetical_range(start: str, stop: str) -> list:
        return [chr(i) for i in range(ord(start), ord(stop) + 1)]

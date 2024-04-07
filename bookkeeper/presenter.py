import sys

from typing import Protocol, Callable
from datetime import datetime, timedelta, date
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.models.budget import Budget
from bookkeeper.view.app_window import MainWindow
from bookkeeper.repository.sqlite_repository import SQliteRepository
from bookkeeper.repository.abstract_repository import AbstractRepository


class AbstractView(Protocol):

    def __init__(self) -> None:
        pass

    def init_ui(self) -> None:
        pass

    def expense_change_handler(
        self, handler: Callable[[int, str, datetime, str, int], None]
    ) -> None:
        """
        Изменяет некоторые параметры записи расходов
        """
        pass

    def expense_add_handler(
        self, handler: Callable[[int, str, datetime], None]
    ) -> None:
        """
        Добавляет новую запись расходов
        """
        pass

    def delete_category_handler(self, handler: Callable[[str], None]) -> None:
        """
        Удаляет категорию из списка категорий
        """
        pass

    def add_category_handler(self, handler: Callable[[Category], None]) -> None:
        """
        Добавляет новую категорию в список категорий
        """
        pass

    def budget_change_handler(self, handler: Callable[[Budget], None]) -> None:
        """
        Изменяет установленный бюджет на период
        """
        pass

    def set_budget(self, budgets: list[Budget]) -> None:
        pass

    def set_categories(self, categories: list[Category]) -> None:
        pass

    def set_expense_list(self, expenses: list[Expense]) -> None:
        pass

    def set_summ(self, summs: list[float]) -> None:
        pass

    def do_show(self) -> None:
        pass


class Bookkeeper:

    def __init__(
        self,
        view: AbstractView,
        category_repository: AbstractRepository[Category],
        budget_repository: AbstractRepository[Budget],
        expense_repository: AbstractRepository[Expense],
    ) -> None:
        self.day_budg = 1000
        self.week_budg = 3000
        self.month_budg = 10000
        self.budgets: list[Budget]

        self.month_summ = 0
        self.week_summ = 0
        self.day_summ = 0

        self.view = view
        self.category_repository = category_repository
        self.expense_repository = expense_repository
        self.budget_repository = budget_repository

        # self.cats = self.category_repository.get_all()
        # self.view.set_category_list(self.cats)
        self.view.expense_change_handler(self.change_expense)
        self.view.expense_add_handler(self.add_expense)
        self.view.delete_category_handler(self.delete_category)
        self.view.add_category_handler(self.add_category)
        self.view.budget_change_handler(self.budget_change)
        self.view.init_ui()

        self.set_budget()
        self.set_categories()
        self.set_expense_list()
        self.set_summ()
        self.view.do_show()

    def set_budget(self) -> None:
        self.budgets = self.budget_repository.get_all()
        if len(self.budgets) == 0:
            budg_for_day = Budget(self.day_budg, 1)
            budg_for_week = Budget(self.week_budg, 7)
            budg_for_month = Budget(self.month_budg, 31)
            self.budgets = [budg_for_day, budg_for_week, budg_for_month]
            for budgs in self.budgets:
                self.budget_repository.add(budgs)
        self.view.set_budget(self.budgets)

    def set_categories(self) -> None:
        categories = self.category_repository.get_all()
        if len(categories) == 0:
            transport_cat = Category("Транспорт")
            home_cat = Category("Дом")
            products_cat = Category("Продукты")
            categories = [transport_cat, home_cat, products_cat]
            for cat in categories:
                self.category_repository.add(cat)
        self.view.set_categories(categories)

    def set_expense_list(self) -> None:
        expenses = self.expense_repository.get_all()
        if len(expenses) == 0:
            expenses = self.expense_repository.get_all()
        self.view.set_expense_list(expenses)

    def set_summ(self) -> None:
        self.day_summ = 0
        self.week_summ = 0
        self.month_summ = 0
        expenses = self.expense_repository.get_all()
        if len(expenses) != 0:
            today = date.today()
            week = today - timedelta(7)
            month = today - timedelta(31)
            for exp in expenses:
                exp_date = exp.expense_date.date()
                if exp_date >= month:
                    self.month_summ += exp.amount
                if exp_date >= week:
                    self.week_summ += exp.amount
                if exp_date >= today:
                    self.day_summ += exp.amount
        summs = list(map(float, [self.day_summ, self.week_summ, self.month_summ]))
        self.view.set_summ(summs)

    def change_expense(
        self,
        amount: int,
        cat: str,
        date: datetime,
        com: str,
        pk: int,
    ) -> None:
        cat_list = self.category_repository.get_all({"name": cat})
        assert len(cat_list) == 1
        prim_key = cat_list[0].pk
        exp = Expense(amount, prim_key, date, comment=com, pk=pk)
        self.expense_repository.update(exp)
        self.set_summ()

    def add_expense(self, amount: int, cat: str, date: datetime) -> None:
        cat_list = self.category_repository.get_all({"name": cat})
        assert len(cat_list) == 1
        prim_key = cat_list[0].pk
        exp = Expense(amount, prim_key, date)
        self.expense_repository.add(exp)
        self.set_summ()

    def delete_category(self, name: str) -> None:
        cat_list = self.category_repository.get_all({"name": name})
        assert len(cat_list) == 1
        prim_key = cat_list[0].pk
        self.category_repository.delete(prim_key)

    def add_category(self, cat: Category) -> None:
        self.category_repository.add(cat)

    def budget_change(self, budg: Budget) -> None:
        self.budget_repository.update(budg)


def main() -> int:
    main_window = MainWindow()
    cat_repo = SQliteRepository[Category]("bookkeper.db", Category)
    budget_repo = SQliteRepository[Budget]("bookkeper.db", Budget)
    expense_repo = SQliteRepository[Expense]("bookkeper.db", Expense)

    Bookkeeper(main_window, cat_repo, budget_repo, expense_repo)
    return 0


if __name__ == "__main__":
    sys.exit(main())

# def add_category(self, name, parent):
#     if name in [c.name for c in self.cats]:
#         raise ValidationError(f"Категория {name} уже существует")
#     cat = Category(name, parent)
#     self.category_repository.add(cat)
#     self.cats.append(cat)
#     self.view.set_category_list(self.cats)

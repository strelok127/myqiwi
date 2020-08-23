import time
import random_data

from . import request
from . import exceptions


class Wallet:
    __PAYMENT_FORM_URL = "https://qiwi.com/payment/form/"
    """ 
    This is Wallet Class
    Methods:
        balance
        profile
        history
        generate_pay_form
        send
        search_payment
        gen_payment
    """

    def __init__(self, token: str, proxy: dict = None):
        """
        Visa QIWI Кошелек
        Parameters
        ----------
        token : str
            `Ключ Qiwi API` пользователя.
        proxy : Optional[str]
            Прокси.
            Появится будущем...
        """
        request.proxy = proxy
        request.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(token),
        }

        profile = self.profile()
        self.__phone = profile["contractInfo"]["contractId"]
        self.__username = profile["contractInfo"]["nickname"]["nickname"]

    @property
    def phone(self):
        return self.__phone

    @property
    def username(self):
        return self.__username

    def balance(self, currency=643):
        """
        Баланс Кошелька.

        Parameters
        ----------
        currency : int
            ID валюты в ``number-3 ISO-4217``.
            Например, ``643`` для российского рубля.

        Returns
        -------
        float
            Баланс кошелька.
        """
        path = "funding-sources/v2/persons/{}/accounts".format(self.phone)
        response = request.send(path)

        for i in response["accounts"]:
            if int(i["currency"]) == currency:
                balance = float(i["balance"]["amount"])
                break

        else:
            raise exceptions.CurrencyInvalid()

        return balance

    @staticmethod
    def profile():
        """
        Профиль кошелька.

        Returns
        -------
        dict
            Много инфы.
        """
        path = "person-profile/v1/profile/current"
        response = request.send(path)

        return response

    def history(self, rows=20, currency=None, operation=None):
        """
        История платежей
        Warning
        -------
        Максимальная интенсивность запросов истории платежей -
        не более 100 запросов в минуту
         для одного и того же номера кошелька.
        При превышении доступ к API блокируется на 5 минут.

        Parameters
        ----------
        rows : Optional[int]
            Число платежей в ответе, для разбивки отчета на части.
            От 1 до 50, по умолчанию 20.
        currency : optional[int]
            ID валюты в ``number-3 ISO-4217``, с которорой будут показываться
            переводы.
            По умолчанию None, значит будут все переводы
            Например, 643 для российского рубля.
        operation : Optional[str]
            Тип операций в отчете, для отбора.
            Варианты: IN, OUT, QIWI_CARD.
            По умолчанию - ALL.
        
        Returns
        -------
        dict
        """
        params = {"rows": rows}
        path = "payment-history/v2/persons/{}/payments".format(self.phone)

        _history = request.send(path, params=params)

        history = []

        for transaction in _history["data"]:
            if currency:
                if transaction["total"]["currency"] != currency:
                    continue

            if operation:
                if transaction["type"] != operation:
                    continue

            transaction = {
                "account": transaction["account"],
                "comment": transaction["comment"],
                "commission": transaction["commission"],
                "date": transaction["date"],
                "status": transaction["statusText"],
                "sum": transaction["total"],
                "trmTxnId": transaction["trmTxnId"],
                "txnId": transaction["txnId"],
                "type": transaction["type"],
            }
            history.append(transaction)

        return history

    def generate_pay_form(
            self, phone=None, username=None, _sum=None, comment="", currency=643
    ):
        if phone:
            form = 99
        else:
            form = 99999
            phone = username

        url = self.__PAYMENT_FORM_URL + str(form) + "?"
        url += "extra%5B%27account%27%5D={}".format(phone)
        url += "&amountInteger={}&amountFraction=0&".format(_sum)
        url += "extra%5B%27comment%27%5D={}".format(comment)
        url += "&currency={}&blocked[0]=account".format(currency)

        if _sum:
            url += "&blocked[1]=sum"
        if comment:
            url += "&blocked[2]=comment"

        return url

    @staticmethod
    def send(phone, _sum, comment=None, currency=643):
        """
        Перевод средств на другой киви кошелёк.
        Parameters
        ----------
        phone : str
            Номер, куда нужно перевести.
        _sum : currency
            Сумма перевода. Обязательно в рублях
        comment : Optional[str]
            Комментарий к платежу
        currency : optional[int]
            ID валюты в ``number-3 ISO-4217``, с которорой будут показываться
            переводы.
            По умолчанию None, значит будут все переводы
            Например, 643 для российского рубля.

        Returns
        -------
        dict
        :param comment:
        :param _sum:
        :param phone:
        :param currency:
        """
        _json = {
            "id": str(int(time.time() * 1000)),
            "sum": {"amount": str(_sum), "currency": str(currency)},
            "paymentMethod": {"type": "Account", "accountId": "643"},
            "comment": comment,
            "fields": {"account": str(phone)}
        }

        path = "sinap/api/v2/terms/99/payments"
        return request.send(path, method="post", json=_json)

    def search_payment(self, comment, need_sum=0, currency=643):
        payments = self.history(rows=50, currency=currency, operation="IN")
        response = {"status": False}

        _sum = 0
        amount_transactions = 0

        for payment in payments:
            if comment == payment["comment"]:
                amount_transactions += 1
                _sum += payment["sum"]["amount"]

        if (0 == need_sum and 0 < _sum) or (0 < need_sum <= _sum):
            response["sum"] = _sum
            response["status"] = True
            response["amount_transactions"] = amount_transactions

        return response

    def gen_payment(self, _sum=None):
        phone = self.__phone
        comment = random_data.etc.password()
        link = self.generate_pay_form(phone=phone, _sum=_sum, comment=comment)

        response = {"comment": comment, "link": link}
        return response

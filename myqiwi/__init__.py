import time
import requests
import random_data

from transliterate import translit

from . import exceptions


class Wallet:
    warnings = True
    error_on_translit = True

    __API_URl = "https://edge.qiwi.com/"
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


    def __init__(self, token: str, proxy: str=None):
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
        self.__session = requests.Session()
        self.__session.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(token),
        }
        self.__phone = self.profile()["contractInfo"]["contractId"]

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
        method = "funding-sources/v2/persons/{}/accounts".format(self.__phone)
        response = self.__request(method)

        for i in response["accounts"]:

            if int(i["currency"]) == currency:
                balance = float(i["balance"]["amount"])

        return balance

    @property
    def phone(self):
        return self.__phone

    def profile(self):
        """
        Профиль кошелька.

        Returns
        -------
        dict
            Много инфы.
        """
        method = "person-profile/v1/profile/current"
        response = self.__request(method)

        return response

    def history(self, rows=20, currency=None, operation=None):
        """
        История платежей
        Warning
        -------
        Максимальная интенсивность запросов истории платежей - не более 100 запросов в минуту
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
        method = "payment-history/v2/persons/{}/payments".format(self.__phone)

        h = self.__request(method, params=params)

        history = []

        for i in h["data"]:
            if currency:
                if i["total"]["currency"] != currency:
                    continue

            if operation:
                if i["type"] != operation:
                    continue

            transaction = {
                "account": i["account"],
                "comment": i["comment"],
                "commission": i["commission"],
                "date": i["date"],
                "status": i["statusText"],
                "sum": i["total"],
                "trmTxnId": i["trmTxnId"],
                "txnId": i["txnId"],
                "type": i["type"],
            }

            history.append(transaction)

        return history

    def generate_pay_form(
        self, phone=None, username=None, sum=None, comment="", currency=643
    ):
        if phone:
            form = 99
        elif username:
            form = 99999
            phone = username

        url = self.__PAYMENT_FORM_URL + str(form) + "?"
        url += "extra%5B%27account%27%5D={}&amountInteger={}".format(phone, sum)
        url += "&amountFraction=0&extra%5B%27comment%27%5D={}".format(comment)
        url += "&currency={}&blocked[0]=account".format(currency)

        if sum:
            url += "&blocked[1]=sum"
        if comment:
            url += "&blocked[2]=comment"

        return url

    def send(self, phone, sum, comment=None, currency=643):
        """
        Перевод средств на другой киви кошелёк.
        Parameters
        ----------
        phone : str
            Номер, куда нужно перевести.
        sum : float
            Сумма перевода. Обязательно в рублях
        comment : Optional[str]
            Комментарий к платежу
        
        Returns
        -------
        dict
        """
        postjson = {
            "id": str(int(time.time() * 1000)),
            "sum": {"amount": str(sum), "currency": str(currency)},
            "paymentMethod": {"type": "Account", "accountId": "643"},
            "comment": comment,
            "fields": {"account": str(phone)},
        }

        method = "sinap/api/v2/terms/99/payments"
        return self.__request(method, method="post", _json=postjson)

    def search_payment(self, comment, need_sum=0, currency=643):
        payments = self.history(rows=50, currency=currency, operation="IN")
        response = {"status": False}

        sum = 0
        amount_transactions = 0

        for payment in payments:
            if comment == payment["comment"]:
                amount_transactions += 1
                sum += payment["sum"]["amount"]

        if (0 == need_sum and 0 < sum) or (0 < need_sum and need_sum <= sum):
            response["sum"] = sum
            response["status"] = True
            response["amount_transactions"] = amount_transactions

        return response

    def gen_payment(self, sum):
        phone = self.__phone
        comment = random_data.etc.password()
        link = self.generate_pay_form(phone=phone, sum=sum, comment=comment)

        response = {"comment": comment, "link": link}
        return response


    def __request(self, method_name, method="get", params=None, _json=None):
        url = self.__API_URl + method_name

        if "get" == method:
            response = self.__session.get(url, params=params, json=_json)

        elif "post" == method:
            response = self.__session.post(url, params=params, json=_json)

        if self.warnings:
            error_text = response.text
            if self.error_on_translit:
                error_text = translit(error_text, "ru", reversed=True)

            if 400 == response.status_code:
                raise exceptions.ArgumentError(error_text)

            if 401 == response.status_code:
                raise exceptions.InvalidToken("Invalid token")

            if 403 == response.status_code:
                raise exceptions.NotHaveEnoughPermissions(error_text)

            if 404 == response.status_code:
                raise exceptions.NoTransaction(error_text)

        return response.json()
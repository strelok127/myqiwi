import time
import random
import requests

from myqiwi import errors


from .__version__ import __title__, __description__, __url__, __version__
from .__version__ import __author__, __author_email__, __license__


class Wallet:
    warnings = True
    api_url = "https://edge.qiwi.com/"
    """ 
    This is Wallet Class
    Methods:
        balance
        profile
        history
        generate_pay_form
        send
    """

    def __init__(self, token: str, phone=None):
        """
        Visa QIWI Кошелек
        Parameters
        ----------
        token : str
            `Ключ Qiwi API` пользователя.
        number : Optional[str]
            Номер для указанного кошелька.
            По умолчанию - ``None``.
            Если не указан, стория работать не будет.
        """
        if None != phone:
            if "+" == phone[:1]:
                phone = phone[1:]

            if False == phone.isdigit():
                raise Exception("Invalid phone")

        self.phone = phone
        self.token = token

        self._session = requests.Session()
        self._session.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(token),
        }

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
        self.__check_phone()

        method = "funding-sources/v2/persons/{}/accounts".format(self.phone)
        response = self.__request(method)

        for i in response["accounts"]:

            if int(i["currency"]) == currency:
                balance = float(i["balance"]["amount"])

        return balance

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

        profile = {
            "authInfo": {
                "boundEmail": response["authInfo"]["boundEmail"],
                "ip": response["authInfo"]["ip"],
            },
            "contractInfo": {
                "blocked": response["contractInfo"]["blocked"],
                "creationDate": response["contractInfo"]["creationDate"],
                "identification": response["contractInfo"]["identificationInfo"],
                "nickname": response["contractInfo"]["nickname"],
                "smsNotification": response["contractInfo"]["smsNotification"],
            },
            "userInfo": {
                "defaultPayCurrency": response["userInfo"]["defaultPayCurrency"],
                "language": response["userInfo"]["language"],
                "operator": response["userInfo"]["operator"],
                "phoneHash": response["userInfo"]["phoneHash"],
            },
        }

        return profile

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
        self.__check_phone()

        params = {"rows": rows}
        method = "payment-history/v2/persons/{}/payments".format(self.phone)

        h = self.__request(method, params=params)

        history = []

        for i in h["data"]:
            if currency != None:
                if i["total"]["currency"] != currency:
                    continue

            if operation != None:
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

    def generate_pay_form(self, number=None, username=None, sum=None, comment=""):
        if number != None:
            form = 99
        elif username != None:
            form = 99999
            number = username

        a = "https://qiwi.com/payment/form/{}?extra%5B%27account%27%5D=".format(form)
        b = str(number) + "&amountInteger=" + str(sum) + "&amountFraction=0"
        c = "&extra%5B%27comment%27%5D=" + comment + "&currency=643"
        d = "&blocked[0]=account"
        a = a + b + c + d

        if None != sum:
            a += "&blocked[1]=sum"
        if comment != "":
            a += "&blocked[2]=comment"

        return a

    def gen_comment(self, length=10):
        """
        Генерация комментария к переводу, для его идентификации.

        -------
        str
        """
        symbols = list("1234567890abcdefghinopqrstuvyxwzABCDEFGHIGKLMNOPQUVYXWZ")
        comment = "".join([random.choice(symbols) for x in range(length)])

        return comment  # Возращается сгенерированный комментарий

    def send(self, phone, sum, comment="", currency=643):
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
        # postjson = {
        #     "id": str(int(time.time() * 1000)),
        #     "sum": {
        #         "amount": str(sum),
        #         "currency": str(currency),
        #     },
        #     "paymentMethod": {
        #         "type": "Account",
        #         "accountId": "643",
        #     },
        #     "comment": comment,
        #     "fields": {
        #         "account": ""
        #     },
        # }
        postjson = {
            "id": str(int(time.time() * 1000)),
            "sum": {"amount": str(sum), "currency": str(currency)},
            "paymentMethod": {"type": "Account", "accountId": "643"},
            "comment": comment,
            "fields": {"account": str(phone)},
        }

        method = "sinap/api/v2/terms/99/payments"
        return self.__request(method, method="post", _json=postjson)



    def search_payment(self, need_sum=0, need_comment=""):
        """
        In future
        """
        pass



    def __check_phone(self):
        if None == self.phone:
            raise errors.NeedPhone("For this function need phone")


    def __request(self, method_name, method="get", params=None, _json=None):
        url = self.api_url + method_name

        if "get" == method:
            response = self._session.get(url, params=params, json=_json)

        elif "post" == method:
            response = self._session.post(url, params=params, json=_json)

        if self.warnings:
            if 400 == response.status_code:
                raise errors.ArgumentError(response.text)

            elif 401 == response.status_code:
                raise errors.InvalidToken("Invalid token")

            elif 403 == response.status_code:
                raise errors.NotHaveEnoughPermissions(response.text)

            elif 404 == response.status_code:
                raise errors.NoTransaction(response.text)

        return response.json()

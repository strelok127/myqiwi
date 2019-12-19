import json
import time

from myqiwi import apihelper

from .__version__ import __title__, __description__, __url__, __version__
from .__version__ import __author__, __author_email__


class Wallet:
    """ This is Wallet Class
    Methods:
        balance
        profile
        history
        generate_pay_form
        send
    """
    def __init__(self, token, number=None):
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

        if isinstance(number, str): 
            self.num = number.replace("+", "")
            if self.num.startswith("8") == True:
                self.num = "7" + self.num[1:]
        self.headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': "Bearer " + token
                        }       
        self.token = token


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
        method = "funding-sources/v2/persons/{}/accounts".format(self.num)
        r = apihelper.make_request(method, self.headers)
       
        b = 0
        for i in r["accounts"]:
        
            if i["currency"] == currency:
                balance = i["balance"]["amount"]
            b += 1

        return balance

    def profile(self):
        """
        Профиль кошелька.

        Returns
        -------
        dict
            Много инфы.
        """
        p = apihelper.make_request("person-profile/v1/profile/current",
                                  self.headers)

        profile = {
            "authInfo": 
                {
                "boundEmail": p["authInfo"]["boundEmail"],
                "ip": p["authInfo"]["ip"]
                },
            "contractInfo": 
                {
                "blocked": p["contractInfo"]["blocked"],
                "creationDate": p["contractInfo"]["creationDate"],
                "identification": p["contractInfo"]["identificationInfo"],
                "nickname": p["contractInfo"]["nickname"],
                "smsNotification": p["contractInfo"]["smsNotification"]
                },
            "userInfo": 
                {
                "defaultPayCurrency": p["userInfo"]["defaultPayCurrency"],
                "language": p["userInfo"]["language"],
                "operator": p["userInfo"]["operator"],
                "phoneHash": p["userInfo"]["phoneHash"]
                }
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
        params = {
                    "rows": rows
                 }
        method = "payment-history/v2/persons/{}/payments".format(self.num)

        h = apihelper.make_request(method, self.headers, params=params)

        history = {}
        a = 0

        for i in h["data"]:
            if currency != None:
                if i["total"]["currency"] != currency: continue

            if operation != None:
                if i["type"] != operation: continue

            d = {   
                "account": i["account"],
                "comment": i["comment"],
                "commission": i["commission"],
                "date": i["date"],
                "status": i["statusText"],
                "sum": i["total"],
                "trmTxnId": i["trmTxnId"],
                "txnId": i["txnId"],
                "type": i["type"]
                }

            history[a] = d
            a += 1

        return history

    def generate_pay_form(self, number, sum="", comment=""):
        a = "https://qiwi.com/payment/form/99?extra%5B%27account%27%5D="
        b = str(number) + "&amountInteger=" + str(sum) +"&amountFraction=0"
        c = "&extra%5B%27comment%27%5D=" + comment + "&currency=643"
        d = "&blocked[0]=account"
        a = a + b + c + d

        if sum != "":
            a += "&blocked[1]=sum"
        if comment != "":
            a += "&blocked[2]=comment"
        
        return a

    def send(self, number, sum, comment=None):
        """
        Перевод средств на другой киви кошелёк.

        Parameters
        ----------
        number : str
            Номер, куда нужно перевести.
        sum : int
            Сумма перевода. Обязательно в рублях
        comment : Optional[str]
            Комментарий к платежу
        
        Returns
        -------
        dict
        """
        postjson = json.loads('{"id":"","sum": {"amount":"","currency":"643"}, "paymentMethod":{"type":"Account","accountId":"643"}, "comment":"","fields":{"account":""}}')
        
        postjson['id'] = str(int(time.time() * 1000))
        postjson['sum']['amount'] = sum
        postjson['fields']['account'] = str(number)
        postjson['comment'] = comment
        


        method = "sinap/api/v2/terms/99/payments"
        r = apihelper.make_request(method, self.headers, method="post", 
                                    js=postjson)

        return r





import os
import pytest

import myqiwi

token = os.environ.get("QIWI_TOKEN")
print(token)

if token:
    qiwi = myqiwi.Wallet(token)
else:
    qiwi = None


@pytest.mark.skipif(qiwi is None, reason="")
def test_get_phone():
    phone = qiwi.number

    assert isinstance(phone, int)


@pytest.mark.skipif(qiwi is None, reason="")
def test_balance():
    balance = qiwi.balance()

    assert 0 <= balance
    assert isinstance(balance, float)


@pytest.mark.skipif(qiwi is None, reason="")
def test_profile():
    profile = qiwi.profile()

    assert isinstance(profile, dict)

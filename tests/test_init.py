from utils import _algod_client


def test_algod():
    print(_algod_client().health())

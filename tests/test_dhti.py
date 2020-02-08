import pytest
from dhti import *

@pytest.fixture(scope='function')
def new_dhti():
    cfg = DHTInterface()
    IP = input("What IP? ")
    port = input("What port? ")
    cfg.set_connection(IP,port)
    yield cfg
    cfg.close_connection()


def test_exists(new_dhti):
    cfg = new_dhti

    key_that_doesnt_exist = 'Isuredonotexistinthesystem'

    exi = cfg.exists(key_that_doesnt_exist)
    assert exi == 'F'


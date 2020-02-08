import pytest
from tfbvDHT.dhti import *

IPPORTFILENAME = '/home/tyler23/Documents/school/projects_class/Distributed-Hash-Table/tests/IPPORT.txt'

@pytest.fixture(scope='function')
def new_dhti():
    cfg = DHTInterface()
    cfg.read_and_set_connection(IPPORTFILENAME)
    yield cfg
    cfg.close_connection()


def test_exists(new_dhti):
    cfg = new_dhti

    key_that_doesnt_exist = 'Isuredonotexistinthesystem'

    exi = cfg.exists(key_that_doesnt_exist)
    assert exi == 'F'


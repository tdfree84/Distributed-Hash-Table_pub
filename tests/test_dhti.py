import pytest
from tfjfbvDHT.dhti import *

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

def test_insert(new_dhti):
    cfg = new_dhti

    key_for_insert = 'iamtestkey'
    value_for_insert = 'testingtesting'

    ins = cfg.insert(key_for_insert,value_for_insert)

    cfg.read_and_set_connection(IPPORTFILENAME)
    exi = cfg.exists(key_for_insert)
    assert ins == 'T'
    assert exi == 'T'

def test_remove(new_dhti):
    cfg = new_dhti

    key_for_insert = 'iamtestkey'
    value_for_insert = 'testingtesting'

    ins = cfg.insert(key_for_insert,value_for_insert)

    cfg.read_and_set_connection(IPPORTFILENAME)
    exi = cfg.exists(key_for_insert)
    assert ins == 'T'
    assert exi == 'T'

    cfg.read_and_set_connection(IPPORTFILENAME)
    rem = cfg.remove(key_for_insert)

    cfg.read_and_set_connection(IPPORTFILENAME)
    exi = cfg.exists(key_for_insert)
    assert exi == 'F'
    assert rem == 'T'

def test_get(new_dhti):
    cfg = new_dhti

    key_for_insert = 'iamtestkey'
    value_for_insert = 'testingtesting'

    ins = cfg.insert(key_for_insert,value_for_insert)

    cfg.read_and_set_connection(IPPORTFILENAME)
    exi = cfg.exists(key_for_insert)
    assert ins == 'T'
    assert exi == 'T'

    cfg.read_and_set_connection(IPPORTFILENAME)
    get = cfg.get(key_for_insert)

    assert get[0] == 'T'
    assert get[1].decode() == value_for_insert

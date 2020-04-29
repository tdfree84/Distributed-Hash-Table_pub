import pytest
from tfjfbvDHT.dhti import *

IPPORTFILENAME = '/home/tyler23/Documents/school/projects_class/Distributed-Hash-Table/tests/IPPORT.txt'

@pytest.fixture(scope='function')
def new_dhti():
    cfg = DHTInterface(ipport_file=IPPORTFILENAME)
    yield cfg
    cfg.close_connection()

def test_owns(new_dhti):
    cfg = new_dhti
    with open(IPPORTFILENAME,'r') as f:
        line = f.readline().strip()
    realIP = line.split(':')[0]
    realPort = int(line.split(':')[1])
    owns_key = realIP + ':' + str(realPort)
     
    own = cfg.owns(owns_key)

    assert own == owns_key

def test_exists(new_dhti):
    cfg = new_dhti

    key_for_insert = 'iamtestkey'
    value_for_insert = 'testingtesting'

    ins = cfg.insert(key_for_insert,value_for_insert)

    exi = cfg.exists(key_for_insert)
    assert exi == 'T'

def test_fail_exists(new_dhti):
    cfg = new_dhti

    key_that_doesnt_exist = 'Isuredonotexistinthesystem'

    exi = cfg.exists(key_that_doesnt_exist)
    assert exi == 'F'

def test_insert(new_dhti):
    cfg = new_dhti

    key_for_insert = 'iamtestkeyasdf;lkj'
    value_for_insert = 'testingtesting'

    ins = cfg.insert(key_for_insert,value_for_insert)

    exi = cfg.exists(key_for_insert)
    assert ins == 'T'
    assert exi == 'T'

def test_remove(new_dhti):
    cfg = new_dhti

    key_for_insert = 'iamtestkey9428ewfijo'
    value_for_insert = 'testingtesting'

    ins = cfg.insert(key_for_insert,value_for_insert)

    exi = cfg.exists(key_for_insert)
    assert ins == 'T'
    assert exi == 'T'

    rem = cfg.remove(key_for_insert)

    exi = cfg.exists(key_for_insert)
    assert exi == 'F'
    assert rem == 'T'

def test_fail_remove(new_dhti):
    cfg = new_dhti

    key_that_doesnt_exist = 'Isuredonotexistinthesystem'

    rem = cfg.remove(key_that_doesnt_exist)
    assert rem == 'F'

def test_get(new_dhti):
    cfg = new_dhti

    key_for_insert = 'iamtestkey'
    value_for_insert = 'testingtesting'

    ins = cfg.insert(key_for_insert,value_for_insert)

    exi = cfg.exists(key_for_insert)
    assert ins == 'T'
    assert exi == 'T'

    get = cfg.get(key_for_insert)

    assert get[0] == 'T'
    assert get[1].decode() == value_for_insert

def test_fail_get(new_dhti):
    cfg = new_dhti

    key_for_get_dne = 'iamtestgetkeythatdoesntexistatall'

    get = cfg.get(key_for_get_dne)

    assert get[0] == 'F'

# Welcome to Tyler and Jack's DHT

#### Dependencies
* python3 == 3.6.9
* pytest == 5.3.5
* pipenv, version 2018.11.26
* git version 2.17.1

#### Prerequisites
- `sudo apt install git python3-pip`
- `pip3 install pipenv`

#### Setup
1. Clone `https://github.com/tdfree84/Distributed-Hash-Table.git`
2. `cd` into directory
3. `pipenv install`
3. `pipenv shell` -> begin development

#### Running
* In order for our implementation to work properly, the `peerProfile.py`, `net_functions.py`, `hash_functions.py` files are required
* To start a **seed client**, simply enter: `python3 tfbvDHT/bvDHT.py`
* For any **connecting clients**, use format: `python3 tfbvDHT/bvDHT.py IP Port`
* To interact with the DHT locally, use the provided menu you will see upon start

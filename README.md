# Welcome to Tyler and Jack's DHT

#### Dependencies
* python3 == 3.8.2
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
* To start a **seed client**, simply enter: `python3 tfjfbvDHT/bvDHT.py`
* For any **connecting clients**, use format: `python3 tfjfbvDHT/bvDHT.py IP Port`
* To interact with the DHT locally, use the provided menu you will see upon start

**Definition of a distributed hash table from [Wikipedia](https://en.wikipedia.org/wiki/Distributed_hash_table):**

A distributed hash table (DHT) is a class of a decentralized distributed system that provides a lookup service similar to a hash table:(key, value) pairs are stored in a DHT, and any participating node can efficiently retrieve the value associated with a given key. Keys are unique identifiers which map to particular values, which in turn can be anything from addresses, to documents, to arbitrary data.[1] Responsibility for maintaining the mapping from keys to values is distributed among the nodes, in such a way that a change in the set of participants causes a minimal amount of disruption. This allows a DHT to scale to extremely large numbers of nodes and to handle continual node arrivals, departures, and failures. 

from enum import Enum

from pymongo import MongoClient


class Mode(Enum):
    ALL = 'all'
    PARTIAL = 'partial'


client = MongoClient(port=27017, username='root', password='example')
record_db = client.record


def insert(value):
    if check_dup(value['name'], value['date'].date()):
        pass
    else:
        record_db.history.insert_one(value)


def find(**kwargs):
    mode = kwargs.get('mode', None)
    if mode == Mode.ALL:
        return record_db.history.find({})
    if mode == Mode.PARTIAL:
        start = kwargs.get('start', None)
        end = kwargs.get('end', None)
        return record_db.history.find({'date': {'$gte': start, '$lt': end}})
    index = kwargs.get('index', None)
    key = kwargs.get('key', None)
    return record_db.history.find({f'{index}': key})


def find_all():
    return find(mode=Mode.ALL)


def find_date_range(start, end):
    return find(start=start, end=end, mode=Mode.PARTIAL)


def check_dup(name, date):
    for i in find(index='name', key=name):
        if i['date'].date() == date:
            return True
    return False
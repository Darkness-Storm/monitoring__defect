from dataclasses import dataclass, asdict

from peewee import DatabaseError

from config import TMPDIR

from app.models import Status, Location, Component, Organisation, ModelBus


@dataclass
class MyError():

    message: str = ''
    description: str = ''
    validate: bool = False


def is_ajax(request):
    try:
        request.headers['X-Requested-With']
    except KeyError:
        return False
    return True
DEFAULT_CHOICE = (0, 'Ничего не выбрано')

def status_choices():
    try:
        return [(s.id, s.descr) for s in Status.select()]
    except DatabaseError:
        return [DEFAULT_CHOICE]
        

def location_choices():
    try:
        return [(l.id, l.descr) for l in Location.select()]
    except DatabaseError:
        return [DEFAULT_CHOICE]


def component_choices():
    try:
        return [(s.id, s.get_full_name()) for s in Component.select().order_by(Component.number)]
    except DatabaseError:
        return [DEFAULT_CHOICE]


def organisation_choices():
    try:
        return [(s.id, s.get_short_name()) for s in Organisation.select().order_by(Organisation.descr)]
    except DatabaseError:
        return [DEFAULT_CHOICE]


def models_choices():
    try:
        return [(m.id, m.descr) for m in ModelBus.select().order_by(ModelBus.descr)]
    except DatabaseError:
        return [DEFAULT_CHOICE]

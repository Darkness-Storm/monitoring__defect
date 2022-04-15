import os
import datetime

from peewee import Model, BlobField, CharField, ForeignKeyField, \
    FloatField,  IntegerField, AutoField, ManyToManyField, \
    BooleanField, DateField, DateTimeField, OperationalError
from flask import current_app, url_for, abort
from playhouse.flask_utils import FlaskDB

from config import TMPDIR


__all__ = [
    'db_wrapper',
    'Attachment',
    'Organisation',
    'OrganisationtAttachments',
    'Component',
    'Status',
    'Location',
    'ModelBus',
    'Contact',
    'Problem',
    'ProblemModels',
    'CorrectiveAction',
    'ProblemAttachment',
    'create_table',
    'drop_table'
]


# database = SqliteExtDatabase(config.sqlite_connection_string, pragmas=(
#     ('cache_size', -1024 * 64),  # 64MB page-cache.
#     ('journal_mode', 'wal')  # Use WAL-mode (you should always use this!).


class MyDB(FlaskDB):

    def connect_db(self):
        try:
            self.database.connect()
        except OperationalError as e:
            #error = f'Произошла ошибка обращения к базе данных. Описание ошибки: {e.args[0]}'
            abort(500, f'Произошла ошибка обращения к базе данных. Описание ошибки: {e.args[0]}')


db_wrapper = MyDB()
#db_wrapper = FlaskDB()


def get_url_attachment(file_name):
    return url_for('static', filename=TMPDIR + r'/' + file_name)


def get_full_filename(file_name):
    return os.path.join(current_app.static_folder, TMPDIR, file_name)


class BaseModel(db_wrapper.Model):

    class Meta:
        database = db_wrapper.database


class Attachment(BaseModel):

    data = BlobField(null=True)
    db_name = CharField(column_name='dbName', null=True)
    descr = CharField(verbose_name='имя файла')
    extension = CharField(verbose_name='расширение', column_name='extesion')

    class Meta:
        table_name = 'Attachements'

    def get_filename(self):
        return os.path.splitext(self.descr)[0] + self.get_extension()

    def get_extension(self):
        if self.extension[0] == '.':
            return self.extension
        else:
            return '.' + self.extension

    def get_tmp_filename(self):
        today = datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S")
        return str(self.id) + today + self.get_extension()

    def write_attachment_for_photo(self):
        file = self.write_attachment_tmpdir()
        return get_url_attachment(file)

    def write_attachment_for_send(self):
        file = self.write_attachment_tmpdir()
        return file, get_full_filename(file)

    def write_attachment_tmpdir(self):
        file_name = self.get_filename()
        try:
            output = open(get_full_filename(file_name), 'wb')
            output.write(self.data)
        except FileExistsError:
            return file_name
        except OSError as e:
        #     if e.args[0] == 2:
        #         if not os.path.exists(tmp_dir):
        # os.makedirs(tmp_dir)
            current_app.logger.error(f'Не удалось записать файл: ошибка - {e.args[0]}: {e.args[1]}. Id = {self.id}')
            file_name = ''
        return file_name


class Organisation(BaseModel):

    address = CharField(verbose_name='Улица, дом, офис', null=True)
    business = CharField(verbose_name='Направление деятельности', null=True)
    consumer = CharField(verbose_name='Основные потребители', null=True)
    country = CharField(verbose_name='Государство', null=True)
    descr = CharField(verbose_name='Наименование')
    legal_address = CharField(verbose_name='Адрес (юридический)', null=True)
    legal_country = CharField(
        verbose_name='Государство (юридическое)', null=True)
    legal_form = CharField(verbose_name='Юридическая форма')
    legal_sity = CharField(verbose_name='Город (юридический)')
    legal_state = CharField(
        verbose_name='Область (штат) (юридическая)', null=True)
    legal_zip = CharField(verbose_name='Индекс (юридический)', null=True)
    mail = CharField(verbose_name='Почта', null=True)
    number_employees = CharField(verbose_name='Численность', null=True)
    phone = CharField(verbose_name='Телефон', null=True)
    site = CharField(verbose_name='Сайт', null=True)
    sity = CharField(verbose_name='Город', null=True)
    state = CharField(verbose_name='Область (штат)', null=True)
    zip_code = CharField(verbose_name='Индекс', column_name='zip', null=True)
    audit_assess = FloatField(null=True)
    audit_date = DateTimeField(null=True)
    audit_id = IntegerField(null=True)
    attachments = ManyToManyField(Attachment, backref='organisations')

    class Meta:
        table_name = 'Organisation'

    def get_short_name(self):
        return f'{self.legal_form} "{self.descr}"'

    def get_short_name1(self):
        return self.legal_form + ' ' + self.descr


class Contact(BaseModel):
    full_name = CharField(verbose_name='ФИО')
    last_update = DateTimeField(verbose_name='Последнее обновление')
    mail = CharField(null=True)
    phone = CharField(verbose_name='телефон, факс', null=True)
    position = CharField(verbose_name='Должность', null=True)
    organisation = ForeignKeyField(column_name='id_org',
                                   field='id', model=Organisation, backref='contacts')

    class Meta:
        table_name = 'Contacts'


OrganisationtAttachments = Organisation.attachments.get_through_model()


class Component(BaseModel):
    descr = CharField(column_name='Наименование')
    number = CharField(column_name='Номер')

    class Meta:
        table_name = 'Components'

    def get_full_name(self):
        return self.number + ' - ' + self.descr


class Status(BaseModel):
    char = CharField(null=True)
    descr = CharField(verbose_name='Наименование')
    img = BlobField(null=True)

    class Meta:
        table_name = 'Status'


class Location(BaseModel):
    descr = CharField(verbose_name='Наименование')

    class Meta:
        table_name = 'Locations'


class ModelBus(BaseModel):
    descr = CharField(verbose_name='Модель ТС')

    class Meta:
        table_name = 'Models'


class Problem(BaseModel):
    id = AutoField()
    comment = CharField(verbose_name='Примечание', null=True)
    component = ForeignKeyField(model=Component,
                                verbose_name='Компонент',
                                column_name='component',
                                field='id', null=True)
    date_created = DateTimeField(
        verbose_name='Дата создания', default=datetime.datetime.now())
    date_detection = DateTimeField(verbose_name='Дата обнаружения', null=True)
    detailed_descr = CharField(verbose_name='Подробное описание', null=True)
    lider = CharField(verbose_name='Ответственный', null=True)
    location_detail = CharField(verbose_name='Место обнаружения', null=True)
    location_detection = ForeignKeyField(verbose_name='Место обнаружения',
                                         column_name='location_detection',
                                         field='id',
                                         model=Location,
                                         null=True)
    main_action = CharField(verbose_name='Основное мероприятие', null=True)
    root_cause = CharField(verbose_name='Коренная причина', null=True)
    short_descr = CharField(verbose_name='Краткое описание')
    status = ForeignKeyField(verbose_name='Статус проблемы', column_name='status',
                             field='id', model=Status, null=True)
    organisation = ForeignKeyField(model=Organisation,
                                   verbose_name='Поставщик',
                                   column_name='organisation',
                                   field='id',
                                   null=True)
    models = ManyToManyField(ModelBus, backref='problems')

    class Meta:
        table_name = 'Problems'

    def __str__(self):
        return f'{self.id} - {self.short_descr}'

    def get_models_to_string(self):
        str_models = ""
        for model in self.models:
            if not str_models:
                str_models = model.descr
            else:
                str_models += "; " + model.descr
        return str_models


ProblemModels = Problem.models.get_through_model()


class CorrectiveAction(BaseModel):
    comment = CharField(verbose_name='Примечание', null=True)
    deadline = DateTimeField(verbose_name='Срок')
    descr = CharField(verbose_name='Описание')
    executor = CharField(verbose_name='Исполнитель')
    serial = CharField(verbose_name='№ п/п', null=True)
    status = ForeignKeyField(verbose_name='Статус', column_name='status',
                             field='id', model=Status)
    problem = ForeignKeyField(backref='actions',
                              column_name='problem',
                              field='id',
                              model=Problem)

    class Meta:
        table_name = 'CorrectiveActions'


class ProblemAttachment(BaseModel):
    id = AutoField()
    attachment = ForeignKeyField(column_name='id_att',
                                 field='id', model=Attachment, null=True)
    problem = ForeignKeyField(
        column_name='id_problem', field='id', model=Problem, null=True)
    photo_new = BooleanField()
    photo_old = BooleanField()

    class Meta:
        table_name = 'ProblemAttachement'
        primary_key = False


MY_MODELS = [Attachment, Organisation, Component, Status, Location, ModelBus, Contact, Problem, 
                ProblemModels, CorrectiveAction, ProblemAttachment, OrganisationtAttachments]

def create_table(db):
    with db:
        db.create_tables(MY_MODELS)


def drop_table(db):
    with db:
        db.drop_tables(MY_MODELS)

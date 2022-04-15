from wtforms import StringField, IntegerField, validators, DateField, SelectField, \
    TextAreaField, SelectMultipleField, FloatField, HiddenField
from wtforms.widgets import html5, html_params

from flask_wtf import FlaskForm

from app.models import *
from app.utils import status_choices, location_choices, component_choices, \
    organisation_choices, models_choices


__all__ = ['CorrActionForm',
           'ProblemForm',
           'ComponentForm',
           'AddressForm',
           'CommonContactForm',
           'ContactForm',
        #    'AuditForm',
        #    'ReportForm',
           'OrganisationForm'
           ]


FORMAT_DATE = '%d-%m-%Y'


def select_multi_checkbox(field, ul_class='', **kwargs):
    kwargs.setdefault('type', 'checkbox')
    field_id = kwargs.pop('id', field.id)
    html = [f'<ul {html_params(id=field_id, class_=ul_class)}>']
    for value, label, checked in field.iter_choices():
        choice_id = f'{field_id}-{value}'
        options = dict(kwargs, name=choice_id, value=value, id=choice_id)
        if checked:
            options['checked'] = 'checked'
        html.append(f'<li><input {html_params(**options)}/> ')
        html.append(f'<label for="{choice_id}">{label}</label></li>')
    html.append('</ul>')
    return ''.join(html)


class NonValidatingSelectMultipleField(SelectMultipleField):
    """
    Attempt to make an open ended select multiple field that can accept dynamic
    choices added by the browser.
    """

    def pre_validate(self, form):
        pass


class CorrActionForm(FlaskForm):

    # id = IntegerField()
    serial = StringField(
        '№', validators=[validators.Length(max=10, message="Поле не должно быть длиннее 10 символов")])
    descr = TextAreaField('Описание', validators=[
        validators.Length(max=255, message="Поле не должно быть длиннее 255 символов"), validators.InputRequired(message="Введите описание")])
    executor = StringField('Исполнитель', validators=[
                           validators.InputRequired(message='Поле "Исполнитель" обязательно для заполнения!')])
    deadline = DateField('Срок исполнения', validators=[
                         validators.InputRequired(message="Заполните срок исполнения")], format=FORMAT_DATE)  # 'data-date-format': 'dd-mm-yyyy'  format=FORMAT_DATE, render_kw={'data-provide': 'datepicker'}
    comment = StringField('Примечание', validators=[
        validators.Length(max=255, message='Поле не должно быть длиннее 255 символов')])
    status_id = SelectField('Статус', coerce=int)
    problem = IntegerField()

    def populate_choice(self):
        self.status_id.choices = status_choices()


class ProblemForm(FlaskForm):

    # id = IntegerField()
    component_id = SelectField('Компонент', coerce=int)
    organisation_id = SelectField('Организация', coerce=int)
    short_descr = TextAreaField('Краткое описание', validators=[
        validators.InputRequired('Краткое описание обязательно для заполнения!')])
    detailed_descr = TextAreaField('Подробное описание')
    location_detection_id = SelectField(
        'Место обнаружения', coerce=int)
    location_detail = TextAreaField('Место')
    root_cause = TextAreaField('Коренная причина')
    status_id = SelectField(
        'Статус', default=2, coerce=int)
    comment = TextAreaField('Примечание')
    lider = TextAreaField('Ответственный')
    main_action = TextAreaField('Основное действие')
    date_detection = DateField('Дата обнаружения',  validators=[
        validators.InputRequired('Дата обнаружения обязательно для заполнения!')], format=FORMAT_DATE)
    models = NonValidatingSelectMultipleField('Модель')  # , widget=select_multi_checkbox)  # render_kw={'class': 'form-check'},
    # models = HiddenField('Модель')

    def populate_choice(self):
        
        self.component_id.choices = component_choices()
        self.organisation_id.choices = organisation_choices()
        self.models.choices = models_choices()
        self.status_id.choices = status_choices()
        self.location_detection_id.choices = location_choices()




class ComponentForm(FlaskForm):
    """docstring for ComponentForm"FlaskForm"""

    descr = StringField('Наименование', validators=[
        validators.Length(
            max=255, message="Поле не должно быть длиннее 255 символов"),
        validators.InputRequired(message="Введите описание")])
    number = StringField('Номер', validators=[
        validators.Length(max=255, message="Поле не должно быть длиннее 255 символов")])


class OrganisationForm(FlaskForm):
    legal_form = StringField('Форма', validators=[
        validators.InputRequired(message='Введите юридическую форму предприятия!!')])
    descr = StringField('Наименование', validators=[
        validators.InputRequired(message='Введите наименование!!')])
    legal_sity = StringField('Город', validators=[
        validators.InputRequired(message='Введите город!!')])


class AddressForm(FlaskForm):

    legal_address = StringField('Адрес')
    legal_country = StringField('Государство')
    legal_sity = StringField('Город', validators=[
        validators.InputRequired(message='Введите город')])
    legal_state = StringField('Область (штат)')
    legal_zip = StringField('Индекс')
    address = StringField('Адрес')
    country = StringField('Государство')
    sity = StringField('Город')
    state = StringField('Область (штат)')
    zip_code = StringField('Индекс')
    org_id = IntegerField()


class CommonContactForm(FlaskForm):

    phone = StringField('Телефон / факс')
    mail = StringField('Электронная почта')
    site = StringField('Сайт')


class ContactForm(FlaskForm):

    full_name = StringField('ФИО', validators=[
        validators.InputRequired(message='Введите ФИО')])
    # last_update = DateField('Последнее обновление')
    mail = StringField('Электронная почта')
    phone = StringField('телефон, факс')
    position = StringField('Должность')
    organisation = IntegerField()


# class AuditForm(FlaskForm):

#     process_descr = TextAreaField('Процесс', validators=[
#         validators.InputRequired(message='Введите наименование процесса')])
#     organisation_id = IntegerField()
#     date_start = DateField('Дата начала', widget=html5.DateInput())
#     date_end = DateField('Дата окончания', widget=html5.DateInput())
#     audit_type_id = SelectField(
#         'Тип', choices=audittype_choices(), coerce=int, validate_choice=False)
#     level = SelectField('Уровень', choices=level_choices(), coerce=int,
#                         validate_choice=False)
#     other = StringField('Прочее')
#     total = FloatField('Общая оценка', validators=[validators.Optional()])
#     auditors = NonValidatingSelectMultipleField('Аудиторы', choices=auditor_choices(
#     ), validate_choice=False)

choices_reports = [(1, 'Было-стало')]


# class ReportForm(FlaskForm):

#     r_reports = SelectField('Отчет', choices=choices_reports)
#     r_date_start = DateField('Дата начала', format=FORMAT_DATE, validators=[
#                              validators.Optional()])
#     r_date_end = DateField('Дата окончания', format=FORMAT_DATE, validators=[
#                            validators.Optional()])
#     r_models = NonValidatingSelectMultipleField(
#         'Модель', choices=models_choices(), validate_choice=False, render_kw={'data-live-search': 'true'})
#     r_component = NonValidatingSelectMultipleField(
#         'Компонент', choices=component_choices(), validate_choice=False, render_kw={'data-live-search': 'true'})
#     r_organisation = NonValidatingSelectMultipleField(
#         'Организация', choices=organisation_choices(), validate_choice=False, render_kw={'data-live-search': 'true'})
#     r_location_detection = NonValidatingSelectMultipleField(
#         'Место обнаружения', choices=location_choices(), validate_choice=False)
#     r_status = NonValidatingSelectMultipleField(
#         'Статус',  validate_choice=False)
#     r_lider = TextAreaField('Ответственный', validators=[
#                             validators.Optional()])
#     r_location_detail = TextAreaField('Детально место', validators=[
#         validators.Optional()])

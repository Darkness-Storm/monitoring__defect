import os
from typing import Union, Tuple, List
import datetime
from collections import namedtuple

import win32com.client as win32
import pythoncom

from flask import current_app, abort, render_template, url_for

from peewee import PeeweeException, DoesNotExist, fn
from playhouse.shortcuts import model_to_dict, dict_to_model

#from app import app
from app.forms import *
from app.models import *
# from app.paginate import *


__all__ = ['add_attachment_to_problem',
        #    'delete_attachment_from_problem',
           'create_or_update_address_organisation',
           'create_or_update_contact',
           'create_or_update_audit',
        #    'get_template_table_attachments',
        #    'get_template_table_corr_action',
        #    'get_list_components',
        #    'get_template_form_component',
        #    'get_context_for_problem',
        #    'get_photos_for_problem',
           'get_list_organisations_by_filter',
           'get_context_organisation',
           'get_template_table_contacts',
           'get_template_table_audits',
           'get_template_table_attachments_audit',
           'add_attachment_audit',
           'delete_attachment_from_audit',
           'create_mail_with_problem',
           'create_presentation_was_is',
           'save_presentation_was_is',
           'report_was_is',
           'create_organisation'
        #    'get_list_models_by_filter'
           ]


def _add_attachement(file):
    descr = os.path.splitext(file.filename)[0]
    extension = os.path.splitext(file.filename)[1]
    try:
        return Attachment.create(descr=descr, extension=extension, data=file.read())
    except PeeweeException:
        raise


def add_attachment_to_problem(file, problem_id: Union[str, int], photo_old=False, photo_new=False) -> Tuple:
    """добавляет вложение file  в проблему с problem_id
        и возвращает Tuple со статусом ответа и сообщением об ошибке,
        если не удалось сохранить в базу данных.
        """

    try:
        problem = Problem.get_by_id(problem_id)
    except DoesNotExist:
        current_app.logger.info(f'Проблема {problem_id} не найдена!')
        return False, 'Проблема не найдена!'

    # descr = os.path.splitext(file.filename)[0]
    # extension = os.path.splitext(file.filename)[1]
    try:
        with db_wrapper.database.atomic():
            att = _add_attachement(file)
            ProblemAttachment.create(
                attachment=att, problem=problem, photo_old=photo_old, photo_new=photo_new)
        return True, ''
    except PeeweeException as e:
        current_app.logger.info(f'Ошибка сохранения данных - ({e.args})')
        return False, e.args


# def delete_attachment_from_problem(problem_id: Union[str, int], att_id: Union[str, int]) -> Tuple:
#     """Удаляет вложение с att_id из проблемы с problem_id
#         и возвращает Tuple со статусом ответа и сообщением об ошибке,
#         если проблема или вложение не найдены"""

#     try:
#         problem = Problem.get_by_id(problem_id)
#         att = Attachment.get_by_id(att_id)
#         att_prob = ProblemAttachment.get(
#             ProblemAttachment.problem == problem, ProblemAttachment.attachment == att)
#     except DoesNotExist as e:
#         current_app.logger.info(f'Сущности не найдены! ({e.args})')
#         return False, e.args
#     try:
#         with db_wrapper.database.atomic():
#             att_prob.delete_instance()
#             att.delete_instance()
#         return True, ''
#     except PeeweeException as e:
#         current_app.logger.info(f'Ошибка при удалении данных - ({e.args})')
#         return False, e.args


# def get_template_table_attachments(problem_id) -> str:
#     """ возвращает html-шаблон таблицы вложений для проблемы с problem_id"""

#     attachments = Attachment.select().join(ProblemAttachment).join(Problem).where((Problem.id == problem_id) & (
#         ProblemAttachment.photo_old == False) & (ProblemAttachment.photo_new == False))
#     return render_template(
#         'table_attachment.html', attachments=attachments)


# def get_list_models_by_filter(str_search):
#     if str_search:
#         queryset = ModelBus.select().where(ModelBus.descr.contains(str_search))
#     else:
#         queryset = ModelBus.select()
#     #queryset = get_list_problems_by_filter(search)
#     return queryset.order_by(ModelBus.descr)


# def get_list_problems_by_filter(str_search='') -> List:

#     if str_search:
#         queryset = Problem.select() \
#             .join(Organisation).switch(Problem) \
#             .join(Status).switch(Problem) \
#             .join(Component).switch(Problem) \
#             .join(Location).switch(Problem) \
#             .join(ProblemModels).join(ModelBus).where(
#             (Problem.short_descr.contains(str_search)) |
#             (Problem.detailed_descr.contains(str_search)) |
#             (Problem.location_detail.contains(str_search)) |
#             (Problem.root_cause.contains(str_search)) |
#             (Problem.comment.contains(str_search)) |
#             (Problem.lider.contains(str_search)) |
#             (Problem.main_action.contains(str_search)) |
#             (Problem.location_detection.descr.contains(str_search)) |
#             (Problem.status.descr.contains(str_search)) |
#             (Problem.component.descr.contains(str_search)) |
#             (Problem.component.number.contains(str_search)) |
#             (ModelBus.descr.contains(str_search)) |
#             (Problem.organisation.descr.contains(str_search))
#         )
#     else:
#         queryset = Problem.select().order_by(Problem.id.desc())
#     #queryset = get_list_problems_by_filter(search)
#     return queryset
    

# def paginate(queryset, page_number):
#     """
#         Возвращает страницу номер page_number 
#         со списоком проблем в зависимости от
#         переданной строки поиска.
#     """

#     paginator = Paginator(queryset, 20)
#     try:
#         page = paginator.page(page_number)
#     except PageNotAnInteger:
#         # # If page is not an integer, deliver first page.
#         pages = paginator.page(1)
#     except EmptyPage:
#         # # If page is out of range (e.g. 9999), deliver last page of results.
#         page = paginator.page(paginator.num_pages)
#     return page


def create_mail_with_problem(problem_id, list_atts):
    try:
        problem = Problem.get_by_id(problem_id)
    except DoesNotExist:
        problem = Problem()
    pythoncom.CoInitialize()
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    # mail.SentOnBehalfOfName = 'EMAIL'
    # mail.To = 'EMAIL'
    mail.Subject = f'Информация по проблеме: {problem.short_descr}'
    # mail.Body = 'Message body'
    mail.HTMLBody = render_template(
        'body_mail_problem.html', problem=problem, corr_action=problem.actions)
    # To attach a file to the email (optional):
    query = Attachment.select().where(Attachment.id.in_(list_atts))
    for att in query:
        _, att_name = att.write_attachment_for_send()
        mail.Attachments.Add(att_name)
    mail.Display()


def create_presentation_was_is(problem_ids: List):
    """
    принимает список id проблем
    возвращает объект PowerPoint, который необходимо активировать для вывода на экран
    """
    problems = Problem.select().where(Problem.id.in_(problem_ids))

    pp = win32.Dispatch('powerpoint.application')
    pp.Visible = False
    prs = pp.Presentations.Open(
        os.path.join(current_app.static_folder, 'reports', 'was-is.pptx'))
    for problem in problems:
        slide = prs.Slides(1).Duplicate()
        slide.Shapes.Item(
            "Title").TextFrame.TextRange.Text = problem.get_models_to_string()
        tShape = slide.Shapes.Item("Table13")
        table = tShape.Table
        table.Cell(
            1, 2).Shape.TextFrame.TextRange.Text = problem.component.get_full_name()
        table.Cell(2, 2).Shape.TextFrame.TextRange.Text = problem.short_descr
        table.Cell(
            3, 2).Shape.TextFrame.TextRange.Text = problem.main_action if problem.main_action else ""
        slide.Shapes.Item("WasText").Top = tShape.Top + tShape.Height
        slide.Shapes.Item("IsText").Top = tShape.Top + tShape.Height

        attachments = ProblemAttachment.select(ProblemAttachment, Problem, Attachment).join(
            Problem).switch(ProblemAttachment).join(Attachment).where(Problem.id == problem.id)
        left_border = 150
        top_border = slide.Shapes.Item(
            "WasText").Top + slide.Shapes.Item("WasText").Height
        bot_border = slide.Shapes.Item("Дата 3").Top - top_border - 15
        for att in attachments:
            if att.photo_old or att.photo_new:
                _, path_att = att.attachment.write_attachment_for_send()
                if path_att:
                    if att.photo_old:
                        left_border = 25
                    elif att.photo_new:
                        left_border = 394
                    slide.Shapes.AddPicture(
                        path_att, False, True, left_border, top_border, 300, bot_border)
    slide = prs.Slides(1).Delete()
    return pp
    # power.Activate()


def save_presentation_was_is(problems: List):
    """
    принимает список Model: Problem
    возвращает имя файла и полный путь к 
    """
    pythoncom.CoInitialize()
    power = win32.Dispatch('powerpoint.application')
    prs = power.Presentations.Open(
        os.path.join(current_app.static_folder, 'reports', 'was-is.pptx'), WithWindow=False)
    for problem in problems:
        slide = prs.Slides(1).Duplicate()
        slide.Shapes.Item(
            "Title").TextFrame.TextRange.Text = problem.get_models_to_string()
        tShape = slide.Shapes.Item("Table13")
        table = tShape.Table
        table.Cell(
            1, 2).Shape.TextFrame.TextRange.Text = problem.component.get_full_name()
        table.Cell(2, 2).Shape.TextFrame.TextRange.Text = problem.short_descr
        table.Cell(
            3, 2).Shape.TextFrame.TextRange.Text = problem.main_action if problem.main_action else ""
        slide.Shapes.Item("WasText").Top = tShape.Top + tShape.Height
        slide.Shapes.Item("IsText").Top = tShape.Top + tShape.Height

        attachments = ProblemAttachment.select(ProblemAttachment, Problem, Attachment).join(
            Problem).switch(ProblemAttachment).join(Attachment).where(Problem.id == problem.id)
        left_border = 150
        top_border = slide.Shapes.Item(
            "WasText").Top + slide.Shapes.Item("WasText").Height
        bot_border = slide.Shapes.Item("Дата 3").Top - top_border - 15
        for att in attachments:
            if att.photo_old or att.photo_new:
                _, path_att = att.attachment.write_attachment_for_send()
                if path_att:
                    if att.photo_old:
                        left_border = 25
                    elif att.photo_new:
                        left_border = 394
                    slide.Shapes.AddPicture(
                        path_att, False, True, left_border, top_border, 300, bot_border)
    slide = prs.Slides(1).Delete()

    file_name = 'was-is_' + \
        datetime.datetime.strftime(
            datetime.datetime.now(), '%Y_%m_%d_%H_%M_%S_%f') + '.pptx'
    full_file_name = os.path.join(current_app.static_folder, TMPDIR, file_name)
    prs.SaveAs(full_file_name)
    power.Quit()
    return file_name, full_file_name


def get_list_organisations_by_filter(str_search=''):
    if str_search:
        list_org = Organisation.select().where(
            Organisation.descr.contains(str_search) |
            Organisation.legal_country.contains(str_search) |
            Organisation.legal_state.contains(str_search) |
            Organisation.legal_sity.contains(str_search) |
            Organisation.legal_address.contains(str_search) |
            Organisation.zip_code.contains(str_search) |
            Organisation.country.contains(str_search) |
            Organisation.state.contains(str_search) |
            Organisation.sity.contains(str_search) |
            Organisation.address.contains(str_search) |
            Organisation.mail.contains(str_search) |
            Organisation.site.contains(str_search) |
            Organisation.descr.contains(str_search)
        )
    else:
        list_org = Organisation.select()

    return list_org


def get_context_organisation(id):
    try:
        organisation = Organisation.get_by_id(id)
    except DoesNotExist:
        current_app.logger.info(f'Организация с {id} не найдена!')
        return abort(404)

    adress_form = AddressForm(obj=organisation)
    common_contact_form = CommonContactForm(obj=organisation)
    contact_form = ContactForm()
    audit_form = AuditForm()

    return {'organisation': organisation,
            'adress_form': adress_form,
            'common_contact_form': common_contact_form,
            'contact_form': contact_form,
            'audit_form': audit_form
            }


def create_organisation(form):
    org = Organisation()
    form.populate_obj(org)
    try:
        org.save()
        return org, ''
    except PeeweeException as e:
        current_app.logger.info(f'Failed to save data - ({e.args})')
        return None, e.args


def create_or_update_address_organisation(form):
    try:
        organisation = Organisation.get_by_id(form.org_id.data)
    except DoesNotExist as e:
        current_app.logger.info(f'Организация с {form.org_id.data} не найдена! ({e.args})')
        return None, e.args

    form.populate_obj(organisation)
    try:
        organisation.save()
    except PeeweeException as e:
        current_app.logger.info(f'Ошибка сохранения данных - ({e.args})')
        return None, e.args
    return organisation, ''


def create_or_update_contact(contact_id, form):
    try:
        contact = Contact.get_by_id(contact_id)
    except DoesNotExist as e:
        contact = Contact()

    form.populate_obj(contact)
    contact.last_update = datetime.datetime.today()  # date(datetime.datetime.now())
    try:
        contact.save()
        return contact, ''
    except PeeweeException as e:
        current_app.logger.info(f'Ошибка сохранения данных - ({e.args})')
        return None, e.args


def get_template_table_contacts(org_id):
    contacts = Contact.select().join(Organisation).where(
        Organisation.id == org_id)
    return render_template(
        'table_contacts.html', contacts=contacts)


def create_or_update_audit(audit_id, form):
    try:
        audit = Audit.get_by_id(audit_id)
    except DoesNotExist:
        audit = Audit()
    form.populate_obj(audit)
    try:
        audit.save()
    except PeeweeException as e:
        current_app.logger.info(f'Ошибка сохранения данных - ({e.args})')
        return None, e.args
    return audit, ''


def get_template_table_audits(org_id):
    audits = Audit.select().join(Organisation).where(
        Organisation.id == org_id)
    return render_template(
        'table_organisation_audits.html', audits=audits)


def get_template_table_attachments_audit(audit_id):
    attachments = Attachment.select().join(
        AuditAttachments).join(Audit).where(Audit.id == audit_id)
    try:
        audit = Audit.get_by_id(audit_id)
    except DoesNotExist:
        audit = Audit()
    return render_template(
        'table_attachment_audit.html', audit=audit)


def add_attachment_audit(file, audit_id):
    try:
        audit = Audit.get_by_id(audit_id)
    except DoesNotExist as e:
        current_app.logger.info(f'Аудит с {audit_id} не найдена!')
        return False, e.args
    try:
        with database.atomic():
            att = _add_attachement(file)
            audit.attachments.add(att)
        return True, ''
    except PeeweeException as e:
        current_app.logger.info(f'Ошибка сохранения данных - ({e.args})')
        return False, e.args


def delete_attachment_from_audit(attachment_id, audit_id) -> Tuple:
    """Удаляет вложение с attachment_id из аудита с audit_id
        и возвращает Tuple со статусом ответа и сообщением об ошибке,
        если проблема или вложение не найдены"""

    try:
        audit = Audit.get_by_id(audit_id)
        audit.attachments.remove(Attachment.select().where(
            Attachment.id == attachment_id))
    except DoesNotExist as e:
        current_app.logger.info(f'Аудит с id-{audit_id} не найден! ({e.args})')
        return False, e.args
    except PeeweeException as e:
        current_app.logger.info(f'Ошибка при удалении данных - ({e.args})')
        return False, e.args
    return True, ''


def report_was_is(form):
    file_name = ""
    problems = Problem.select().join(ProblemModels).join(ModelBus)
    if form.r_date_start.data:
        problems = problems.where(Problem.date_created >
                                  form.r_date_start.data)
    if form.r_date_end.data:
        problems = problems.where(Problem.date_created <
                                  form.r_date_end.data)
    if form.r_organisation.data:
        problems = problems.where(
            Problem.organisation.in_(form.r_organisation.data))
    if form.r_component.data:
        problems = problems.where(
            Problem.component.in_(form.r_component.data))
    if form.r_location_detection.data:
        problems = problems.where(
            Problem.location_detection.in_(form.r_location_detection.data))
    if form.r_status.data:
        problems = problems.where(
            Problem.status.in_(form.r_status.data))
    if form.r_location_detail.data:
        problems = problems.where(
            Problem.location_detail.contains(form.r_location_detail.data))
    if form.r_lider.data:
        problems = problems.where(
            Problem.lider.contains(form.r_lider.data))

    if form.r_models.data:
        problems = problems.where(
            ModelBus.id.in_(form.r_models.data))
    if problems:
        file_name, _ = save_presentation_was_is(
            problems)
    return file_name

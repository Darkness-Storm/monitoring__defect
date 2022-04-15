from typing import Union, Tuple, List, Dict
from dataclasses import asdict

from flask import request, jsonify, abort, send_file, render_template, url_for, redirect, Blueprint, current_app

from flask_wtf.form import FlaskForm
from peewee import OperationalError, DoesNotExist, PeeweeException, DatabaseError
from playhouse.shortcuts import model_to_dict, dict_to_model

from app.models import *
from app.views.servises import *
from app.forms import *
from app.utils import MyError


pbp = Blueprint('problem', __name__, url_prefix='/problem')


def get_context_for_problem(problem_id) -> Tuple:
    context = {}
    error = None
    
    try:
        problem = Problem.get_by_id(problem_id)
        main_form = ProblemForm(obj=problem)
        main_form.populate_choice()
    except DoesNotExist as e:
        current_app.logger.error(e.args)
        # return context, e.args
        #abort(404)
        error = MyError(message=f'Проблема с id-{problem_id} не существует!',
                        description='', validate=False)
        return context, error
    except DatabaseError as e:
        print('get_context_for_problem')
        current_app.logger.error(e.args)
        #abort(500)
        error = MyError(message='Ошибка при попытке запроса к базе данных!',
                        description=e.args, validate=False)
        return context, error
    try:
        attachments = Attachment.select().join(ProblemAttachment).join(Problem).where((Problem.id == problem_id) & (
            ProblemAttachment.photo_old == False) & (ProblemAttachment.photo_new == False))
    except DatabaseError:
        attachments = []

    photos = get_photos_for_problem(problem_id)
    context = {
        'problem': problem,
        'corr_actions': problem.actions,
        'photos': photos,
        'main_form': main_form,
        'attachments': attachments,
        'title': f'Проблема - {problem.short_descr} (id: {problem.id})'
    }
    return context, error


def get_photos_for_problem(problem_id) -> Dict:
    photos = {}
    try:
        query = ProblemAttachment.select(ProblemAttachment, Problem, Attachment).join(
            Problem).switch(ProblemAttachment).join(Attachment).where(Problem.id == problem_id).execute()
        for att in query:
            if att.photo_old:
                photos['photo_old_url'] = att.attachment.write_attachment_for_photo()
                photos['photo_old_id'] = att.attachment.id
                photos['photo_old_path'] = url_for(
                    'common.send_attachment', id=att.attachment.id)
            elif att.photo_new:
                photos['photo_new_url'] = att.attachment.write_attachment_for_photo()
                photos['photo_new_id'] = att.attachment.id
                photos['photo_new_path'] = url_for(
                    'common.send_attachment', id=att.attachment.id)
    except DatabaseError:
        pass
    return photos
    


def update_problem(problem_id, form):
    """
        Ообновляет проблему.
        Возвращает Tuple из Problem (или None если не удалось сохранить)
        и ошибок (или пустой строки если все нормально).
    """
    try:
        problem = Problem.get_by_id(problem_id)
        form.populate_obj(problem)
        problem.save()
        return problem, ''
    except DoesNotExist:
        return None, f'Проблема id-{problem_id} не найдена!'

    except PeeweeException as e:
        current_app.logger.error(f'Failed to save data - ({e.args})')
        return None, e.args


def create_problem(form):
    problem = Problem()
    models = form.data.get('models', list())
    form.__delitem__('models')
    form.populate_obj(problem)
    try:
        with db_wrapper.database.atomic():
            problem.save()
            problem.models.add(models)
        return problem, None
    except DatabaseError as e:
        current_app.logger.error(e.args)
        #abort(500)
        error = MyError(message='Ошибка при попытке запроса к базе данных!',
                        description=e.args, validate=False)
        return None, error


@pbp.route('/all')
def problems():
    try:
        problems = Problem.select().order_by(Problem.date_detection.desc())
        return jsonify(template=render_template('problems.html', problems=problems))
    except DatabaseError as e:
        current_app.logger.error(e.args)
        #abort(500)
        error = asdict(MyError(message='Ошибка базы данных!', description=e.args, validate=False))
        return jsonify(success=False, error=error), 400
    

@pbp.route('/<int:problem_id>')
def show_problem(problem_id):
    context, error = get_context_for_problem(problem_id)
    if not error:
        return jsonify(template=render_template('problem.html', **context), success=True)
    else:
        return jsonify(success=False, error=error), 400


@pbp.route('/add', methods=['GET', 'POST'])
def add_problem():
    if request.method == 'GET':
        form = ProblemForm()
        form.populate_choice()
        return jsonify(template=render_template('problem_add.html', main_form=form))

    elif request.method == 'POST':

        form = ProblemForm()
        form.populate_choice()
        
        if form.validate():
            problem, error = create_problem(form)
            print(f'error create - {error}')
            if error:
                return jsonify(success=False, error=error), 400
        else:
            template = render_template('problem_add.html', main_form=form)
            error = asdict(MyError(message='Ошибка проверки данных!', description=form.errors, validate=True))
            print(f'error val - {error}')
            return jsonify(success=False, error=error, template=template), 400

        context, error = get_context_for_problem(problem.id)
        print(f'error con - {error}')
        if not error:
            return jsonify(template=render_template('problem.html', **context), success=True)
        else:
            return jsonify(success=False, error=error), 400


@pbp.route('/<int:problem_id>/update', methods=['POST'])
def save_problem(problem_id):
    #problem_id = request.form.get('id')
    try:
        problem = Problem.get_by_id(problem_id)
    except DoesNotExist as e:
        current_app.logger.error(e.args)
        error = MyError(message=f'Проблема с id-{problem_id} не существует!',
                        description='', validate=False)
        return jsonify(success=False, error=error), 400
    except DatabaseError as e:
        current_app.logger.error(e.args)
        abort(500, f'Произошла ошибка обращения к базе данных. Описание ошибки: {e.args[0]}')

    form = ProblemForm()
    form.populate_choice()
    form.populate_obj(problem)

    if form.validate():
        problem.save()
        return jsonify(success=True)
    else:
        error = asdict(MyError(message='Ошибка проверки данных!', description=form.errors, validate=True))
        template = render_template('problem_form.html', main_form=form)
        return jsonify(success=False, error=error, template=template)


    # except DatabaseError as e:
    #     current_app.logger.error(e.args)
    #     abort(500)    


def get_template_table_corr_action(problem_id):
    actions = CorrectiveAction.select().join(Problem).where(
        Problem.id == problem_id).order_by(
        CorrectiveAction.serial.asc())
    return render_template(
        'problem_table_corr_action.html', actions=actions)


@pbp.route('/action/<int:action_id>')
def get_corr_action(action_id):
    try:
        corr_action = CorrectiveAction.get_by_id(action_id)
        form = CorrActionForm(obj=corr_action)
        form.populate_choice()
    except DoesNotExist as e:
        current_app.logger.error(e.args)
        abort(404)
    except DatabaseError as e:
        current_app.logger.error(e.args)
        abort(500)
    return jsonify(template=render_template('problem_corr_action_form.html', form_corr=form, action_id=action_id))


@pbp.route('/<int:problem_id>/action/add', methods=['GET', 'POST'])
def corr_action_add(problem_id):
    
    try:
        problem = Problem.get_by_id(problem_id)
    except DoesNotExist as e:
        current_app.logger.error(e.args)
        abort(404)
    except DatabaseError as e:
        current_app.logger.error(e.args)
        abort(500)

    if request.method == 'GET':
        
        corr_action = CorrectiveAction()
        corr_action.problem = problem
        form = CorrActionForm(obj=corr_action)
        form.populate_choice()
        return jsonify(template=render_template('problem_corr_action_form.html', form_corr=form))
    elif request.method == 'POST':
        form_action = CorrActionForm()
        try:
            form_action.populate_choice()
            if form_action.validate():
                corr_action = CorrectiveAction()
                form_action.populate_obj(corr_action)
                corr_action.save()
            else:
                error = asdict(MyError(message='Ошибка проверки данных!', description=form_action.errors, validate=True))
                return jsonify(success=False, error=error)
        except DatabaseError as e:
            current_app.logger.error(e.args)
            abort(500)
        template = get_template_table_corr_action(problem_id)
        return jsonify(success=True, template=template)


@pbp.route('/action/<int:action_id>/update', methods=['POST'])
def edit_corr_action(action_id):
    problem_id = request.form.get('problem')
    try:
        corr_action = CorrectiveAction.get_by_id(action_id)
        if int(corr_action.problem.id) != int(problem_id):
            description = f'Переданный id ({problem_id}) проблемы не соответствует первоначальному id ({corr_action.problem.id})'
            error = asdict(MyError(message='Ошибка проверки данных!', description=description, validate=True))
            return jsonify(success=False, error=error)
        form_action = CorrActionForm()
        form_action.populate_choice()
        if form_action.validate():
            form_action.populate_obj(corr_action)
            corr_action.save()
        else:
            error = asdict(MyError(message='Ошибка проверки данных!', description=form_action.errors, validate=True))
            return jsonify(success=False, error=error)
        template = get_template_table_corr_action(problem_id)
        return jsonify(success=True, template=template)
    except DoesNotExist as e:
        current_app.logger.error(e.args)
        abort(404)
    except ValueError as e:
        current_app.logger.error(e.args)
        description = f'Переданный id ({problem_id}) проблемы не является числом!'
        error = asdict(MyError(message='Ошибка проверки данных!', description=description, validate=True))
        return jsonify(success=False, error=error)
    except DatabaseError as e:
        current_app.logger.error(e.args)
        abort(500)


@pbp.route('/action/<int:action_id>/delete', methods=['DELETE'])
def delete_action(action_id):
    """ Endpoint ajax для удаления корректирующего по проблеме
        по проблеме.
    """
    try:
        corr_action = CorrectiveAction.get_by_id(action_id)
        problem_id = corr_action.problem
        corr_action.delete_instance()
        template = get_template_table_corr_action(problem_id)
        return jsonify(success=True, template=template)
    except DoesNotExist as e:
        current_app.logger.error(e.args)
        abort(404)
    except DatabaseError as e:
        current_app.logger.error(e.args)
        abort(500)


@pbp.route('/<int:problem_id>/was_is')
def create_was_is_problem(problem_id):
    """ Endpoint ajax для формирования презентации "Было-стало"
        по проблеме.
    """
    problems = Problem.select().where(Problem.id == problem_id)
    file_name, _ = save_presentation_was_is(problems)
    url_file = get_url_attachment(file_name)
    return jsonify(file_name=file_name, url_file=url_file)


@pbp.route('/<int:problem_id>/get_att_mail')
def get_att_mail(problem_id):
    """ Endpoint ajax для формирования модального окна
        для выбора вложений в почтовое сообщение.
    """

    attachments = Attachment.select().join(ProblemAttachment).join(
        Problem).where(Problem.id == problem_id)
    template = render_template(
        'modal_change_att_mail.html', attachments=attachments, problem_id=problem_id)
    return jsonify(template=template)


@pbp.route('/<int:id>/create_outlook_mail')
def create_outlook_mail(id):
    atts = request.args.get('atts')
    atts = atts.split(',')
    create_mail_with_problem(id, atts)
    return jsonify(success=True)


def get_template_table_attachments(problem_id) -> str:
    """ возвращает html-шаблон таблицы вложений для проблемы с problem_id"""

    attachments = Attachment.select().join(ProblemAttachment).join(Problem).where((Problem.id == problem_id) & (
        ProblemAttachment.photo_old == False) & (ProblemAttachment.photo_new == False))
    return render_template(
        'problem_table_attachment.html', attachments=attachments)
    

@pbp.route('/<int:problem_id>/attachment/add', methods=['POST'])
def problem_attachment_add(problem_id):

    try:
        file = request.files['filetosave']
    except KeyError:
        return jsonify(success=False, message='Передайте вложение!')

    photo_old = request.args.get('photoOld', False)
    photo_new = request.args.get('photoNew', False)
    success, errors = add_attachment_to_problem(
        file, problem_id, photo_old, photo_new)
    if success:
        if photo_old or photo_new:
            photos = get_photos_for_problem(problem_id)
            return jsonify(success=success, photos=photos)
        else:
            template = get_template_table_attachments(problem_id)
            return jsonify(success=success, template=template)
    else:
        return jsonify(success=success, errors=errors, message='Не удалось сохранить!')


@pbp.route('/<int:problem_id>/attachment/<int:att_id>/delete', methods=['DELETE'])
def delete_attachment(problem_id, att_id):
    """ Endpoint ajax для удаления вложений по проблеме с problem_id.
        Возвращает json со статусом ответа (success),
        шаблоном для замены html элемента (если все ок)
        или сообщение c ошибками.
    """

    try:
        problem = Problem.get_by_id(problem_id)
        att = Attachment.get_by_id(att_id)
        att_prob = ProblemAttachment.get(
            ProblemAttachment.problem == problem, ProblemAttachment.attachment == att)
    except DoesNotExist as e:
        current_app.logger.error(e.args)
        abort(404)
    except DatabaseError as e:
        current_app.logger.error(e.args)
        abort(500)

    try:
        with db_wrapper.database.atomic():
            att_prob.delete_instance()
            att.delete_instance()
        template = get_template_table_attachments(problem_id)
        return jsonify(success=True, template=template)
    except DatabaseError as e:
        current_app.logger.error(e.args)
        abort(500)

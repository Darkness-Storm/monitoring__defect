from typing import Union, Tuple, List

from flask import request, jsonify, render_template, Blueprint
from peewee import OperationalError, DoesNotExist, PeeweeException, DatabaseError
from playhouse.shortcuts import model_to_dict, dict_to_model

from app.models import Component
from app.forms import ComponentForm
from app.utils import MyError


component_bp = Blueprint('component', __name__, url_prefix='/component')


@component_bp.route('/all')
def components():
    """
        Возвращает шаблон с таблицей компонентов.
    """

    list_components = Component.select().order_by(Component.descr)
    return render_template('components.html', list_components=list_components)


@component_bp.route('/<int:component_id>')
def get_component(component_id):
    """
    Endpoint ajax формирования формы для редактирования компонента.
    Возвращает html-шаблон формы.
    """

    try:
        component = Component.get_by_id(component_id)
    except DoesNotExist:
        component = Component()
    form = ComponentForm(obj=component)
    return jsonify(template=render_template('form_component.html', form=form, component_id=component_id))


def create_or_update_component(component_id, form: ComponentForm) -> Tuple:
    """
        Создает или обновляет компонент.
        Возвращает Tuple из Component (или None) и
        ошибки, если что-то пошло не так.
    """

    try:
        component = Component.get_by_id(component_id)
    except DoesNotExist:
        component = Component()

    form.populate_obj(component)
    try:
        component.save()
        return component, ''
    except DatabaseError as e:
        app.logger.error(e.args)
        error = MyError(message='Ошибка при попытке запроса к базе данных!',
                        description=e.args, validate=False)
        return component, error


@component_bp.route('/update', methods=['POST'])
def edit_component():
    """ Endpoint ajax запроса для создания или редактирования компонента.
        Возвращает json со статусом ответа (success),
        шаблоном для замены html элемента и сериализованной моделью компонента (если все ок)
        или сообщение c ошибками.
    """
    if request.method == 'POST':
        component_id = request.form.get('component_id')
        form = ComponentForm()
        if form.validate():
            component, error = create_or_update_component(component_id, form)
            if not error:
                component_js = model_to_dict(component, extra_attrs=['get_full_name'])
                #template = render_template(
                #    'table_components.html', list_components=get_list_components())
                return jsonify(success=True, template="template", component=component_js)
            else:

                return jsonify(success=False, error=error), 400
        else:
            error = asdict(MyError(message='Ошибка проверки данных!', description=form.errors, validate=True))
            return jsonify(success=False, error=error)


@component_bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_component(id):
    """ Endpoint ajax запроса для удаления компонента.
        Возвращает json со статусом ответа (success)
        и ошибкой (если имеется).
    """

    try:
        comp = Component.get_by_id(id)
        comp.delete_instance()
    except DoesNotExist as e:
        app.logger.error(f'Компонент с {id} не найден!')
        error = MyError(message=f'Компонент с {id} не найден!',
                        description='', validate=False)
        return jsonify(success=False, error=error), 400
    except DatabaseError as e:
        app.logger.error(f'Ошибка при удалении данных! ({e.args})')
        error = MyError(message='Ошибка при удалении данных!',
                        description=e.args, validate=False)
        return jsonify(success=False, error=error), 400

    return jsonify(success=True)
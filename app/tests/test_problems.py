import pytest
import datetime
import os
from contextlib import suppress

from playhouse.shortcuts import model_to_dict, dict_to_model

from app.models import CorrectiveAction, Problem
# from app.views.problems import get_photos_for_problem

@pytest.fixture()
def data():
    return {'component_id': '1'
            , 'organisation_id': '1'
            , 'short_descr': 'тестовое описание 1'
            , 'detailed_descr': ''
            , 'location_detection_id': '1'
            , 'location_detail': ''
            , 'root_cause': ''
            , 'status_id': '1'
            , 'comment': ''
            , 'lider': ''
            , 'main_action': ''
            , 'date_detection': '22-02-2022'
            , 'models': ['1', '2']}

@pytest.fixture()
def data_corr_action():
    return {'serial': '2'
            , 'descr': 'тестовое описание корректирующих действий 2'
            , 'executor': 'Исполнитель 2'
            , 'comment': 'no comment'
            , 'status_id': '1'
            , 'deadline': '15-03-2022'}


def create_data_problem(database):
    with database:
        problem, _ = Problem.get_or_create(short_descr="test descr", date_detection="2022-03-16", component_id=1,organisation=1, location_detection=1)
        problem.save()
        corr_action = CorrectiveAction(serial=1, descr='тестовое описание корректирующих действий 1', executor='Исполнитель 1', status=1, deadline="2022-03-25")#'25-03-2022'
        corr_action.problem = problem
        corr_action.save()
    return problem.id, corr_action.id


def test_request_problems(client):

    response = client.get("/problem/all")
    assert response.status_code == 200
    has_template = False
    if 'template' in response.json:
        has_template = True
    assert has_template, 'В ответе отсутствует ключ "template"'
    assert '<table class="table table-hover table-bordered table-striped table-sm brython-table" id="mainTable">' in response.json['template']


def test_request_problems_nonvalid(client, database, app):
    """
    пробуем послать запрос при отсутствуещей БД
    """
    database.close()
    with suppress(FileNotFoundError):
        os.remove(app.config['DATABASE']['name'])

    response = client.get("/problem/all")
    assert response.status_code == 400
    # has_template = False
    # if 'template' in response.json:
    #     has_template = True
    # assert has_template, 'В ответе отсутствует ключ "template"'
    # assert '<h1>Произошла непредвиденная ошибка</h1>' in response.json['template']
    assert response.json['success'] == False
    has_error = False
    if 'error' in response.json:
        has_error = True
    assert has_error, 'В ответе отсутствует ключ "error"'
    assert response.json['error']['validate'] == False
    assert response.json['error']['message'] == 'Ошибка базы данных!'


def test_problem_get_valid(client, database):
    """
    пробуем послать запрос с существующим id проблемы
    """

    problem_id, corr_action_id = create_data_problem(database)
    problems = Problem.select().count()
    assert problems == 1
    database.close()

    response = client.get(f'/problem/{problem_id}')
    assert response.status_code == 200
    assert response.json['success'] == True
    has_template = False
    if 'template' in response.json:
        has_template = True
    assert has_template, 'В ответе отсутствует ключ "template"'
    assert f'<p class="invisible" hidden id="idProblem"><small>{problem_id}</small></p>' in response.json['template']


def test_problem_get_nonvalid(client, database):
    """
    пробуем послать запрос с несуществующим id проблемы
    """

    problem_id, corr_action_id = create_data_problem(database)
    problems = Problem.select().count()
    assert problems == 1
    database.close()

    response = client.get(f'/problem/{problem_id+1}')
    assert response.status_code == 400
    # has_template = False
    # if 'template' in response.json:
    #     has_template = True
    # assert has_template, 'В ответе отсутствует ключ "template"'
    # assert '<h2>Запрашиваемые Вами данные не найдены!</h2>' in response.json['template']
    assert response.json['success'] == False
    has_error = False
    if 'error' in response.json:
        has_error = True
    assert has_error, 'В ответе отсутствует ключ "error"'
    assert response.json['error']['validate'] == False
    assert response.json['error']['message'] == f'Проблема с id-{problem_id+1} не существует!'


def test_problem_get_nonvalid1(client, database, app):
    """
    пробуем послать запрос с существующим id проблемы,
    но с отсутствующей БД
    """

    problem_id, corr_action_id = create_data_problem(database)
    problems = Problem.select().count()
    assert problems == 1
    database.close()
    with suppress(FileNotFoundError):
        os.remove(app.config['DATABASE']['name'])

    response = client.get(f'/problem/{problem_id}')
    assert response.status_code == 400
    # has_template = False
    # if 'template' in response.json:
    #     has_template = True
    # assert has_template, 'В ответе отсутствует ключ "template"'
    # assert '<h1>Произошла непредвиденная ошибка</h1>' in response.json['template']
    has_error = False
    if 'error' in response.json:
        has_error = True
    assert has_error, 'В ответе отсутствует ключ "error"'
    assert response.json['error']['validate'] == False
    assert response.json['error']['message'] == 'Ошибка при попытке запроса к базе данных!'


def test_problem_add_get(client, database, app):

    response = client.get('/problem/add')
    assert response.status_code == 200
    has_template = False
    if 'template' in response.json:
        has_template = True
    assert has_template, 'В ответе отсутствует ключ "template"'
    assert '<form id="formProblem">' in response.json['template']


def test_problem_add_get_nonvalid(client, database, app):
    """
    пробуем послать запрос на добавление проблемы
    на отсутствующую БД
    """
    database.close()
    with suppress(FileNotFoundError):
        os.remove(app.config['DATABASE']['name'])
    response = client.get('/problem/add')
    assert response.status_code == 200
    #assert '<h1>Произошла непредвиденная ошибка</h1>' in response.json['template']
    # has_error = False
    # if 'error' in response.json:
    #     has_error = True
    # assert has_error, 'В ответе отсутствует ключ "error"'
    # assert response.json['error']['validate'] == False
    # assert response.json['error']['message'] == 'Ошибка при попытке запроса к базе данных!'
    has_template = False
    if 'template' in response.json:
        has_template = True
    assert has_template, 'В ответе отсутствует ключ "template"'
    assert '<form id="formProblem">' in response.json['template']


def test_problem_add_post(client, data):

    response = client.post('/problem/add', data=data)
    assert response.status_code == 200
    has_template = False
    if 'template' in response.json:
        has_template = True
    assert has_template, 'В ответе отсутствует ключ "template"'
    assert '<form id="formProblem">' in response.json['template']
    assert response.json['success'] == True


def test_problem_add_post_nonvalid(client, data):

    data['date_detection'] = ''
    response = client.post('/problem/add', data=data)
    assert response.status_code == 400
    has_template = False
    if 'template' in response.json:
        has_template = True
    assert has_template, 'В ответе отсутствует ключ "template"'
    assert '<form id="formProblem">' in response.json['template']
    assert response.json['success'] == False
    has_error = False
    if 'error' in response.json:
        has_error = True
    assert has_error, 'В ответе отсутствует ключ "error"'
    assert response.json['error']['validate'] == True
    assert response.json['error']['message'] == 'Ошибка проверки данных!'


def test_problem_add_post_nonvalid2(client, data):

    data['status_id'] = '100'
    response = client.post('/problem/add', data=data)
    assert response.status_code == 400
    has_error = False
    if 'error' in response.json:
        has_error = True
    assert has_error, 'В ответе отсутствует ключ "error"'
    assert response.json['success'] == False
    assert response.json['error']['validate'] == True
    assert response.json['error']['message'] == 'Ошибка проверки данных!'


def test_problem_add_post_nonvalid3(client, data, database, app):


    database.close()
    with suppress(FileNotFoundError):
        os.remove(app.config['DATABASE']['name'])
    response = client.post('/problem/add', data=data)
    assert response.status_code == 400
    # has_template = False
    # if 'template' in response.json:
    #     has_template = True
    # assert has_template, 'В ответе отсутствует ключ "template"'
    # assert '<h1>Произошла непредвиденная ошибка</h1>' in response.json['template']
    has_error = False
    if 'error' in response.json:
        has_error = True
    assert has_error, 'В ответе отсутствует ключ "error"'
    assert response.json['error']['validate'] == False
    print(response.json['error']['description'])
    assert response.json['error']['message'] == 'Ошибка при попытке запроса к базе данных!'


def test_problem_update_valid(client, data, database):

    problem_id, _ = create_data_problem(database)
    data['date_detection'] = '22-05-2021'
    response = client.post(f'problem/{problem_id}/update', data=data)
    assert response.status_code == 200
    assert response.json['success'] == True


def test_problem_update_nonvalid(client, data, database):
    """
    Обновление проблемы с несуществующим id
    """
    problem_id, _ = create_data_problem(database)

    response = client.post(f'problem/{problem_id+100}/update', data=data)
    assert response.status_code == 400
    # has_template = False
    # if 'template' in response.json:
    #     has_template = True
    # assert has_template, 'В ответе отсутствует ключ "template"'
    # assert '<h2>Запрашиваемые Вами данные не найдены!</h2>' in response.json['template']

    assert response.json['success'] == False
    has_error = False
    if 'error' in response.json:
        has_error = True
    assert has_error, 'В ответе отсутствует ключ "error"'
    assert response.json['error']['message'] == f'Проблема с id-{problem_id+100} не существует!'
    assert response.json['error']['validate'] == False


def test_problem_update_nonvalid1(client, data, database):

    problem_id, _ = create_data_problem(database)
    data['short_descr'] = ''
    response = client.post(f'problem/{problem_id}/update', data=data)
    assert response.status_code == 200
    assert response.json['success'] == False
    has_error = False
    if 'error' in response.json:
        has_error = True
    assert has_error, 'В ответе отсутствует ключ "error"'
    assert response.json['error']['message'] == 'Ошибка проверки данных!'
    assert response.json['error']['validate'] == True


def test_problem_update_nonvalid2(client, data, database, app):

    problem_id, _ = create_data_problem(database)
    #data['date_detection'] = '22-05-2021'
    database.close()
    with suppress(FileNotFoundError):
        os.remove(app.config['DATABASE']['name'])
    response = client.post(f'problem/{problem_id}/update', data=data)
    assert response.status_code == 400
    # has_template = False
    # if 'template' in response.json:
    #     has_template = True
    # assert has_template, 'В ответе отсутствует ключ "template"'
    # assert '<h1>Произошла непредвиденная ошибка</h1>' in response.json['template']
    assert response.json['success'] == False
    has_error = False
    if 'error' in response.json:
        has_error = True
    assert has_error, 'В ответе отсутствует ключ "error"'
    assert response.json['error']['message'] == 'Не удалось сохранить данные!'
    assert response.json['error']['validate'] == False


def test_problem_update_nonvalid3(client, data, database):

    problem_id, _ = create_data_problem(database)
    data['status_id'] = '100'
    response = client.post(f'problem/{problem_id}/update', data=data)
    assert response.status_code == 200
    assert response.json['success'] == False
    has_error = False
    if 'error' in response.json:
        has_error = True
    assert has_error, 'В ответе отсутствует ключ "error"'
    assert response.json['error']['message'] == 'Ошибка проверки данных!'
    assert response.json['error']['validate'] == True


# def test_get_photos_for_problem(client, data):
#     data['id'] = 1
#     response = client.post('/problem/add', data=data)
#     assert response.status_code == 200
#     photos = get_photos_for_problem(1)
#     assert photos == {}

# def test_get_photos_for_problem_nonvalid(client, data, database, app):
#     data['id'] = 1
#     response = client.post('/problem/add', data=data)
#     assert response.status_code == 200
#     database.close()
#     with suppress(FileNotFoundError):
#         os.remove(app.config['DATABASE']['name'])
#     photos = get_photos_for_problem(1)
#     assert photos == {}


# def test_corr_action_get(client, database):
#     """
#     пробуем послать запрос с существующим id корректирующих действий
#     """

#     _, corr_action_id = create_data_problem(database)
#     actions = CorrectiveAction.select().count()
#     assert actions == 1
#     database.close()

#     response = client.get(f'/problem/action/{corr_action_id}')
#     assert response.status_code == 200
#     has_template = False
#     if 'template' in response.json:
#         has_template = True
#     assert has_template, 'В ответе отсутствует ключ "template"'


# def test_corr_action_get_nonvalid(client, database):
#     """
#     пробуем послать запрос с несуществующим id корректирующих действий
#     """
#     problem_id, corr_action_id = create_data_problem(database)
#     actions = CorrectiveAction.select().where(
#         CorrectiveAction.problem == problem_id).count()
#     assert actions == 1
#     database.close()

#     response = client.get(f'/problem/action/{corr_action_id+100}')
#     assert response.status_code == 404
#     if 'template' in response.json:
#         has_template = True
#     assert has_template, 'В ответе отсутствует ключ "template"'
#     assert '<h2>Запрашиваемые Вами данные не найдены!</h2>' in response.json['template']


# def test_corr_action_get_nonvalid1(client, app, database):
#     """
#     пробуем послать запрос с существующим id корректирующих действий,
#     но с отсутствующей БД
#     """
#     problem_id, corr_action_id = create_data_problem(database)
#     actions = CorrectiveAction.select().where(
#         CorrectiveAction.problem == problem_id).count()
#     assert actions == 1
#     database.close()
#     with suppress(FileNotFoundError):
#         os.remove(app.config['DATABASE']['name'])

#     response = client.get(f'/problem/action/{corr_action_id}')
#     assert response.status_code == 500
#     if 'template' in response.json:
#         has_template = True
#     assert has_template, 'В ответе отсутствует ключ "template"'
#     assert '<h1>Произошла непредвиденная ошибка</h1>' in response.json['template']


# def test_corr_action_add_get(client, data_corr_action, database):
#     problem_id, _ = create_data_problem(database)
#     # actions = CorrectiveAction.select().join(Problem).where(
#     #     Problem.id == problem_id).count()
#     # assert actions == 1
#     database.close()

#     data_corr_action['problem'] = problem_id
#     response = client.get(f'/problem/{problem_id}/action/add', data=data_corr_action)
#     assert response.status_code == 200
#     has_template = False
#     if 'template' in response.json:
#         has_template = True
#     assert has_template, 'В ответе отсутствует ключ "template"'
#     # actions = CorrectiveAction.select().join(Problem).where(
#     #     Problem.id == problem_id).count()
#     # assert actions == 1


# def test_corr_action_add_get_nonvalid(client, data_corr_action, database):
#     """
#     пробуем послать запрос с несуществующим id проблемы
#     """
#     problem_id, _ = create_data_problem(database)
#     problems = Problem.select().count()
#     assert problems == 1
#     database.close()

#     data_corr_action['problem'] = problem_id
#     response = client.get(f'/problem/{problem_id+100}/action/add', data=data_corr_action)
#     assert response.status_code == 404
#     has_template = False
#     if 'template' in response.json:
#         has_template = True
#     assert has_template, 'В ответе отсутствует ключ "template"'
#     assert '<h2>Запрашиваемые Вами данные не найдены!</h2>' in response.json['template']

#     problems = Problem.select().count()
#     assert problems == 1

# def test_corr_action_add_get_nonvalid2(client, data_corr_action, database, app):
#     """
#     пробуем послать запрос с несуществующим id проблемы
#     """
#     problem_id, _ = create_data_problem(database)
#     problems = Problem.select().count()
#     assert problems == 1
#     database.close()
#     with suppress(FileNotFoundError):
#         os.remove(app.config['DATABASE']['name'])

#     data_corr_action['problem'] = problem_id
#     response = client.get(f'/problem/{problem_id}/action/add', data=data_corr_action)
#     assert response.status_code == 500

#     has_template = False
#     if 'template' in response.json:
#         has_template = True
#     assert has_template, 'В ответе отсутствует ключ "template"'
#     assert '<h1>Произошла непредвиденная ошибка</h1>' in response.json['template']


# def test_corr_action_add_post(client, data_corr_action, database):
#     problem_id, _ = create_data_problem(database)
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1
#     database.close()
#     data_corr_action['problem'] = problem_id
#     response = client.post(f'/problem/{problem_id}/action/add', data=data_corr_action)
#     assert response.status_code == 200
#     assert response.json['success'] == True
#     has_template = False
#     if 'template' in response.json:
#         has_template = True
#     assert has_template, 'В ответе отсутствует ключ "template"'
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 2

# def test_corr_action_add_post_nonvalid(client, data_corr_action, database):
#     problem_id, _ = create_data_problem(database)
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1
#     database.close()
#     data_corr_action['problem'] = problem_id + 100
#     response = client.post(f'/problem/{problem_id+100}/action/add', data=data_corr_action)
#     assert response.status_code == 404
#     has_template = False
#     if 'template' in response.json:
#         has_template = True
#     assert has_template, 'В ответе отсутствует ключ "template"'
#     assert '<h2>Запрашиваемые Вами данные не найдены!</h2>' in response.json['template']

#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1


# def test_corr_action_add_post_nonvalid2(client, data_corr_action, database):
#     problem_id, _ = create_data_problem(database)
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1
#     database.close()
#     data_corr_action['status_id'] = 5000
#     response = client.post(f'/problem/{problem_id}/action/add', data=data_corr_action)
#     assert response.status_code == 200
#     assert response.json['success'] == False
#     has_error = False
#     if 'error' in response.json:
#         has_error = True
#     assert has_error, 'В ответе отсутствует ключ "error"'
#     assert response.json['error']['validate'] == True
#     assert response.json['error']['message'] == 'Ошибка проверки данных!'
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1


# def test_corr_action_add_post_nonvalid3(client, data_corr_action, database, app):
#     problem_id, _ = create_data_problem(database)
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1
#     database.close()
#     with suppress(FileNotFoundError):
#         os.remove(app.config['DATABASE']['name'])

#     response = client.post(f'/problem/{problem_id}/action/add', data=data_corr_action)
#     assert response.status_code == 500
#     has_template = False
#     if 'template' in response.json:
#         has_template = True
#     assert has_template, 'В ответе отсутствует ключ "template"'
#     assert '<h1>Произошла непредвиденная ошибка</h1>' in response.json['template']
#     # assert response.json['success'] == False
#     # has_error = False
#     # if 'error' in response.json:
#     #     has_error = True
#     # assert has_error, 'В ответе отсутствует ключ "error"'
#     # assert response.json['error']['validate'] == False
#     # assert response.json['error']['message'] == 'Не удалось получить данные!'


# def test_corr_action_update_post(client, data_corr_action, database):
#     problem_id, corr_action_id = create_data_problem(database)
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1
#     database.close()

#     data_corr_action['problem'] = problem_id
#     data_corr_action['id'] = corr_action_id
#     response = client.post(f'/problem/action/{corr_action_id}/update', data=data_corr_action)
#     assert response.status_code == 200
#     assert response.json['success'] == True
#     has_template = False
#     if 'template' in response.json:
#         has_template = True
#     assert has_template, 'В ответе отсутствует ключ "template"'
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1
#     database.close()


# def test_corr_action_update_post_nonvalid(client, data_corr_action, database):
#     """
#     пробуем послать запрос с несуществующим id корректирующих действий
#     """
#     problem_id, corr_action_id = create_data_problem(database)
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1
#     database.close()
#     data_corr_action['problem'] = problem_id
#     data_corr_action['id'] = corr_action_id
#     response = client.post(f'/problem/action/{corr_action_id+1}/update', data=data_corr_action)
#     assert response.status_code == 404
#     has_template = False
#     if 'template' in response.json:
#         has_template = True
#     assert has_template, 'В ответе отсутствует ключ "template"'
#     assert '<h2>Запрашиваемые Вами данные не найдены!</h2>' in response.json['template']
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1


# def test_corr_action_update_post_nonvalid1(client, data_corr_action, database):
#     """
#     пробуем послать запрос с невалидной датой
#     """

#     problem_id, corr_action_id = create_data_problem(database)
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1
#     database.close()
#     data_corr_action['problem'] = problem_id
#     data_corr_action['id'] = corr_action_id
#     data_corr_action['deadline'] = ''
#     response = client.post(f'/problem/action/{corr_action_id}/update', data=data_corr_action)
#     assert response.status_code == 200
#     assert response.json['success'] == False
#     has_error = False
#     if 'error' in response.json:
#         has_error = True
#     assert has_error, 'В ответе отсутствует ключ "error"'
#     assert response.json['error']['validate'] == True
#     assert response.json['error']['message'] == 'Ошибка проверки данных!'
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1


# def test_corr_action_update_post_nonvalid2(client, data_corr_action, database):
#     """
#     пробуем послать запрос с id проблемы несоответствующей записанному в БД
#     """
#     problem_id, corr_action_id = create_data_problem(database)
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1
#     database.close()

#     data_corr_action['problem'] = problem_id + 1
#     data_corr_action['id'] = corr_action_id

#     response = client.post(f'/problem/action/{corr_action_id}/update', data=data_corr_action)
#     assert response.status_code == 200
#     assert response.json['success'] == False
#     has_error = False
#     if 'error' in response.json:
#         has_error = True
#     assert has_error, 'В ответе отсутствует ключ "error"'
#     assert response.json['error']['validate'] == True
#     assert response.json['error']['message'] == 'Ошибка проверки данных!'
#     assert response.json['error']['description'] == f'Переданный id ({problem_id+1}) проблемы не соответствует первоначальному id ({problem_id})'
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1


# def test_corr_action_update_post_nonvalid3(client, data_corr_action, database):
#     """
#     пробуем послать запрос с нечисловым id проблемы 
#     """
#     problem_id, corr_action_id = create_data_problem(database)
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1
#     database.close()

#     data_corr_action['problem'] = 'test_id'
#     data_corr_action['id'] = corr_action_id

#     response = client.post(f'/problem/action/{corr_action_id}/update', data=data_corr_action)
#     assert response.status_code == 200
#     assert response.json['success'] == False
#     has_error = False
#     if 'error' in response.json:
#         has_error = True
#     assert has_error, 'В ответе отсутствует ключ "error"'
#     assert response.json['error']['validate'] == True
#     assert response.json['error']['message'] == 'Ошибка проверки данных!'
#     assert response.json['error']['description'] == f'Переданный id (test_id) проблемы не является числом!'
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1

# def test_corr_action_update_post_nonvalid4(client, data_corr_action, database, app):
#     """
#     пробуем послать запрос на обновление
#     с отсутствующей БД
#     """
#     problem_id, corr_action_id = create_data_problem(database)
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1
#     database.close()
#     with suppress(FileNotFoundError):
#         os.remove(app.config['DATABASE']['name'])
#     data_corr_action['problem'] = problem_id
#     data_corr_action['id'] = corr_action_id

#     response = client.post(f'/problem/action/{corr_action_id}/update', data=data_corr_action)
#     assert response.status_code == 500
#     has_template = False
#     if 'template' in response.json:
#         has_template = True
#     assert has_template, 'В ответе отсутствует ключ "template"'
#     assert '<h1>Произошла непредвиденная ошибка</h1>' in response.json['template']

# def test_corr_action_delete(client, database):
#     """
#     пробуем послать запрос на удаление корректирующего
#     """
#     problem_id, corr_action_id = create_data_problem(database)
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1
#     database.close()
#     response = client.delete(f'/problem/action/{corr_action_id}/delete')
#     assert response.status_code == 200
#     assert response.json['success'] == True
#     has_template = False
#     if 'template' in response.json:
#         has_template = True
#     assert has_template, 'В ответе отсутствует ключ "template"'
#     assert '<table class="table table-hover table-bordered table-striped table-sm table-responsive" id="tableAction">' in response.json['template']
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 0


# def test_corr_action_delete_nonvalid(client, database):
#     """
#     пробуем послать запрос на удаление корректирующего
#     с несуществующим id
#     """
#     problem_id, corr_action_id = create_data_problem(database)
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1
#     database.close()
#     response = client.delete(f'/problem/action/{corr_action_id+1}/delete')
#     assert response.status_code == 404
#     has_template = False
#     if 'template' in response.json:
#         has_template = True
#     assert has_template, 'В ответе отсутствует ключ "template"'
#     assert '<h2>Запрашиваемые Вами данные не найдены!</h2>' in response.json['template']
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1


# def test_corr_action_delete_nonvalid1(client, database, app):
#     """
#     пробуем послать запрос на удаление корректирующего
#     с отключившейся БД
#     """
#     problem_id, corr_action_id = create_data_problem(database)
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1
#     database.close()
#     with suppress(FileNotFoundError):
#         os.remove(app.config['DATABASE']['name'])
#     response = client.delete(f'/problem/action/{corr_action_id}/delete')
#     assert response.status_code == 500
#     has_template = False
#     if 'template' in response.json:
#         has_template = True
#     assert has_template, 'В ответе отсутствует ключ "template"'
#     assert '<h1>Произошла непредвиденная ошибка</h1>' in response.json['template']


# def test_corr_action_delete_nonvalid2(client, database):
#     """
#     пробуем послать запрос на удаление корректирующего
#     методом GET
#     """
#     problem_id, corr_action_id = create_data_problem(database)
#     actions = CorrectiveAction.select().join(Problem).where(
#         Problem.id == problem_id).count()
#     assert actions == 1
#     database.close()
#     response = client.get(f'/problem/action/{corr_action_id}/delete')
#     assert response.status_code == 405
#     has_template = False
#     if 'template' in response.json:
#         has_template = True
#     assert has_template, 'В ответе отсутствует ключ "template"'
#     assert '<h2>Точка доступа не поддерживает данный метод запроса</h2>' in response.json['template']
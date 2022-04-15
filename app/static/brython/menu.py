from browser import document, ajax, window, confirm, html
from browser.session_storage import storage

from utils import *
from custom_table import BrythonTable
from custom_select import BrythonSelect


def get_big_spinner ():
    return """<div class="d-flex justify-content-center"><div class="spinner-border" style="width: 5rem; height: 5rem;" role="status">
    <span class="sr-only">Loading...</span></div></div>"""


def render_contents(request):
    #document['containerContent'].html = get_big_spinner()
    if request.status == 200 or request.status == 0:
        data = request.json

        if data.get('error'):
            show_errors(error)
        else:
            document['containerContent'].html = data['template']
            update_custom_elements()
    elif request.status == 404:
        data = request.json
        try:
            template = data['template']
            document['containerContent'].html = template
        except KeyError:
            pass
        #print(request.text)


def update_custom_elements():

    for item in document.select(".brython-table"):
        BrythonTable(item)
    for item in document.select(".brython-select"):
        BrythonSelect(item)
    init_flatpickr()
    init_bsCustomFileInput()
    try:
        document["inputOldPhoto"].bind('change', change_old_photo)
        document["inputNewPhoto"].bind('change', change_new_photo)
    except KeyError:
        pass

def show_errors(error={}):
    if error.get('validate', False):
        pass
    else:
        pass
    #show_toast(error.get('message'))
    # +"<b><h4>"+error.get('description', '')+'</h4>')
    message = error['message']
    descr = ""
    #descr = error.get('description', '')
    if isinstance(error['description'], dict):
        for k, v in error['description'].items():
            descr = descr + k  + ": " + v[0] +"; "
    elif isinstance(error['description'], str):
        descr = error['description']
    message = message + "<p>Описание ошибки-<small>" + descr + "</small></p>"
    show_toast(message)

def save_content_html():
    storage['oldhtml'] = document['containerContent'].html


def go_back():
    try:
        document['containerContent'].html = storage['oldhtml']
        update_custom_elements()
    except KeyError:
        show_toast('Не удалось выполнить переход!')


#####################################################################################################
########  Problems

def problem_id():
    try:
        return document['idProblem'].text
    except KeyError:
        return ""


def get_all_problems():
    # document['containerContent'].html = get_big_spinner()

    ajax.get('/problem/all', oncomplete=render_contents)
    return False


def show_problem(id):
    #save_content_html()
    # document['containerContent'].html = get_big_spinner()
    #print(target)
    document[f'link{id}'].html = get_spinner()
    url = f'/problem/{id}'
    ajax.get(url, oncomplete=render_contents)


def get_form_add_problem():

    document['containerContent'].html = get_big_spinner()
    ajax.get('/problem/add', oncomplete=render_contents)
    return False


def complete_save_new_problem(request):
    if request.status == 200 or request.status == 0:
        data = request.json
        if data.get('success', False):
            document['containerContent'].html = data.get('template', "")
            update_custom_elements()
        else:
            show_errors1(data.get('error'))
    else:
        show_errors1(data.get('error'))
        #show_toast()


def save_new_problem():
    try:
        form = document["formProblem"]
    except KeyError:
        show_toast(f"Не найдена форма для отравки! Попробуйте позднее.")
        return
    document['containerContent'].html = get_big_spinner()
    ajax.post('/problem/add', data=form_serialize(form), oncomplete=complete_save_new_problem, headers=headers)
    return False


def complete_save_problem(request, btn, btn_old_html):
    if request.status == 200 or request.status == 0:
        data = request.json
        if data['success']:
            clear_errors()
            show_toast('Сохранено!')
        else:
            show_errors(data['error'])
            #show_toast(data['message'])
            if data.get('template'):
                document['formProblem'].html = data['template']
                update_custom_elements()
    else:
        show_toast("Ошибка при записи данных! Попробуйте позднее.")
    # render_contents(request)
    btn.html = btn_old_html


def save_problem():
    btn = document["btnSaveProblemBr"]
    btn_old_html = btn.html
    btn.html = get_spinner(' Сохранение')

    try:
        form = document["formProblem"]
    except KeyError:
        show_toast(f"Не найдена форма для отравки! Попробуйте позднее.")
        return
    ajax.post(f'/problem/{problem_id()}/update', data=form_serialize(form), oncomplete=lambda request: complete_save_problem(request, btn, btn_old_html), headers=headers)


def complete_load_att(request, btn_old_html):
    if request.status == 200 or request.status == 0:
        data = request.json
        if data.get('success', False):
            document['tableAttProblem'].html = data.get('template','')
            show_toast("Вложения добавлены!")
        else:
            show_errors(errors=data.get('errors',''), message=data.get("message", ''))
    else:
        show_toast("Ошибка при загрузке данных! Попробуйте позднее.")
    try:
        btn = document["btnLoadAtt"]
        btn.html = btn_old_html
    except KeyError:
        pass
    

def load_attachment_problem():
    try:
        btn = document["btnLoadAtt"]
        btn_old_html = btn.html
        btn.html = get_spinner(' Загрузка')
    except KeyError:
        btn_old_html = ""
    url = f'/problem/{problem_id()}/attachment/add' #?photoOld=0&photoNew=0
    for f in document["customFile"].files:
        ajax.file_upload(url, f, oncomplete=lambda request: complete_load_att(request, btn_old_html))

def update_state_photo(photo_old, photo_new):
    if photo_old:
        try:
            old = document["photoOld"]
            old.href = ""
            old.html = ""
            btn_del = document['btnDelOldPhoto']
            btn_del.classList.add("disabled")
            document['btnAddOldPhoto'].classList.remove('disabled')
        except KeyError:
            pass
            
    if photo_new:
        try:
            old = document["photoNew"]
            old.href = ""
            old.html = ""
            btn_del = document['btnDelNewPhoto']
            btn_del.classList.add("disabled")
            document['btnAddNewPhoto'].classList.remove('disabled')
        except KeyError:
            pass

def complete_delete_att(request, photo_old, photo_new):

    if request.status == 200 or request.status == 0:
        data = request.json
        if data.get('success', False):
            document['tableAttProblem'].html = data.get('template','')
            show_toast("Запись удалена!")
            update_state_photo(photo_old, photo_new)
        else:
            show_errors(errors=data.get('errors',''), message=data.get("message", ''))
    elif request.status == 404:
        show_toast('Данные, запрашиваемые для удаления, не найдены!')
    elif request.status == 500:
        show_toast("Ошибка при удалении данных! Попробуйте позднее.")


def delete_attachement(att_id, photo_old=False, photo_new=False):
    if confirm("Вы действительно хотите удалить файл?"):
        ajax.delete(f'/problem/{problem_id()}/attachment/{att_id}/delete', oncomplete=lambda request: complete_delete_att(request, photo_old, photo_new))

# def del_attachement(id):
#     if confirm("Вы действительно хотите удалить запись?"):
#         ajax.delete(f'/problem/{problem_id()}/attachment/{id}/delete', oncomplete=complete_delete_att)


# def delete_photo(id, photo_old, photo_new):
#     if confirm("Вы действительно хотите удалить запись?"):
#         ajax.delete(f'/problem/{problem_id()}/attachment/{id}/delete', oncomplete=complete_delete_att)
#         if photo_old:
#             try:
#                 old = document["photoOld"]
#                 old.href = ""
#                 old.html = ""
#                 btn_del = document['btnDelOldPhoto']
#                 btn_del.classList.add("disabled")
#             except KeyError:
#                 pass
                
#         if photo_new:
#             try:
#                 old = document["photoNew"]
#                 old.href = ""
#                 old.html = ""
#                 btn_del = document['btnDelNewPhoto']
#                 btn_del.classList.add("disabled")
#             except KeyError:
#                 pass


def complete_load_oldphoto(request):
    if request.status == 200 or request.status == 0:
        data = request.json
        if data.get('success', False):
            photos = data.get('photos', None)
            if photos:
                try:
                    old = document["photoOld"]
                except KeyError:
                    old = html.A(id="photoOld")
                old.href = photos['photo_old_path']
                old <= html.IMG(Class="img-fluid img-thumbnail rounded mx-auto d-block", alt="", src=photos['photo_old_url'])
                try:
                    btn_del = document['btnDelOldPhoto']
                    btn_del.classList.remove("disabled")
                    btn_del.href = f"javascript:deleteAttachment({photos['photo_old_id']}, true, false)"
                except KeyError:
                    pass
                try:
                    document['btnAddOldPhoto'].classList.add('disabled')
                except KeyError:
                    pass
                    
        else:
            show_errors(errors=data.get('errors',''), message=data.get("message", ''))
    else:
        show_toast("Ошибка при удалении данных! Попробуйте позднее.")


def change_old_photo(event):
    f = event.target.files[0]
    url = f'/problem/{problem_id()}/attachment/add?photoOld=1' #&photoNew=0
    ajax.file_upload(url, f, oncomplete=complete_load_oldphoto)


def complete_load_newphoto(request):
    if request.status == 200 or request.status == 0:
        data = request.json
        if data.get('success', False):
            photos = data.get('photos', None)
            if photos:
                try:
                    old = document["photoNew"]
                except KeyError:
                    old = html.A(id="photoNew")
                old.href = photos['photo_new_path']
                old <= html.IMG(Class="img-fluid img-thumbnail rounded mx-auto d-block", alt="", src=photos['photo_new_url'])
                try:
                    btn_del = document['btnDelNewPhoto']
                except KeyError:
                    btn_del = None
                if btn_del:
                    btn_del.classList.remove("disabled")
                    btn_del.href = f"javascript:deleteAttachment({photos['photo_new_id']}, false, true)"
                try:
                    document['btnAddNewPhoto'].classList.add('disabled')
                except KeyError:
                    pass
        else:
            show_errors(errors=data.get('errors',''), message=data.get("message", ''))
    else:
        show_toast("Ошибка при удалении данных! Попробуйте позднее.")


def change_new_photo(event):
    f = event.target.files[0]
    url = f'/problem/{problem_id()}/attachment/add?photoNew=1' #&photoNew=0
    ajax.file_upload(url, f, oncomplete=complete_load_newphoto)


def complete_delete_action(request):
    
    if request.status == 200 or request.status == 0:
        data = request.json
        if data.get('success', False):
            document['tableAction'].html = data.get('template','')
            show_toast("Запись удалена!")
        else:
            show_errors(errors=data.get('errors',''), message=data.get("message", ''))
    elif request.status == 404:
        show_toast('Запрашиваемые Вами данные для удаления не найдены!')
    elif request.status == 500:
        show_toast("Ошибка при удалении данных! Попробуйте позднее.")


def del_action(id):
    if confirm("Вы действительно хотите удалить запись?"):
        ajax.delete(f'problem/action/{id}/delete', oncomplete=complete_delete_action)


def complete_send_action(request):
    if request.status == 200 or request.status == 0:
        data = request.json
        if data.get('success', False):
            
            try:
                document["tableAction"].html = data.get('template', '')  
            except KeyError:
                pass
            show_toast('Сохранено')        
        else:
            show_errors(data['error'])
    else:
        show_toast("Ошибка при записи данных! Попробуйте позднее.")
    hide_modal()


def send_corr_action():
    try:
        form = document["formCorrAction"]
        form.select_one("#problem").value = problem_id()
        action_id = int(form.select_one("#id").value)
    except KeyError:
        show_toast(f"Не найдена форма для отравки! Попробуйте позднее.")
        return
    except ValueError:
        action_id = 0
    try:
        document['modalEditLabel'].html = get_spinner('Отправка')
    except KeyError:
        pass
    if action_id:
        url = f'/problem/action/{action_id}/update'
    else:
        url = f'/problem/{problem_id()}/action/add'
    ajax.post(url, data=form_serialize(form), headers=headers, oncomplete=complete_send_action)


def complete_get_action(request):
    if request.status == 200 or request.status == 0:
        data = request.json
        try:
            document['modalEdit'].html = data["template"]
        except KeyError:
            pass
        show_modal()
        init_flatpickr()
    elif request.status == 404:
        show_toast("Ошибка загрузки данных! Попробуйте позднее.")


def show_modal_edit_action(id):
    try:
        form = document["formCorrAction"]
        clear_form(form)
    except KeyError:
        pass
    if id:
        url = f'/problem/action/{id}'
    else:
        url = f'/problem/{problem_id()}/action/add'
    ajax.get(url, oncomplete=complete_get_action, headers=headers)

####### отчеты по проблемам
##### Презентация "Было-стало", подготовка письма Outlook с вложениями

def complete_get_outlook(request):
    if not (request.status == 200 or request.status == 0):
        show_toast("Ошибка запроса данных! Попробуйте позднее.")
    hide_modal()


def get_outlook_with_att():
    old_label = document['staticBackdropLabelMail']
    old_label_html = old_label.html
    old_label.html = get_spinner(' Подождите, идет подготовка данных ')
    url = f'/problem/{problem_id()}/create_outlook_mail'
    atts = [item.value for item in document['changeAttachments'].options if item.selected]
    ajax.get(url, data={'atts': atts}, oncomplete=complete_get_outlook)


def comlete_get_modal_att(request, btn, btn_old_html):
    if request.status == 200 or request.status == 0:
        data = request.json
        document['modalEdit'].html = data.get("template", "")
        show_modal()
    else:
        show_toast("Ошибка запроса данных! Попробуйте позднее.")
    if btn:
        btn.html = btn_old_html


def get_modal_att_mail(problem_id):
    try:
        btn = document['btnSendMailProblem']
        btn_old_html = btn.html
        btn.html = get_spinner(' Загрузка')
    except KeyError:
        btn = None
        btn_old_html = ""
    ajax.get(f'/problem/{problem_id}/get_att_mail',headers=headers, oncomplete=lambda request: comlete_get_modal_att(request, btn, btn_old_html))


def complete_send_presentation(request, btn, btn_old_html):
    if request.status == 200 or request.status == 0:
        data = request.json
        link = html.A(href=data['url_file'], download=data['file_name'])
        event = window.MouseEvent.new("click")
        link.dispatchEvent(event)
    else:
        show_toast("Ошибка запроса данных! Попробуйте позднее.")
    if btn:
        btn.html = btn_old_html


def presentation_problem_wasis(problem_id):
    try:
        btn = document['btnCreateWasIs']
        btn_old_html = btn.html
        btn.html = get_spinner(' Загрузка')
    except KeyError:
        btn = None
        btn_old_html = ""
    url = f'/problem/{problem_id}/was_is'
    ajax.get(url, headers=headers, oncomplete=lambda request: complete_send_presentation(request, btn, btn_old_html))



##########################################################################
# Bus Component

def complete_send(request):
    if request.status == 200 or request.status == 0:
        data = request.json
        if data.get('success'):
            show_toast('Сохранено')
            try:
                component = data["component"]
                id = component["id"]
                replace_tr = document[f"{id}"]    
            except KeyError:
                replace_tr = None
            if id:
                if replace_tr:
                    replace_tr.select_one(".number").text = component["number"]
                    replace_tr.select_one(".descr").text = component["descr"]
                else:
                    body = document.select_one("#mainTable").select_one("tbody")
                    tr = html.TR(id=id)
                    tr <= html.TD(html.A(html.IMG(src="/static/img/bootstrap-icons/pencil.svg"
                                    , **{'alt': "", 'width': "16", 'height': "16", 'title': 'Редактировать'})
                                    ,Class="editComp", href=f"javascript:getComponent({id})")
                                )
                    tr <= html.TD(component["number"], Class="number")
                    tr <= html.TD(component["descr"], Class="descr")
                    body.prepend(tr)
        else:
            show_toast(data['message'])
    else:
        show_toast("Ошибка при записи данных! Попробуйте позднее.")
    hide_modal()


def send_form(event):
    event.preventDefault()
    try:
        form = document["formEditComponent"]
    except KeyError:
        show_toast(f"Не найдена форма для отравки! Попробуйте позднее.")
        return
    try:
        document['modalEditLabel'].html = get_spinner('Отправка')
    except KeyError:
        pass
    ajax.post('/component/update', data=form_serialize(form), headers=headers, oncomplete=complete_send)


def complete_delete(request, id):

    if request.status == 200 or request.status == 0:
        data = request.json
        if data['success']:
            tr = document[id]
            tr.clear()
            show_toast("Удалено!")
        else:
            show_toast(data['message'])
    else:
        show_toast("Ошибка при удалении данных! Попробуйте позднее.")
    hide_modal()


def delete_component(event):
    event.preventDefault()
    if confirm("Вы действительно хотите удалить эту запись?"):
        id = document["component_id"].value
        url = f'/component/{id}/delete'
        ajax.delete(url, oncomplete=lambda request: complete_delete(request, id), headers=headers)


def complete_get_component(request):
    if request.status == 200 or request.status == 0:
        data = request.json
        try:
            document['modalEdit'].html = data["template"]
            document['btnSubmit'].bind('click', send_form)
            document['btnDelete'].bind('click', delete_component)
        except KeyError:
            pass
        show_modal()
    else:
        show_toast("Ошибка загрузки данных! Попробуйте позднее.")


def show_modal_edit_component(id):
    try:
        form = document["formEditComponent"]
        clear_form(form)
    except KeyError:
        pass
    url = f'/component/{id}'
    ajax.get(url, oncomplete=complete_get_component, headers=headers)


def get_components():
    document['containerContent'].html = get_big_spinner()
    ajax.get('/component/all', oncomplete=render_contents, headers=headers)
    return False


window.showProblem = show_problem
window.goBack = go_back
window.getAllProblems = get_all_problems
window.getComponents = get_components
window.getComponent = show_modal_edit_component
window.addProblem = get_form_add_problem
window.saveNewProblem = save_new_problem
window.saveProblem1 = save_problem
window.deleteCorrAction = del_action
window.sendCorrAction = send_corr_action
window.showModalAction = show_modal_edit_action
window.deleteAttachment = delete_attachement
window.LoadAttProblem = load_attachment_problem
#window.deletePhoto = delete_photo
window.getReportProblemWasIs = presentation_problem_wasis
window.getAttForMail = get_modal_att_mail
window.sendAttForMail = get_outlook_with_att

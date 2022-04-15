from browser import document, window

from custom_table import BrythonTable
from custom_select import BrythonSelect


jq = window.jQuery
flatpickr = window.flatpickr
bsCustomFileInput = window.bsCustomFileInput


def init_bsCustomFileInput():
    bsCustomFileInput.init()

    
def init_flatpickr():
    flatpickr(".datepicker", {
        "locale": "ru", 
        "dateFormat": "d-m-Y"
    })

headers={'X-Requested-With':'X-Requested-With'}


def show_toast(message=""):
    document['toast-body'].text = message
    jq('#mainToast').toast('show')

def show_modal():
    jq('#modalEdit').modal('show')

def hide_modal():
    jq('#modalEdit').modal('hide')

def form_serialize(form):
    s_ser = ''
    for el in form.elements:
        id = el.name if el.name else el.id
        if id:
            if el.type == 'select-multiple':
                sel_options = [item for item in el.options if item.selected]
                for item in sel_options:
                    s_ser += f'{id}={item.value}&'
            elif el.type == 'checkbox':
                if el.checked:
                    s_ser += f'{id}=checked&'
            elif el.type == 'radio':
                if el.checked:
                    s_ser += f'{id}={el.value}&'
            elif el.type == 'button' or el.type == 'submit':
                pass
            else:
                s_ser += f'{id}={el.value}&'
    return s_ser

def clear_form(form):
    for el in form.elements:
        if el.type == 'text' or el.type=='textarea':
            el.value = ""
        elif el.type == 'radio' or el.type == 'checkbox':
            el.checked = False
        elif el.type == 'select-one' or el.type == 'select-multiple':
            el.value = "All"

def get_spinner(message=""):
    return '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>'+message

def get_big_spinner():
    return """<div class="d-flex justify-content-center"><div class="spinner-border" style="width: 5rem; height: 5rem;" role="status"><span class="sr-only">Loading...</span></div></div>"""


def clear_errors():
    for elem in document.select('.non-valid'):
        elem.text = ""


def show_errors(errors={}, validate=False, message=""):
    if validate:
        for key, value in errors:
            document.select_one(f"#{key}_error").text = value

        show_toast(message)
    else:
        show_toast(message+"\n"+errors)

def get_id_trow(event):
    """возвращает id записи в БД при клике по строке таблицы
    event - событие щелчка
    """
    tr = event.target.closest("TR")
    try:
        id = tr.attrs["id"]
    except KeyError:
        id = 0
    return id

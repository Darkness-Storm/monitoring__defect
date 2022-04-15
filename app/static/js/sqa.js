$( document ).ready(function() {
    // Handler for .ready() called.
    bsCustomFileInput.init();
    // $.fn.datepicker.defaults.language = "ru"
    // $.fn.datepicker.defaults.format = "dd-mm-yyyy";
    // $.fn.datepicker.defaults.autoclose = true;
    // $('.datepicker').datepicker();

    flatpickr(".datepicker", {
        "locale": "ru", 
        dateFormat: "d-m-Y",
    });
    // $('#models').selectpicker({'liveSearch': true});
    $('#organisation').selectpicker({'liveSearch': true}); 
    // $('#component').selectpicker({'liveSearch': true});
    $('#r_component').selectpicker();
    $('#r_models').selectpicker();
    $('#r_organisation').selectpicker();
    $('#r_location_detection').selectpicker();
    $('#r_status').selectpicker();
//   setTimeout(() => {
//     jQuery('.selectpicker').selectpicker('refresh');
//   }, 500);
});

function showToast(message){
    $('#toast-body').text(message);
    $('#mainToast').toast('show');
}

function getSpinner(title=""){
    return '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>'+title;
}
// $('#modalEdit').on('show.bs.modal', function (event) {
//     $('#modalEditLabel').html('Загрузка '+getSpinner());
//     $('#modalBody').html('<p class="">Подождите</p>');
// });

function formatDate(date) {
  var dd = date.getDate();
  if (dd < 10) dd = '0' + dd;
  var mm = date.getMonth() + 1;
  if (mm < 10) mm = '0' + mm;
  var yy = date.getFullYear() ;
  return yy + '-' + mm + '-' + dd;
}

function getMessageErrors(dataErrors){
    messageErrors="";
    if (dataErrors) {
        for (let key in dataErrors){
            messageErrors+=key + ": " + dataErrors[key];
        };
    }
    return messageErrors;
}
function clearErrors(){
    for (let elem of document.getElementsByClassName('non-valid')){
        elem.innerHTML = ""; // "тест", "пройден"
    };
}

function showErrors(errors, validate=false, message=""){
    if (validate){
        for (let key in errors){
            $('#'+key+'_error').html(errors[key]);
        };
        showToast(message);
    } else {
        showToast(message+"\n"+errors);
    };
}

function clearForm(form){
    $(':input', '#'+form).each( function() {
        console.log(this.type);
        if(this.type=='text' || this.type=='textarea'){
                 this.value = '';
           }
        else if(this.type=='radio' || this.type=='checkbox'){
             this.checked=false;
          }
             else if(this.type=='select-one' || this.type=='select-multiple'){
                  this.value ='All';
         }
     });
}

///////////////////////////////////////////////////////////////////////////////////////
// поисковые запросы

function search1(event){
    event.preventDefault();
    let btn = document.getElementById('btnSearch');
    let oldHtmlBtn = btn.innerHTML;
    btn.innerHTML = getSpinner();
    let xhr = new XMLHttpRequest();
    let url = new URL(window.location.href);
    url.searchParams.set('search', document.forms['formSearch'].elements['searchFor'].value);
    xhr.open('GET', url);
    xhr.responseType = 'text';
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.send();
    xhr.onload = function() {
        document.getElementById('mainTable').innerHTML=xhr.response;
    };
    xhr.onerror = function() {
        showErrors(xhr.status, validate=false, message="Не удалось получить данные с сервера!!");
    };
    xhr.onloadend = function() {
        btn.innerHTML= oldHtmlBtn;
    }
    return false;
}
function search(event){
    event.preventDefault();
    let btn = $('#btnSearch');
    let oldHtmlBtn = btn.html();
    btn.html(getSpinner());
    let url = new URL(window.location.href);

    $.get(url,{
        'search': $('#formSearch #searchFor').val()
    }).done(function(data){
        $('#mainTable').replaceWith(data.template);
        $('#paginate').replaceWith(data.t_paginate);
    }).fail(function(jqXHR, textStatus){
        showErrors(textStatus, validate=false, message=textStatus);
    }).always(function(){
        btn.html(oldHtmlBtn);
    })
    return false;
}

function getPage(page_number){
    let url = new URL(window.location.href);
    $.get(url,{
        'page': page_number,
        'search': $('#formSearch #searchFor').val()
    }).done(function(data){
        $('#mainTable').replaceWith(data.template);
        $('#paginate').replaceWith(data.t_paginate);
    }).fail(function(jqXHR, textStatus){
        showErrors(textStatus, validate=false, message=textStatus);
    });
}
//////////////////////////////////////////////////////////////////////////////
//// ПРОБЛЕМЫ //////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////
// работа по проблеме
// function saveProblem1(){
//     let btn = document.getElementById('btnSaveProblem');
//     let oldHtmlBtn = btn.innerHTML;
//     btn.innerHTML = getSpinner(title='Загрузка');
//     let xhr = new XMLHttpRequest();
//     xhr.open('POST', '/problem/update');
//     xhr.responseType = 'json';
//     xhr.send(new FormData(formProblem));
//     xhr.onload = function() {
//         if (xhr.response.success) {
//             showToast("Сохранено!");
//             clearErrors();
//         } else {
//             showErrors(xhr.response.errors, validate=xhr.response.validate, message=xhr.response.message);
//         }
//     };
//     xhr.onerror = function() {
//         showErrors(xhr.status, validate=false, message="Не удалось отправить данные на сервер!!");
//     };
//     xhr.onloadend = function() {
//         btn.innerHTML= oldHtmlBtn;
//     }
// }

// function saveProblem(){
//     btn = $('#btnSaveProblem');
//     let oldHtmlBtn = btn.html();
//     btn.html(getSpinner(' Загрузка'));
//     console.log($("#formProblem").serialize());
//     $.post('/problem/update',
//         $("#formProblem").serialize()
//     ).done(function(data){
//         if (data.success){
//             clearErrors();
//             showToast("Сохранено!");
//         } else {
//             showErrors(data.errors, validate=data.validate, message=data.message);
//         }
//     }).fail(function(jqXHR){
//         showToast(`Ошибка ${jqXHR.status}: ${jqXHR.statusText}`);
//     }).always(function(){
//         btn.html(oldHtmlBtn);
//     })
// }

//////////////////////////////////////////////////////////////////////////////
///  Работа с вложениями по проблеме

// загрузка нового вложения
// $(function() {
//     $("#formLoadAttachment").submit(function(event){
//         event.preventDefault();
//  function LoadAttPr(){
//         let oldHtmlBtn = $('#btnLoadAtt').html();
//         $('#btnLoadAtt').html(getSpinner()+'Загрузка');
//         let file_data = $("#customFile").prop("files")[0];
//         let form_data = new FormData();
//         form_data.append("file", file_data);
//         //form_data.append("problem_id", $('#idProblem').text());
//         form_data.append("problem_id", $('#formProblem #id').val());
//         $.ajax({
//             url: '/add_attachment',
//             type: 'post',
//             data: form_data,
//             processData: false,
//             contentType: false})
//         .done(function(data){
//             if (data.success) {
//                 $('#tableAttProblem').replaceWith(data.template);
//                 showToast("Добавлено!");
//             } else {
//                 showErrors(data.errors, message=data.message);
//             }
//         }).fail(function (data) {
//             showToast("Не удалось отправить данные на сервер!!");
//         }).always(function(){
//             $('#btnLoadAtt').html(oldHtmlBtn);
//         });
//         return false;
//     }

//удаление вложения
// function deleteAttachment(att_id){
//     let result = confirm("Вы действительно хотите удалить запись?");
//     if (result){
//         $.ajax({
//             url: '/delete_attachment',
//             type: 'DELETE',
//             data: {id: att_id,
//                 problem_id: $('#formProblem #id').val()}
//         }).done(function(data) {
//             if (data.success) {
//                 $('#tableAttProblem').replaceWith(data.template);
//                 showToast("Запись удалена");
//             } else {
//                 messageErrors = "";
//                 if (data.errors) {
//                     for (let key in data.errors){
//                         messageErrors+=data.errors[key];
//                     }
//                 };
//                 showToast(data.message + ". " + messageErrors);
//             }
//         }).fail(function(){
//             showToast("Не удалось удалить объект!");
//         });
//     }
// }
// получить список вложений для включения в mail
// function getAttForMail(problem_id) {
//     let oldHtmlBtn = $('#btnSendMailProblem').html();
//     $('#btnSendMailProblem').html(getSpinner()+' Загрузка');
//     $.get('/get_att_mail/'+ problem_id).done(function(data){
//         $('#modalChangeAttMail').replaceWith(data.template);
//         $('#modalChangeAttMail').modal('show');
//     }).always(function(){
//         $('#btnSendMailProblem').html(oldHtmlBtn);
//     });
// }

// отправка списка вложений и создание mail-а
// function sendAttForMail(){
//     let oldHtmlBtn = $('#staticBackdropLabelMail').html();
//     $('#staticBackdropLabelMail').html(getSpinner()+' Подождите, идет подготовка данных ');
//     let url = `/problem/${$('#formAttMail #id').val()}/create_outlook_mail`
//     $.get(url, {
//         'atts': $('#changeAttachments').val(),
//     }).fail(function (data) {
//         showToast("Не удалось отправить данные на сервер!!");
//     }).always(function(){
//         $('#modalChangeAttMail').modal('hide');
//         $('#staticBackdropLabelMail').html(oldHtmlBtn);
//     });
// }
// удаление фото было-стало
// function deletePhoto(att_id, isPhotoOld, isPhotoNew) {
//     //console.log(isPhotoOld);
//     //console.log(isPhotoNew);
//     deleteAttachment(att_id);
//     if (isPhotoOld){
//         $("#photoOld").prop('href',"");
//         $("#photoOld").html('');
//         // $("#photoOld > img").prop('src', "");
//         $("#btnDelOldPhoto").addClass([ "disabled" ]);
//     };
//     if (isPhotoNew){
//         $("#photoNew").prop('href',"");
//         $("#photoNew").html('');
//         // $("#photoNew > img").prop('src', "");
//         $("#btnDelNewPhoto").addClass([ "disabled" ]);
//     };
// }
// //добавление фото "было"
// $(function() {
//     $("#inputOldPhoto").on('change',function(){
//         let form_data = new FormData();
//         form_data.append("file", this.files[0]);
//         form_data.append("problem_id", $('#formProblem #id').val());
//         form_data.append("photoOld", true);
//         $.ajax({
//             url: '/add_attachment',
//             type: 'post',
//             data: form_data,
//             processData: false,
//             contentType: false})
//         .done(function(data){
//             if (data.success) {
//                 $("#photoOld").prop('href',data.photos.photo_old_path);
//                 $("#photoOld").html('<img alt="" class="img-fluid img-thumbnail rounded mx-auto d-block"></img>');
//                 $("#photoOld > img").prop('src', data.photos.photo_old_url);
//                 $("#btnDelOldPhoto").removeClass([ "disabled" ]);
//                 $("#btnDelOldPhoto").prop('href',"javascript:deletePhoto(" + data.photos.photo_old_id +", true, false)")
//                 showToast("Добавлено!");
//             } else {
//                 messageErrors = "";
//                 if (data.errors) {
//                     for (let key in data.errors){
//                         messageErrors+=data.errors[key];
//                     };
//                 };
//                 showToast(data.message + ". " + messageErrors);
//             }
//         }).fail(function (data) {
//             showToast("Не удалось отправить данные на сервер!!");
//         }).always(function(){
//             //$('#btnLoadAtt').html(oldHtmlBtn);
//         });
//     });
// });

// //добавлениие фото "стало"
// $(function() {
//     $("#inputNewPhoto").on('change',function(){
//         let form_data = new FormData();
//         form_data.append("file", this.files[0]);
//         form_data.append("problem_id", $('#formProblem #id').val());
//         form_data.append("photoNew", true);
//         $.ajax({
//             url: '/add_attachment',
//             type: 'post',
//             data: form_data,
//             processData: false,
//             contentType: false})
//         .done(function(data) {
//             if (data.success) {
//                 $("#photoNew").prop('href',data.photos.photo_new_path);
//                 $("#photoNew").html('<img alt="" class="img-fluid img-thumbnail rounded mx-auto d-block"></img>');
//                 $("#photoNew > img").prop('src', data.photos.photo_new_url);
//                 $("#btnDelNewPhoto").removeClass([ "disabled" ]);
//                 $("#btnDelNewPhoto").prop('href',"javascript:deletePhoto(" + data.photos.photo_new_id +", false, true)")
//                 showToast("Добавлено!");
//             } else {
//                 messageErrors = "";
//                 if (data.errors) {
//                     for (let key in data.errors){
//                         messageErrors+=data.errors[key];
//                     };
//                 };
//                 showToast(data.message + ". " + messageErrors);
//             }
//         }).fail(function () {
//             showToast("Не удалось отправить данные на сервер!!");
//         }).always(function(){
//             //$('#btnLoadAtt').html(oldHtmlBtn);
//         });
//     });
// });

// // запрос на создание презентации "было-стало"
// function getReportProblemWasIs(problem_id){
//     btn = $('#btnCreateWasIs');
//     let oldHtmlBtn = btn.html();
//     btn.html(getSpinner(' Загрузка'));
//     $.get('/problem/'+problem_id+'/was_is'
//     ).done(function(data){
//         let link = document.createElement("a");
//         link.setAttribute("href", data.url_file);
//         link.setAttribute("download", data.file_name);
//         link.click();
//     }).fail(function(jqXHR){
//         showToast(`Ошибка ${jqXHR.status}: ${jqXHR.statusText}`);
//     }).always(function(){
//         btn.html(oldHtmlBtn);
//     })
// }

//////////////////////////////////////////////////////////////////////////////
// работа с корректирующими действиями по проблеме
// function showModalAction(action_id){
//     clearForm('formCorrAction');
//     if (action_id != 0){
//         $.get('/action/' + action_id
//         ).done(function(data){
//             //console.log(data);
//             $('#formCorrAction').replaceWith(data);
//             // $('#formCorrAction #deadline').datepicker();
//             flatpickr(".datepicker", {
//                 "locale": "ru", 
//                 dateFormat: "d-m-Y",
//             });
//          });
//     }
//     $('#modalAddAction').modal('show');
// }

// function sendCorrAction(){
//     $('#formCorrAction #problem').val($('#formProblem #id').val());
//     $.post('/action/update',
//         $("#formCorrAction").serialize()
//     ).done(function(data){
//         if (data.success) {
//             $('#tableAction').replaceWith(data.template);
//             showToast("Сохранено!");
//             $('#modalAddAction').modal('hide');
//         } else {
//             showErrors(data.errors, validate=data.validate, message=data.message);
//         }
//     }).fail(function (data) {
//         showErrors(data.errors, validate=data.validate, message=data.message);
//     });
// }
// function deleteCorrAction(action_id){
//     //отправляет запрос на удаление корректирующих действий с action_id и обновляет таблицу table-corr-action
//     let result = confirm("Вы действительно хотите удалить запись?");
//     if (result) {
//         $.ajax({
//             url: '/action/delete',
//             type: 'DELETE',
//             data: {id: action_id,
//                 problem_id: $('#formProblem #id').val()}})
//         .done(function(data){
//             if (data.success) {
//                 $('#tableAction').replaceWith(data.template);
//                 showToast("Запись удалена");
//             } else {
//                 showErrors(data.errors, validate=data.validate, message=data.message);
//             }
//         }).fail(function(jqXHR, textStatus){
//             showErrors(jqXHR.status+" "+jqXHR.statusText, message=textStatus);
//         });
//     }
// }

///////////////////////////////////////////////////////////////////////////
//  редактирование компонентов

// function showModalEditComponent(component_id){
//     clearForm('formEditComponent');
//     $.get('/component/'+component_id
//     ).done(function(data){
//         $('#modalEdit').replaceWith(data.template);
//         $('#modalEdit').modal('show');
//      }).fail(function(){
//          showToast('Ошибка загрузки данных! Попробуйте позднее.');
//     });
// }

// function editComponent(target) {
//     //отправляет редактированные данные компонента из formEditComponent

//     if (target.id != "btnSubmit") return;
//     $('#modalEditLabel').html(getSpinner('Отправка'));
//     console.log($("#formEditComponent").serialize());
//     $.post('/component/update',
//         $("#formEditComponent").serialize()
//     ).done(function(data){
//         if (data.success) {
//             if (window.location.pathname.includes('component')) {
//                 $('#mainTable').replaceWith(data.template);
//                 showToast("Сохранено!");
//             } else {
//                 console.log(data);
//                 $("#component").append($('<option>', { 
//                     value: data.component.id,
//                     text : data.component.get_full_name
//                 }));
//                 $("#component").selectpicker('refresh').trigger('change');
//                 $('#component').selectpicker('val', data.component.id );//.prop('selected', true);
//                 $('#component').selectpicker('render');
//             }
//             $('#modalEdit').modal('hide');
//         } else {
//             showErrors(data.errors, validate=data.validate, message=data.message);
//         }
//     }).fail(function (data) {
//         showErrors(data.errors, validate=data.validate, message=data.message);
//     });
// }

////////////////////////////////////////////////////////////////////////////////////////////
// Организации ////////////////////////////////////////////////////////////////////////////

function showModalAddOrganisation(){
    
    $.get('/organisation/add').done(function(data){
        $('#modalEdit').replaceWith(data.template);
        $('#modalEdit').modal('show');
     }).fail(function(){
        $('#modalBody').html('<p>Не удалось загрузить данные</p><p>Попробуйте позднее</p>');
        $('#modalEditLabel').html('Ошибка загрузки данных');
    });
}

function addOrganisation(target){
    if (target.id != "btnSubmit") return;
    $.post('/organisation/add', $('#formAddOrganisation').serialize()
    ).done(function(data){
        if (data.success){
            $("#organisation").append($('<option>', { 
                value: data.org.id,
                text : data.org.get_short_name 
            }));
            //$("#organisation").selectpicker('refresh').empty().append(data.template).selectpicker('refresh').trigger('change');
            $("#organisation").selectpicker('refresh').trigger('change');
            $('#organisation').selectpicker('val', data.org.id );//.prop('selected', true);
            $('#organisation').selectpicker('render');
        } else {
            showErrors(data.errors, validate=data.validate, message=data.message);
        }
    }).fail(function(data){
        showErrors(data.errors, validate=data.validate, message=data.message);
    }).always(function(){
        $('#modalEdit').modal('hide');
    })
}

function editAdress(org_id) {
    $('#formLegalAdrress #org_id').val(org_id);
    $.post('/edit_address', $('#formLegalAdrress').serialize()
    ).done(function(data){
        if (data.success) {
            showToast("Сохранено!");
        } else {
            showToast(data.message + ". " + getMessageErrors(data.errors));
        }
    }).fail(function (data) {
        showToast("Не удалось отправить данные на сервер!!");
    });
}
function showModalEditContact(contact_id){
    
    $.get('/contact/form', {
    'id': contact_id,
    'org_id': $('#org_id').html()
    }).done(function(data){
        if (data.success) {
            $('#modalEdit').replaceWith(data.template);
            $('#modalEdit').modal('show');
        } else {
            showToast(data.message);
        }
     }).fail(function(){
        $('#modalBody').html('<p>Не удалось загрузить данные</p><p>Попробуйте позднее</p>');
        $('#modalEditLabel').html('Ошибка загрузки данных');
    });
}
/*$('#modalEditContact').on('show.bs.modal', function (event) {
    document.getElementById('formEditContact').reset();
    let contact_id = $(event.relatedTarget).data('whatever')
    $.get('/get_form_contact', {
    'id': contact_id,
    }).done(function(data){
        $('#formEditContact').replaceWith(data);
     });
    $('#formEditContact #contact_id').val(contact_id);
});*/
function editContact(event){
    let target = event.target;
    if (target.id != "btnSubmit") return;
    $('#modalEditLabel').html("Отправка " + getSpinner());
    $('#formEditContact #organisation').val($('#org_id').html());
    $.post('/edit_contact',
        $("#formEditContact").serialize()
    ).done(function(data){
        if (data.success) {
            $('#tableContacts').replaceWith(data.template);
            showToast("Сохранено!");
        } else {
            showToast(data.message + ". " + data.errors);
        }
    }).fail(function (data) {
        showToast("Не удалось отправить данные на сервер!!");
    }).always(function(){
        $('#modalEdit').modal('hide');
        $('#formEditContact').trigger('reset');
    });
}

function showModalEditAudit(audit_id){
    $('#modalEdit').modal('show');
    $.get('/get_form_audit', {
    'id': audit_id,
    }).done(function(data){
        $('#modalBody').html(data.template);
        $('#formEditAudit #audit_id').val(audit_id);
        //document.getElementById('btnSubmit').innerHTML = 'Отправить';
        document.getElementById('btnSubmit').addEventListener('click', function(event){
            let target = event.target;
            if (target.id != "btnSubmit") return;
            document.getElementById('modalEditLabel').innerHTML = "Отправка " + getSpinner();
            editAudit(data.organisation_id)});
        document.getElementById('modalEditLabel').innerHTML = 'Аудит id - ' + audit_id;
     }).fail(function(){
        document.getElementById('modalBody').innerHTML = "<p>Не удалось загрузить данные</p><p>Попробуйте позднее</p>";
        document.getElementById('modalEditLabel').innerHTML = 'Ошибка загрузки данных';
     });

}
/*$('#modalEditAudit').on('show.bs.modal', function (event) {
    document.getElementById('formEditAudit').reset();
    document.getElementById('formLoadAttachmentAudit').reset();
    let audit_id = $(event.relatedTarget).data('whatever')
    $.get('/get_form_audit', {
    'id': audit_id,
    }).done(function(data){
        $('#divEditAudit').replaceWith(data);
     });
    $('#formEditAudit #audit_id').val(audit_id);
});*/
function editAudit(org_id){

    $('#formEditAudit #organisation_id').val(org_id);
    $.post('/edit_audit',
        $("#formEditAudit").serialize()
    ).done(function(data){
        if (data.success) {
            $('#tableAudits').replaceWith(data.template);
            showToast("Сохранено!");
        } else {
            showToast(data.message + ". " + getMessageErrors(data.errors));
        }
    }).fail(function (data) {
        showToast("Не удалось отправить данные на сервер!!");
    }).always(function(){
        $('#modalEdit').modal('hide');
    });
}

function getAudits(){
    $.get('/audit/21').done(function(data){
        console.log("function done!");
        console.log(data.success);
        console.log(data.error);
        console.log(data.message);
    }).fail(function(data){
        console.log("function fail!");
        console.log(data);
    });
}

function addAttachmentAudit(audit_id){
    let oldHtmlBtn = $('#btnLoadAtt'+audit_id).html();
    $('#btnLoadAtt'+audit_id).html(getSpinner() + ' Загрузка');
    let file_data = $("#customFile"+audit_id).prop("files")[0];
    let form_data = new FormData();
    form_data.append("file", file_data);
    form_data.append("audit_id", audit_id);
    $.ajax({
        url: '/load_attachment_audit',
        type: 'post',
        data: form_data,
        processData: false,
        contentType: false})
    .done(function(data){
        if (data.success) {
            $('#tableAttAudit'+audit_id).replaceWith(data.template);
            showToast("Добавлено!");
        } else {
            messageErrors = "";
            if (data.errors) {
                for (let key in data.errors){
                    messageErrors+=data.errors[key];
                };
            };
            showToast(data.message + ". " + messageErrors);
        }
    }).fail(function (data) {
        showToast("Не удалось отправить данные на сервер!!");
    }).always(function(){
        $('#btnLoadAtt'+audit_id).html(oldHtmlBtn);
    });
}
function deleteAttachmentAudit(attachment_id, audit_id){
    let result = confirm("Вы действительно хотите удалить запись?");
    if (result){
        $.ajax({
            url: '/delete_attachment_audit',
            type: 'DELETE',
            data: {attachment_id: attachment_id,
                audit_id: audit_id}
        }).done(function(data) {
            if (data.success) {
                $('#tableAttAudit'+audit_id).replaceWith(data.template);
                showToast("Запись удалена");
            } else {
                messageErrors = "";
                if (data.errors) {
                    for (let key in data.errors){
                        messageErrors+=data.errors[key];
                    }
                };
                showToast(data.message + ". " + messageErrors);
            }
        }).fail(function(){
            showToast("Не удалось удалить объект!");
        });
    }
}


function LoadReport(){
    let oldHtmlBtn = $('#btnSubmit').html();
    $('#btnSubmit').html(getSpinner()+' Загрузка');
    $.post('/reports',
        $("#formReport").serialize()
    ).done(function(data){
        var link = document.createElement("a");
        link.setAttribute("href", data.url_file);
        link.setAttribute("download", data.file_name);
        link.click();
    }).fail(function (data) {
        showToast("Не удалось получить данные с сервера!!");
    }).always(function(){
        $('#btnSubmit').html(oldHtmlBtn);
    });
}

function ColapseQuestion(colapseId){
    $('#colapseId').collapse('toggle');
}


function learnUrl(){
    console.log(window.location.pathname);
}
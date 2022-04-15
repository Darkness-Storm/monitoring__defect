document.addEventListener('DOMContentLoaded', function(){
    brython({cache: true});
    flatpickr(".datepicker", {
        "locale": "ru", 
        dateFormat: "d-m-Y",
    });
});
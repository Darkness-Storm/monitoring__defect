from javascript import Math, Date
from browser import document, html, window, aio
#from browser.aio import run #, async, await
from paginate import *


class BrythonTable():
    
    btn_class = 'btn btn-outline-secondary btn-sm'
    btn_class_active = 'btn btn-secondary btn-sm'
    orphans = 3
    _not = ['no', 'false',  'нет', 'н', 'n', ]
    use_paginate = True

    def __init__(self, target, page=1):
        self.target = target
        try:
            self.per_page = self.target.attrs['data-perpage']
        except KeyError:
            self.per_page = 20
        try:
            self.use_paginate = self.target.attrs['data-paginate']
            if self.use_paginate.lower() in self._not:
                self.use_paginate=False
        except KeyError:
            pass
        

        self._initUIComponent()
        self._register_events()
        self.model = [row for row in self.target.select('tbody tr')]
        if not self.use_paginate:
            self.per_page = len(self.model)
        self.paginator = Paginator(self.model, self.per_page, orphans=self.orphans)
        self.get_page(page)
        self._render()

    def _initUIComponent(self):
        
        self.search = html.INPUT(
            Class='form-control form-control-sm', 
            type='search', 
            **{'placeholder': 'Поиск', 'aria-label': 'Поиск'}
        )
        self.bot_div = html.DIV(Class="btn-toolbar", id="divPaginate")
        self.raquo = html.SPAN("&raquo", **{'aria-hidden': 'true'})
        self.laquo = html.SPAN("&laquo", **{'aria-hidden': 'true'})
        self.btn_first = html.BUTTON(
            self.laquo.html*2,
            type="button",
            Class=self.btn_class,
            **{'aria-label': 'PrePrevious',
            'data-id': 'first'}
        )
        self.btn_prev = html.BUTTON(
            self.laquo.html,
            type="button",
            Class=self.btn_class,
            **{'aria-label': 'Previous',
            'data-id': 'prev'}
        )
        self.btn_next = html.BUTTON(
            self.raquo.html,
            type="button",
            Class=self.btn_class,
            **{'aria-label': 'Next',
            'data-id': 'next'}
        )
        self.btn_last = html.BUTTON(
            self.raquo.html*2,
            type="button",
            Class=self.btn_class,
            **{'aria-label': 'NextNext',
            'data-id': 'last'}
        )
        self.btn_cur = html.BUTTON(
            type="button",
            Class=self.btn_class,
            **{'aria-label': 'Current'}
        )
        self.select_per_page = html.SELECT(html.OPTION(elt, value=i) 
            for i, elt in enumerate([10, 20, 50, 100]))
        #self.select_per_page.Class = 'form-control form-control-sm form-select'
        self.select_per_page.classList.add("form-control")
        self.select_per_page.classList.add("form-control-sm")
        for item in self.select_per_page.options:
            if item.text == str(self.per_page):
                item.selected = True

    def _register_events(self):
        self.btn_next.bind('click', self._click_btn_page)
        self.btn_last.bind('click', self._click_btn_page)
        self.btn_prev.bind('click', self._click_btn_page)
        self.btn_first.bind('click', self._click_btn_page)
        self.search.bind('input', self.filter_data)
        self.select_per_page.bind('change', self.update_per_page)

    def _render_paginate_group(self):
        if self.use_paginate:
            self.bot_div.clear()
            
            if self.page.has_previous():
                self.btn_first.disabled = False
                self.btn_prev.disabled = False
            else:
                self.btn_first.disabled = True
                self.btn_prev.disabled = True
            if self.page.has_next():
                self.btn_next.disabled = False
                self.btn_last.disabled = False
            else:
                self.btn_next.disabled = True
                self.btn_last.disabled = True
            
            div_number = html.DIV(Class="btn-group")
            for page in self.page.get_valid_range():
                if page == self.page.number:
                    btn = html.BUTTON(page, type="button",
                        Class=self.btn_class_active, id="currentPage",
                        **{'data-id': page, 'data-active': True}
                        )
                    btn.disabled = True
                else:
                    btn = html.BUTTON(page, type="button",
                        Class=self.btn_class,
                        **{'data-id': page}
                        )
                
                btn.bind('click', self._click_btn_page)
                div_number <= btn
            # badge = f'<span class="badge badge-pill badge-light">{self.paginator.num_pages}</span>'
            #badge = html.SPAN(self.paginator.num_pages, Class='badge')
            self.bot_div <= self.btn_first
            self.bot_div <= self.btn_prev
            self.bot_div <= div_number
            self.bot_div <= self.btn_next
            self.btn_last.clear()
            self.btn_last <= self.raquo.html
            self.btn_last <= " " + str(self.paginator.num_pages)
            self.bot_div <= self.btn_last

    def _click_btn_page(self, event):
        target = event.target
        try:
            btn = target.closest("BUTTON")
            btn_id = btn.attrs["data-id"]
        except KeyError:
            btn_id = "first"
        
        try:
            btn_id_int = int(btn_id)
            self.get_page(btn_id_int)
        except ValueError:
            if btn_id == "next":
                self.get_page(self.page.next_page_number())
            elif btn_id == "prev":
                self.get_page(self.page.previous_page_number())
            elif btn_id == "first":
                self.get_page(1)
            elif btn_id == "last":
                self.get_page(self.paginator.num_pages)
        self._render_paginate_group()
    
    def _render(self):

        for idx, item in enumerate(self.target.select('thead th')):
            link_up = html.A("&#11165", href="#",
                Class="badge badge-light badge-secondary",
                **{'data-ascending': 'up', 'title': 'по возрастанию', 'data-idx': idx})
            link_up.bind('click', self.sorted_data)
            link_down = html.A("&#11167", href="#", Class="badge badge-light badge-secondary", **{'data-ascending': 'down', 'title': 'по убыванию', 'data-idx': idx})
            link_down.bind('click', self.sorted_data)
            item <= link_up + link_down
        
        count_col = len(self.target.select('thead th'))
        tr = self.target.select_one('thead')
        top_div = html.DIV()#Class="row"
        inner_top_div = html.DIV(Class="row")
        if self.use_paginate:
            inner_top_div <= html.DIV(self.select_per_page, Class="col-sm-3")
        inner_top_div <= html.DIV(self.search, Class="col-sm mr-auto")
        top_div <= inner_top_div
        tr.prepend(html.TR(html.TH(top_div, colspan=f"{count_col}")))
        if self.use_paginate:
            self.target.parent.append(self.bot_div)

    def current_page(self):
        return self.page.number

    def get_page(self, page_number):
        self.page = self.paginator.get_page(page_number)
        self.target.select_one('tbody').clear()
        self.target.select_one('tbody') <= self.page
        self._render_paginate_group()

    def sorted_data(self, event):

        event.preventDefault()
        target = event.target
        try:
            ascending = target.attrs['data-ascending']
            col_num = int(target.attrs['data-idx'])
        except KeyError:
            ascending = 'up'
            col_num = 0
        except ValueError:
            ascending = 'up'
            col_num = 0
        
        def k_str(_item):
            return _item.children[col_num].text
        def k_int(_item):
            return float(_item.children[col_num].text)

        try:
            self.paginator.object_list.sort(key=k_int)
        except ValueError:
            self.paginator.object_list.sort(key=k_str)

        if ascending == 'down':
            #self.model.reverse()
            self.paginator.object_list.reverse()
        self.get_page(1)
    
    def update_per_page(self, event):
        event.preventDefault()
        selected = [option.text for option in event.target if option.selected]
        self.per_page = selected[0]
        rows = self.paginator.object_list
        self.paginator = Paginator(rows, self.per_page, orphans=self.orphans)
        self.get_page(1)

    def clear_filter(self, event):
        event.preventDefault()
        self.paginator = Paginator(self.model, self.per_page, orphans=self.orphans)
        self.get_page(1)

    def filter_data(self, event):
        event.preventDefault()
        value = event.target.value.lower()
        if len(value) == 0:
            self.clear_filter(event)
        elif len(value) > 0 and len(value) < 2:
            return
        new_rows = list(filter(lambda item: value in item.text.lower(), self.model))
        self.paginator = Paginator(new_rows, self.per_page, orphans=self.orphans)
        self.get_page(1)


# for item in document.select(".brython-table"):
#     BrythonTable(item)

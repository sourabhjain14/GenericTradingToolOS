"""
Automated Trading Tool
Copyright (c) 2026 Sourabh Jain

This project is licensed under the MIT License. 
See the LICENSE file in the project root for full license information.
"""


from initialize import param
#from ipywidgets import widgets
import ipywidgets as widgets
from ipywidgets import interact,interactive, interact_manual, Button, Output, HBox, VBox, Layout
import globalvar


style = {'description_width': 'initial'}
bw = '25%'

def create_generic_widget(widgettype, param, param_name, param_list, param_value, tag=''):
    return None



def item_set_value(value, items, i, j, width):
    z = i+width*j
    items[z].value=value


def item_get_value(items, i, j, width):
    z = i+width*j
    return items[z].value


def add_global_trade_item_row_old(param):
    iw=param['trade_table_width']
    iw1 =  len(globalvar.g_param['trade_items'])
    iw2 = iw1+iw
    for i in range(iw1, iw2):
        if (i>20 and ((i+1)%iw==0)):
            wbutton = widgets.Button(description="Close")
            wbutton.style.button_color = 'green'
            wbutton.layout.display = 'none'
            globalvar.g_param['trade_items'].append(wbutton)
        else:
            widgetsLabel = widgets.Text(value=" ",disabled=True)
            globalvar.g_param['trade_items'].append(widgetsLabel)


def add_global_trade_item_row(param):
    iw=param['trade_table_width']
    iw1 =  len(param['trade_items'])
    iw2 = iw1+iw
    for i in range(iw1, iw2):
        if (i>20 and ((i+1)%iw==0)):
            wbutton = widgets.Button(description="Close")
            wbutton.style.button_color = 'green'
            wbutton.layout.display = 'none'
            param['trade_items'].append(wbutton)
        else:
            #widgetsLabel = widgets.Text(value=" ",disabled=True)
            widgetsLabel = widgets.Label(value=" ")
            param['trade_items'].append(widgetsLabel)
            
'''
def create_global_trade_items_old(param):
    globalvar.g_param['trade_items'] = []
    iw = param['trade_table_width']
    iwx = param['trade_table_height']*iw
    for i in range(iwx):
        if (i>20 and ((i+1)%iw==0)):
            wbutton = widgets.Button(description="Close")
            wbutton.style.button_color = 'green'
            wbutton.layout.display = 'none'
            #wbutton.on_click(functools.partial(on_close_trade_button_clicked_thread, candle=None, security=None, param=None))
            globalvar.g_param['trade_items'].append(wbutton)
        else:
            #widgetsLabel = widgets.Label("")#,
            widgetsLabel = widgets.Text(value=" ",disabled=True)
            #if i<iw:widgetsLabel.style = {'background': 'yellow'}
            #widgetsLabel.layout = widgets.Layout(background_color='green')
            #style=styles[i%2]
            #widgetsLabel.layout = widgets.Layout(**style)
            #widgetsLabel.style.color == 'lightblue'
            globalvar.g_param['trade_items'].append(widgetsLabel)
            #print(globalvar.g_param['trade_items'][-1].style)
    
    item_set_value("SYMBOL", globalvar.g_param['trade_items'], 0, 0, iw)
    item_set_value("LAST PRICE", globalvar.g_param['trade_items'], 1, 0, iw)
    item_set_value("ENTRY PRICE", globalvar.g_param['trade_items'], 2, 0, iw)
    item_set_value("EXIT PRICE", globalvar.g_param['trade_items'], 3, 0, iw)
    item_set_value("POSITION", globalvar.g_param['trade_items'], 4, 0, iw)
    item_set_value("HOLDING", globalvar.g_param['trade_items'], 5, 0, iw)
    item_set_value("PNL", globalvar.g_param['trade_items'], 6, 0, iw)
    item_set_value("ENTRY TIME", globalvar.g_param['trade_items'], 7, 0, iw)
    item_set_value("EXIT TIME", globalvar.g_param['trade_items'], 8, 0, iw)
    item_set_value("FOS", globalvar.g_param['trade_items'], 9, 0, iw)
    item_set_value("TRADE TYPE", globalvar.g_param['trade_items'], 10, 0, iw)
    item_set_value("EXIT", globalvar.g_param['trade_items'], 11, 0, iw)
    return
'''

def create_global_trade_items(param):
    param['trade_items'] = []
    iw = param['trade_table_width']
    iwx = param['trade_table_height']*iw
    for i in range(iwx):
        if (i>20 and ((i+1)%iw==0)):
            wbutton = widgets.Button(description="Close")
            wbutton.style.button_color = 'green'
            wbutton.layout.display = 'none'
            #wbutton.on_click(functools.partial(on_close_trade_button_clicked_thread, candle=None, security=None, param=None))
            param['trade_items'].append(wbutton)
        else:
            widgetsLabel = widgets.Label("")#,
            #widgetsLabel = widgets.Text(value=" ",disabled=True)
            #widgetsLabel = widgets.Label(value=" ")
            #if i<iw:widgetsLabel.style = {'background': 'yellow'}
            #widgetsLabel.layout = widgets.Layout(background_color='green')
            #style=styles[i%2]
            #widgetsLabel.layout = widgets.Layout(**style)
            #widgetsLabel.style.color == 'lightblue'
            param['trade_items'].append(widgetsLabel)
            #print(param['trade_items'][-1].style)
    
    item_set_value("SYMBOL", param['trade_items'], 0, 0, iw)
    item_set_value("LAST PRICE", param['trade_items'], 1, 0, iw)
    item_set_value("ENTRY PRICE", param['trade_items'], 2, 0, iw)
    item_set_value("EXIT PRICE", param['trade_items'], 3, 0, iw)
    item_set_value("POSITION", param['trade_items'], 4, 0, iw)
    item_set_value("HOLDING", param['trade_items'], 5, 0, iw)
    item_set_value("PNL", param['trade_items'], 6, 0, iw)
    item_set_value("ENTRY TIME", param['trade_items'], 7, 0, iw)
    item_set_value("EXIT TIME", param['trade_items'], 8, 0, iw)
    item_set_value("FOS", param['trade_items'], 9, 0, iw)
    item_set_value("TRADE TYPE", param['trade_items'], 10, 0, iw)
    item_set_value("EXIT", param['trade_items'], 11, 0, iw)
    #param['trade_items'][0] = "SYMBOL"
    #print("param['trade_items']: ",param['trade_items'])
    return


def create_datepicker(param, param_name, tag=''):
    if tag=='':
        tag = param_name
    param[param_name] = None
    def datepicker_f(change):
        param[param_name] = change.new
        print(param[param_name])
    datepicker_w = widgets.DatePicker(
        description=tag,
        disabled=False,
        layout={'width': bw}, style=style
    )
    datepicker_w.observe(datepicker_f,'value')
    return datepicker_w




def create_dropdown(param, param_name, param_list, param_value, tag=''):
    if tag=='':
        tag = param_name
    param[param_name] = param_value
    def dropdown_f(change):
        param[param_name] = change.new
        #print("param[param_name]:",param[param_name])
    #tradeDirection_w = interactive(tradeDirection_f, tradeDirection=['BOTH','LONG','SHORT'])
    dropdown_w=widgets.Dropdown(
        options=param_list,
        value=param[param_name],
        description=tag,
        layout={'width': bw}, style=style
    )
    dropdown_w.observe(dropdown_f, 'value')
    return dropdown_w



def create_checkbox(param, param_name, status, tag=''):
    if tag=='':
        tag = param_name
    param[param_name] = status
    def checkbox_f(change):
        param[param_name] = change.new
    checkbox_w = widgets.Checkbox(
        value=param[param_name],
        description=tag,
        disabled=False,
        indent=False,
        layout={'width': bw}
    )
    checkbox_w.observe(checkbox_f, 'value')
    return checkbox_w


def create_text(param, param_name, param_value, tag=''):
    if tag=='':
        tag = param_name
    param[param_name] = param_value
    #def label_f(change):
    #    param[param_name] = change.new
    label_w=widgets.Text(value=param[param_name],description=tag, disabled=False, layout={'width': bw}, style=style)
    #label_w.observe(label_f,'value')
    return label_w




def create_inttext(param, param_name, param_value, tag=''):
    if tag=='':
        tag = param_name
    param[param_name] = param_value
    def inttext_f(change):
        param[param_name] = change.new
    inttext_w=widgets.IntText(value=param[param_name],description=tag,\
                                  disabled=False, layout={'width': bw}, style=style)
    inttext_w.observe(inttext_f,'value')
    return inttext_w




def create_boundedinttext(param, param_name, param_value, min, max, step, tag=''):
    if tag=='':
        tag = param_name
    param[param_name] = param_value
    def inttext_f(change):
        param[param_name] = change.new
    inttext_w=widgets.BoundedIntText(value=param[param_name],min=min, max=max, step=step,description=tag,\
                                  disabled=False, layout={'width': bw}, style=style)
    inttext_w.observe(inttext_f,'value')
    return inttext_w



def create_floattext(param, param_name, param_value, tag=''):
    if tag=='':
        tag = param_name
    param[param_name] = param_value
    def floattext_f(change):
        param[param_name] = change.new
    floattext_w=widgets.FloatText(value=param[param_name],description=tag,\
                                  disabled=False, layout={'width': bw}, style=style)
    floattext_w.observe(floattext_f,'value')
    return floattext_w



def create_timepicker(param, param_name, param_value, tag=''):
    if tag=='':
        tag = param_name
    param[param_name] = param_value
    def w_f(change):
        param[param_name] = change.new
    w=widgets.TimePicker(value=param[param_name], description=tag, disabled=False, layout={'width': bw}, style=style)
    w.observe(w_f,'value')
    return w
    


def create_boundedfloattext(param, param_name, param_value, min, max, step, tag=''):
    if tag=='':
        tag = param_name
    param[param_name] = param_value
    def floattext_f(change):
        param[param_name] = change.new
    floattext_w=widgets.BoundedFloatText(value=param[param_name],min=min, max=max, step=step, description=tag,\
                                  disabled=False, layout={'width': bw}, style=style)
    floattext_w.observe(floattext_f,'value')
    return floattext_w




def create_multiselect(param, param_name, param_value, param_value_list, tag=''):
    if tag=='':
        tag = param_name
    param[param_name] = param_value
    def multiselect_f(change):
        param[param_name] = change.new
    multiselect_w=widgets.SelectMultiple(options=param_value_list,value=param_value,description=tag, disabled=False)
    multiselect_W.observe(multiselect_f,'value')
    return multiselect_w



def create_select_deselect_pair(param, param_name, param_value, param_value_list, tag=''):
    param[param_name] = param_value
    display_selected_list = param_value

    if tag=='':
        S1='Select:'
        S2='Selected:'
    else:
        S1=tag
        S2='NOT ' + tag
    
    # Sample items for selection
    items = param_value_list
    #items = ['Option A', 'Option B', 'Option C', 'Option D']
    rows = 100 if tag=='To Trade' else 5
    # Create a SelectMultiple widget for selecting multiple items
    select_multiple = widgets.SelectMultiple(options=items,description=S1,disabled=False, rows=rows)

    # Create a SelectMultiple widget for displaying selected items
    display_selected = widgets.SelectMultiple(options=[],description=S2,disabled=False, rows=rows)

    def update_display_selected(change):
        for v in select_multiple.value:
            if v not in display_selected_list:
                display_selected_list.append(v)
        display_selected.options = display_selected_list
        param[param_name] = display_selected_list
        #print(param[param_name])
    
    def update_select_multiple(change):
        for v in display_selected.value:
            if v in display_selected_list:
                display_selected_list.remove(v)
        display_selected.options = display_selected_list
        param[param_name] = display_selected_list
        #print(param[param_name])
        #select_multiple.value = tuple(item for item in select_multiple.options if item not in display_selected.value)
    
    # Link the select_multiple widget to update display_selected when selection changes
    select_multiple.observe(update_display_selected, names='value')
    
    # Link the display_selected widget to update select_multiple when deselection occurs
    display_selected.observe(update_select_multiple, names='value')

    #display(select_multiple, display_selected)
    select_pair = HBox([select_multiple, display_selected])
    return select_pair



def create_button(param, param_name, param_value, tag=''):
    if tag=='':
        tag = param_name
    param[param_name] = param_value
    button = widgets.Button(description=tag,layout={'width': bw})
    #button.style.button_color = 'black'
    def on_button_clicked(b):
        print(param)
    button.on_click(on_button_clicked)
    return button



class create_inttext2():
    def __init__(self, param, param_name, param_value, tag=''):
        self.param = param
        self.param_name = param_name
        self.param_value = param_value
        self.tag = tag
        if self.tag=='':
            self.tag = self.param_name
        self.param[self.param_name] = self.param_value
    def inttext_f(self, change):
        #print("I am in class")
        self.param[self.param_value] = change.new
    def create(self):
        inttext_w=widgets.IntText(value=self.param[self.param_name],description=self.tag, disabled=False, layout={'width': bw}, style=style)
        inttext_w.observe(self.inttext_f,'value')
        return inttext_w
import ipywidgets as widgets
from IPython.display import display, HTML
import os, sys, copy
from .custom_widgets import *
from .auxfuncs import *

#=====================================================================
def create_widget(key, value):
    label = widgets.Label(value=key)
    label.add_class('ifk-widget-label')
    
    box = widgets.VBox([label])
    box.add_class('ifk-widget-box')
    
    if value is None:
        wid = widgets.Button(description=key)
        wid.add_class('ifk-widget-Button')
        label.value = ''
    elif isinstance(value, bool):
        wid = widgets.Checkbox(value=value, description=key, indent=False)
        box.add_class('ifk-widget-Checkbox')
        label.value = ''
    elif isinstance(value, int):
        wid = widgets.IntText(value=value)
        box.add_class('ifk-widget-IntText')
    elif isinstance(value, float):
        step = 10**(-count_decimal_places(value))
        wid = widgets.FloatText(value=value, step=step)
        box.add_class('ifk-widget-FloatText')
    elif isinstance(value, str):
        if os.sep in value:
            wid = FileAutocomplete(placeholder=value)
            box.add_class('ifk-widget-FileAutocomplete')
        elif 'password' in key.lower():
            wid = widgets.Password(placeholder=value)
            box.add_class('ifk-widget-Password')
        elif value.endswith('...'):
            wid = widgets.Textarea(placeholder=value[:-3])
            box.add_class('ifk-widget-Textarea')
        else:
            wid = widgets.Text(placeholder=value)
            box.add_class('ifk-widget-Text')
    elif isinstance(value, tuple):
        if value:
            wid = widgets.Dropdown(options=value, value=value[0])
            box.add_class('ifk-widget-Dropdown')
        else:
            wid = widgets.Label(value="(Empty list - no options)")
            box.add_class('ifk-widget-Label')
    else:
        wid = widgets.Label(value=f"Unsupported type: {type(value).__name__}")
        box.add_class('ifk-widget-Label')
    
    wid.add_class('ifk-widget-input')
    box.children = list(box.children) + [wid,]
    box.label = label
    box.wid = wid
    return box

#=====================================================================
def dict_to_form(input_dict, title=None, collapsed=None, nested=False):
    widgets_list = []
    widgets_dict = {}

    if collapsed is None and title is not None:
        title_widget = widgets.Label(value=title)
        title_widget.add_class('ifk-form-title')
        widgets_list.append(title_widget)

    for key, value in input_dict.items():
        hbox_items = []
        
        # Case: nested tuple group
        if isinstance(key, tuple) and isinstance(value, tuple):
            for sub_key, sub_val in zip(key, value):
                wid = create_widget(sub_key, sub_val)
                widgets_dict[sub_key] = wid
                hbox_items.append(wid)

        elif isinstance(value, dict):
            # Case: nested dictionary group
            sub_vbox, sub_widgets_dict = dict_to_form(value, title=key, collapsed=True, nested=True)
            widgets_dict.update(sub_widgets_dict)
            hbox_items.append(sub_vbox)
            
        else:
            wid = create_widget(key, value)
            widgets_dict[key] = wid
            hbox_items.append(wid)
            
        hbox = widgets.HBox(hbox_items)
        hbox.add_class('ifk-form-hbox')
        widgets_list.append(hbox)
        
    if collapsed is not None:
        vbox = CollapsibleVBox(widgets_list, title=title, collapsed=collapsed)
        vbox.toggle_button.add_class('ifk-form-toggle-button')
        vbox.label.add_class('ifk-widget-label')
        vbox.layout.width = '100%'
    else:
        vbox = widgets.VBox(widgets_list)

    if not nested: vbox.add_class('ifk-form')

    return vbox, widgets_dict

#=====================================================================
class Form(object):
    def __init__(self, input_dict, title=None, collapsed=None, max_width=600,
                 mandatory=None, disable=None, hide=None, check=None):
        
        self.input_dict = input_dict
        self.title = title
        self.collapsed = collapsed
        self.mandatory = mandatory
        self.disable = disable
        self.hide = hide
        self.check = check

        self.vbox, self.widgets_dict = dict_to_form(input_dict, title=title, collapsed=collapsed)
        self.vbox.layout.max_width = f'{max_width}px'

        if isinstance(mandatory, list):
            for key in mandatory:
                wid = self.widgets_dict[key]
                wid.label.value = f"{wid.label.value} *"

        self.disable_conditions = self.add_observer(disable, self.update_disable)
        self.hide_conditions = self.add_observer(hide, self.update_hide)
        self.check_conditions = self.add_observer(check, self.update_check)

        # Set initial state for disable and hide conditions
        self.update_disable()
        self.update_hide()
        self.update_check()

    #=====================================================================
    def add_observer(self, conditions, func):
        # Store conditions as a dictionary of widgets and functions
        conditions_out = {}
        if isinstance(conditions, dict):
            for key, val in conditions.items():
                if key in self.widgets_dict:
                    if callable(val):
                        wid = self.widgets_dict[key]
                        conditions_out[wid] = val

            # The function will be called when any of the widgets change
            for key, wid in self.widgets_dict.items():
                wid.wid.observe(func, names='value')

        return conditions_out
        
    #=====================================================================
    @throttle(0.2)
    def update_disable(self, change=None):
        if hasattr(self, 'disable_conditions'):
            value_dict = self.get_values()
            for wid, condition in self.disable_conditions.items():
                wid.wid.disabled = condition(value_dict)

    #=====================================================================
    @throttle(0.2)
    def update_hide(self, change=None):
        if hasattr(self, 'hide_conditions'):
            value_dict = self.get_values()
            for wid, condition in self.hide_conditions.items():
                if condition(value_dict):
                    wid.layout.display = 'none'
                else:
                    wid.layout.display = 'block'
        
    #=====================================================================
    @throttle(0.2)
    def update_check(self, change=None):
        if hasattr(self, 'check_conditions'):
            value_dict = self.get_values()
            for wid, condition in self.check_conditions.items():
                if condition(value_dict):
                    wid.wid.remove_class('ifk-widget-input-error')
                else:
                    wid.wid.add_class('ifk-widget-input-error')

    #=====================================================================
    def display(self):
        display(self.vbox)

    #=====================================================================
    def get_values(self):
        out = {key: wid.wid.value for key, wid in self.widgets_dict.items() if hasattr(wid.wid, 'value')}
        return out
    
    #=====================================================================
    def check_and_return_values(self):
        out = {}
        for key, wid in self.widgets_dict.items():
            if hasattr(wid.wid, 'value'):
                value = wid.wid.value
                disabled = wid.wid.disabled
                hidden = wid.layout.display == 'none'
                mandatory = key in self.mandatory if self.mandatory else False
                
                if value == '' and mandatory:
                    raise ValueError(f"Mandatory field '{key}' is empty.")
                
                elif not (disabled or hidden):
                    out[key] = value

        return out
    
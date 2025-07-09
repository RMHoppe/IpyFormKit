import ipywidgets as widgets
from traitlets import Any, observe
import numpy as np
import os

class FileAutocomplete(widgets.VBox):
    def __init__(self, root_path='./', placeholder='Start typing a file name...', max_results=99, **kwargs):
        super().__init__()
        
        self.root_path = root_path
        self.max_results = max_results

        # Main input field
        self.text = widgets.Text(placeholder=placeholder, **kwargs)
        self.layout.min_width = self.text.layout.min_width
        self.layout.width = '100%'
        self.layout.overflow = 'visible'
        self.text.layout.margin = '0px'
        self.text.layout.width = '100%'
        
        # Container for suggestions (styled like a dropdown)
        self.suggestions_box = widgets.VBox()
        self.suggestions_box.add_class('suggestion-box')
        self.children = [self.text, self.suggestions_box]
        self.text.observe(self._on_text_change, names='value')
        self.add_class('file-autocomplete')
    
    def _on_text_change(self, change):
        typed = change['new']
        matches = self._get_matching_files(typed)
        self._update_suggestions(matches)
    
    def _get_matching_files(self, path):
        try:
            if os.sep in path:
                folder = path[:path.rindex(os.sep)+1]
                prefix = path[path.rindex(os.sep)+1:]
            else:
                folder = ''
                prefix = path

            abs_folder_path = os.path.join(self.root_path, folder)
            files = os.listdir(abs_folder_path)
            matches = [folder + f for f in files if prefix in f]
            return sorted(matches)[:self.max_results]
        except Exception:
            return []

    def _update_suggestions(self, matches, clicked=False):
        suggestion_widgets = []
        if not matches:
            label = widgets.Label(value='No matches found')
            suggestion_widgets.append(label)
        else:
            if clicked and len(matches)==1:
                if matches[0] == self.text.value:
                    self.suggestions_box.children = []
                    return
                
            for i, match in enumerate(matches):
                abs_path = os.path.join(self.root_path, match)
                is_dir = os.path.isdir(abs_path)
                if i < len(self.suggestions_box.children) and hasattr(self.suggestions_box.children[0], 'children'):
                    suggestion = self.suggestions_box.children[i]
                    suggestion = self._reuse_suggestion(suggestion, match, is_dir)
                else:
                    suggestion = self._create_suggestion(match, is_dir)

                suggestion_widgets.append(suggestion)

        self.suggestions_box.children = suggestion_widgets

    def _create_suggestion(self, match, is_dir):
        icon_html = '\U0001F4C1' if is_dir else '\U0001F4C4'
        icon_widget = widgets.Label(value=icon_html)
        icon_widget.add_class('file-autocomplete-icon')

        if os.sep in match:
            description = match[match.rindex(os.sep)+1:]
        else:
            description = match

        if is_dir:
            description += os.sep
            match += os.sep

        text_button = widgets.Button(description=description)
        text_button.file = match
        text_button.on_click(self._on_suggestion_clicked)

        suggestion = widgets.HBox(
            [icon_widget, text_button],
            layout=widgets.Layout(align_items='center', padding='0px', margin='0px')
        )
        
        suggestion.add_class('autocomplete-suggestions-hbox')
        text_button.add_class('autocomplete-suggestions')
        return suggestion
    
    def _reuse_suggestion(self, suggestion, match, is_dir):
        if os.sep in match:
            description = match[match.rindex(os.sep)+1:]
        else:
            description = match

        if is_dir:
            description += os.sep
            match += os.sep

        suggestion.children[1].description = description
        suggestion.children[1].file = match
        suggestion.children[0].value = '\U0001F4C1' if is_dir else '\U0001F4C4'
        return suggestion

    def _on_suggestion_clicked(self, button):
        matches = self._get_matching_files(button.file)
        self.text.value = button.file
        self._update_suggestions(matches, clicked=True)

    def observe(self, *args, **kwargs):
        if hasattr(self, 'text'):
            # If the text widget has an observe method, call it
            return self.text.observe(*args, **kwargs)
        
        # Otherwise, call the superclass observe method
        return super().observe(*args, **kwargs)
        
    @property
    def disabled(self):
        return self.text.disabled
    
    @disabled.setter
    def disabled(self, val):
        self.text.disabled = val

    @property
    def value(self):
        return self.text.value
    
    @value.setter
    def value(self, val):
        self.text.value = val
    
class CollapsibleVBox(widgets.VBox):
    def __init__(self, children=None, title='Section', collapsed=False):
        self.collapsed = collapsed
        
        # Collapse/expand button (not toggle)
        self.toggle_button = widgets.Button(
            tooltip="Expand/Collapse",
            description='\u25B6' if collapsed else '\u25BC',
            layout=widgets.Layout(width='40px', height='32px'),
        )
        
        self.label = widgets.HTML(
            value=f"{title}",
            layout=widgets.Layout(align_self='center', margin='0 8px')
        )
        
        self.header = widgets.HBox(
            [self.toggle_button, self.label],
            layout=widgets.Layout(align_items='center', margin='5px 0 0 0')
        )
        
        self.content_box = widgets.VBox(children or [])
        self.content_box.layout.display = 'none' if collapsed else 'block'
        self.content_box.layout.padding = '0 0 0 10px'
        
        super().__init__([self.header, self.content_box])
        
        self.toggle_button.on_click(self._on_toggle_click)

    def _on_toggle_click(self, b):
        self.collapsed = not self.collapsed
        self.content_box.layout.display = 'none' if self.collapsed else 'block'
        self.toggle_button.description = '\u25B6' if self.collapsed else '\u25BC'


class ArraySlider(widgets.Box):
    def __init__(self, array, **kwargs):
        super().__init__()
        self.array = np.asarray(array)

        self.slider = widgets.IntSlider(min=0, max=len(array)-1, step=1, readout=False, **kwargs)
        self.readout = widgets.Label(value=str(self.array[0]))
        self.children = [self.slider, self.readout]

        # Update readout on slider change
        self.slider.observe(self._update_value, names='value')

        # Set initial value
        self._update_value({'new': self.slider.value})

        self.add_class('array-slider')
        self.readout.add_class('array-slider-readout')
        self.slider.add_class('array-slider-slider')

    def _update_value(self, change):
        val = self.array[change['new']]
        self.value = val  # this updates the trait
        self.readout.value = str(val)

    @observe('value')
    def _value_changed(self, change):
        # Optional: If the value is updated externally, update the slider position
        try:
            idx = np.where(self.array == change['new'])[0][0]
            self.slider.value = idx
        except IndexError:
            pass
        
    @property
    def disabled(self):
        return self.slider.disabled
    
    @disabled.setter
    def disabled(self, val):
        self.slider.disabled = val


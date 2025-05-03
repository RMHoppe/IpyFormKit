import ipywidgets as widgets
from IPython.display import display, HTML, clear_output
from .custom_widgets import CollapsibleVBox, FileAutocomplete
import os, copy
from .launch import launch
from .m3dis import m3dis

# Inject VS Code themed CSS
launcher_stylesheet = """
<style>
             
:root {
  --jp-ui-font-color0: var(--vscode-editorWidget-foreground, var(--jp-ui-font-color0));
  --jp-ui-font-color1: var(--vscode-editorWidget-foreground, var(--jp-ui-font-color1));
  --jp-ui-font-color2: var(--vscode-editorWidget-foreground, var(--jp-ui-font-color2));
  --jp-widgets-readout-color: var(--vscode-editorWidget-foreground, var(--jp-widgets-readout-color)) !important;
  --jp-layout-color0: var(--vscode-editorWidget-background);
  --jp-layout-color1: var(--vscode-editor-background);
  --jp-layout-color2: var(--vscode-list-inactiveSelectionBackground);
  --jp-layout-color3: red;
  --jp-widgets-color: var(--vscode-editorWidget-foreground, var(--jp-ui-font-color0));
  --jp-widgets-label-color: var(--vscode-editorWidget-foreground, var(--jp-ui-font-color0));
  --jp-widgets-input-color: var(--vscode-editorWidget-foreground, var(--jp-ui-font-color0));
  --jp-widgets-input-background-color: var(--vscode-editor-background);
  --jp-widgets-input-border-color: var(--vscode-editorWidget-border, lightgrey);
  --jp-widgets-inline-width: 100%;
}
             
.widget-text {
    min-width: 50px;
}
             
.cell-output-ipywidget-background {
    background-color: var(--vscode-editor-background) !important;
}

.masonry-form {
  column-width: 400px;
  column-gap: 16px;
  display: inline-block;
}

.widget-form {
    display: inline-block;
    width: 100%;
    margin: 8px 0 8px 0;
    break-inside: avoid;
    background-color: var(--jp-layout-color0);
    padding: 2px 10px 10px 10px;
    border: 1px solid var(--jp-widgets-input-border-color);
}
             
.widget-form-collapse {
    background-color: var(--jp-layout-color0);
}
             
.widget-form-input {
    margin: 0px 2px 2px 2px;
    width: 100%;
}      
             
.widget-form-input-label {
    margin: 2px 2px 0px 2px;
    width: 100%;
}      
             
.widget-form-input-box {
    overflow: visible;
    height: auto;
    margin: 0 10px 0 0;
    display: flex;
}

.widget-form-input-box.reversed {
    flex-direction: column-reverse;
}    
             
.widget-form-hbox {
    overflow: visible;
    display: flex;
}
             
.widget-form-title {
    color: var(--jp-layout-color2);
    font-weight: bold;
    font-style: italic;
    font-size: 1.5em;
    margin: 0px;
    padding: 0px;
    text-align: right;
}

</style>
"""

#=====================================================================
def create_widget(key, value):
    label = widgets.Label(value=key)
    label.add_class('widget-form-input-label')
    
    box = widgets.VBox([label])
    box.add_class('widget-form-input-box')
    
    if isinstance(value, bool):
        wid = widgets.Checkbox(value=value, description=key, indent=False)
        label.layout.height = '0px'
        box.add_class('reversed')
    elif isinstance(value, int):
        wid = widgets.IntText(value=value)
        box.layout.width = '100px'
    elif isinstance(value, float):
        wid = widgets.FloatText(value=value)
        box.layout.width = '100px'
    elif isinstance(value, str):
        if os.sep in value:
            wid = FileAutocomplete(placeholder=value)
        else:
            wid = widgets.Text(placeholder=value)
        box.layout.flex = '1'
    elif isinstance(value, list):
        if value:
            wid = widgets.Dropdown(options=value, value=value[0])
        else:
            wid = widgets.Label(value="(Empty list - no options)")
    else:
        wid = widgets.Label(value=f"Unsupported type: {type(value).__name__}")
    
    wid.add_class('widget-form-input')
    
    box.children = list(box.children) + [wid,]
    return box

#=====================================================================
def dict_to_widgets(input_dict, advanced=None, border=True, title=None):
    widgets_list = []
    widgets_dict = {}

    if title is not None:
        title_widget = widgets.Label(value=title)
        title_widget.add_class('widget-form-title')
        widgets_list.append(title_widget)

    for key, value in input_dict.items():
        # Case: nested tuple group
        if isinstance(key, tuple) and isinstance(value, tuple):
            hbox_items = []
            for sub_key, sub_val in zip(key, value):
                wid = create_widget(sub_key, sub_val)
                widgets_dict[sub_key] = wid.children[-1]
                hbox_items.append(wid)
            
            box = widgets.HBox(hbox_items)
            box.add_class('widget-form-hbox')
            widgets_list.append(box)

        else:
            wid = create_widget(key, value)
            widgets_dict[key] = wid.children[-1]
            widgets_list.append(wid)

    if advanced:
        accwid, accdict = dict_to_widgets(advanced, border=False)
        accord = CollapsibleVBox(children=(accwid,), title='advanced', collapsed=True)
        accord.toggle_button.add_class('widget-form-collapse')
        accord.children[-1].layout.margin = '2px 2px 2px 10px'
        widgets_dict.update(accdict)
        widgets_list.append(accord)
        
    box = widgets.VBox(widgets_list)
    if border:
      box.add_class('widget-form')

    return box, widgets_dict

#=====================================================================
class launcher():
  #=====================================================================
  def __init__(self):
    display(HTML(launcher_stylesheet))

    inputs = {}
    Box = widgets.Box()
    Box.add_class('masonry-form')

    params = {
        ('atmos_format', 'atmos_file'): (['Marcs', 'Stagger', 'Stagger2', 'Co5bold', 'Text'],
                                        'input_multi3d/atmos/p5777_g+4.4_m0.0_t01_st_z+0.00_a+0.00_c+0.00_n+0.00_o+0.00_r+0.00_s+0.00.mod'),
        ('vmic', 'FeH'): (-1.0, 0.0),
        ('nx', 'ny', 'nz'): (1, 1, 128),}
    advanced = {
        'dims':8,
        ('use_rho', 'use_ne'): (True, True),}


    sub, inputs['atmos_params'] = dict_to_widgets(params, advanced=advanced, title='atmos_params')
    Box.children += (sub,)

    params = {
        'atom_file': './input_multi3d/atoms/atom.ba06',
        ('abundance', 'relative_abundance'): (2.11, False),}
    advanced = {
        ('convlim', 'convmax'): (1e-2, 1e-3),}

    sub, inputs['atom_params'] = dict_to_widgets(params, advanced=advanced, title='atom_params')
    Box.children += (sub,)

    params = {
        ('maxiter', 'ng_step'): (99, -1),
        'custom_mu':'1.0 0.8 0.6 0.4 0.2',}
    advanced = {
        ('m1d_legacy_mode','decouple_continuum'): (False, True),
        ('rotate_atmos', 'rotate_continuum'): (True, True),
        ('short_scheme', 'short_ntheta', 'short_nphi'): (['radau', 'lobatto', 'gauss', 'disk_center', 'set_a2', 'set_a4', 'set_a6', 'set_a8', 'set_b4', 'set_b6', 'set_b8'], 2, 4),
        ('long_scheme', 'long_ntheta', 'long_nphi'): (['radau', 'lobatto', 'gauss', 'custom', 'disk_center', 'set_a2', 'set_a4', 'set_a6', 'set_a8', 'set_b4', 'set_b6', 'set_b8'], 4, 4),}

    sub, inputs['m3d_params'] = dict_to_widgets(params, advanced=advanced, title='m3d_params')
    Box.children += (sub,)

    params = {
        'abundance':'C=8.52, O=8.75, Ni=6.22',
        'absmet_file': './input_multi3d/absmet',}
    advanced = {
        'abund_file': './input_multi3d/abund/abund_magg',}
    sub, inputs['composition_params'] = dict_to_widgets(params, advanced=advanced, title='composition_params')
    Box.children += (sub,)

    params = {
        ('aa_blue', 'aa_red', 'R'): (4200, 4300, 1e5),
        'lam_file': './file_with_wavelengths.txt',}
    sub, inputs['spectrum_params'] = dict_to_widgets(params, title='spectrum_params')
    Box.children += (sub,)

    launchName = widgets.Text(description='Input File:', placeholder='ba_test1')
    launchButton = widgets.Button(description='Launch')
    overwrite = widgets.ToggleButton(description='Overwrite', value=False)
    verbose = widgets.ToggleButton(description='verbose', value=False)
    buttons = widgets.HBox([launchButton, overwrite, verbose])
    Box.children += (widgets.VBox([launchName, buttons]),)

    def _on_launch_click(btn):
        """Launch the M3DIS simulation."""
        # Get the values from the widgets
        nml = {}
        for key in inputs.keys():
          settings = {k:v.value for k, v in inputs[key].items() if v.value}
          if settings != {}:
            nml[key] = settings

        with output:
          clear_output(wait=True)
          name = launchName.value
          v = 2 if verbose.value else 1
          o = overwrite.value
          # Launch M3DIS with the parameters
          if name:
            output_folder, ok = launch(name, nml_settings=nml, overwrite=o, verbose=v)
            if ok:
                if os.sep in name:
                  name = name.split(os.sep)[-1]

                print('reading ' + output_folder)
                self.__dict__[name] = m3dis.read(output_folder)
          else:
            print("Please enter a name for the input file.")

    launchButton.on_click(_on_launch_click)

    output = widgets.Output()
    display(Box, output)

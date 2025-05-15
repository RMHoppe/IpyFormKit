# IpyFormKit

IpyFormKit is a Python library for creating dynamic, interactive forms using `ipywidgets` in Jupyter notebooks. It simplifies the process of building forms for data entry, configuration, or experimentation with minimal code.

## Features

- **Dynamic Forms**: Automatically generate forms from dictionaries with support for various input types (text, numbers, dropdowns, checkboxes, etc.).
- **Custom Widgets**: Includes specialized widgets like `FileAutocomplete` for file selection and `CollapsibleVBox` for collapsible sections.
- **Validation and Logic**: Add conditions to disable, hide, or validate fields dynamically based on user input.
- **Masonry Layout**: Organize multiple forms in a responsive masonry-style layout.
- **Adaptive CSS Styling** Seamless integration with Jupyter Notebook/Lab, Google Colab and VScode themes.

<div style="display: flex; justify-content: space-around;">
  <img src="https://raw.githubusercontent.com/RMHoppe/IpyFormKit/refs/heads/main/images/jupyterlab-light.png" alt="Jupyter Lab Light Example" width="300">
  <img src="https://raw.githubusercontent.com/RMHoppe/IpyFormKit/refs/heads/main/images/jupyterlab-dark.png" alt="Jupyter Lab Dark Example" width="300">
  <img src="https://raw.githubusercontent.com/RMHoppe/IpyFormKit/refs/heads/main/images/vscode.png" alt="VSCode Example" width="300">
  <img src="https://raw.githubusercontent.com/RMHoppe/IpyFormKit/refs/heads/main/images/googlecolab.png" alt="Google Colab Example" width="300">
</div>


## Installation
```bash
pip install ipyformkit
```

For use in Google Colab one currently needs to downgrade ipywidgets as widgets are not displayed otherwise.
```bash
pip install ipyformkit
pip install "ipywidgets>=7,<8"
```

## Example Usage
```python
import ipyformkit as ifk

test = {'first name':'Zaphod',
        'last name':'Beeblebrox',
        ('age', 'gender'):(-200, ('two-headed', 'male', 'female', 'non-binary')),
        'height':2.05,
        'date of birth':'Unknown (he probably lied about it anyway)',
        ('Input 1', 'Input 2', 'Input 3', 'Input 4'):('president', 'of', 'the', 'galaxy'),
        ('street', 'house'):('Heart of Gold Spaceship', 1),
        'additional info':{'hobbies':'Kidnapping himself, avoiding responsibility, being outrageous',}
       }


mandatory = ['first name', 'last name', 'age']
disable = {'last name': lambda d: d['first name'] == '',}
hide = {'house': lambda d: d['street'] == '',}
check = {'age': lambda d: d['age'] > 0,}

form = ifk.Form(test, title='Test Form', mandatory=mandatory, disable=disable, hide=hide, check=check, max_width=400)
form.display()
```

Text input is converted into placeholders instead of values by default. One can set multiple values at once by supplying a dictionary to the `.set_values()` method. The dictionary keys should match the field names in the form. The values can be any type supported by ipywidgets.

```python
form.set_values({'first name': 'Arthur', 'last name': 'Dent', 'age': 42})
```

Retrieve values:
```python
values = form.get_values() # returns unchecked values
out = form.check_and_return_values() # return checked values and highlights missing mandatory inputs
```

## Documentation
`ifk.Form()` is a class that creates a form using ipyipywidgets. It can be displayed using its `.display()` method. It takes a dictionary as input and generates the corresponding ipywidgets. The class also supports various features such as validation, conditional display, and custom styling. The arguments `mandatory`, `disable`, `hide` and `check` expect dictionaries with the affected field name as a key and a function as a value. The function takes the current form inputs as a dictionary and returns a boolean value. The function should return True if the field should be disabled, hidden or checked, and False otherwise. The `.get_values()` method returns the current values of each input field without applying any validation. The `.check_and_return_values()` method will return the current values but validate that all checks are passed.

| **Dictionary Value Type**   | **Created Widget**       | **Notes**                                                                  |
|-----------------------------|--------------------------|----------------------------------------------------------------------------|
| `bool`                      | `ipywidgets.Checkbox`    | A checkbox with the dictionary key as its description.                     |
| `int`                       | `ipywidgets.IntText`     | A text box for integer input.                                              |
| `float`                     | `ipywidgets.FloatText`   | A text box for float input with step size based on decimal places.         |
| `str` (contains `os.sep`)   | `FileAutocomplete`       | A custom widget for selecting files from the working directory.            |
| `str` (contains "password") | `ipywidgets.Password`    | A password input field.                                                    |
| `str` (ends with `...`)     | `ipywidgets.Textarea`    | A multi-line text area with the placeholder text (excluding `...`).        |
| `str` (other cases)         | `ipywidgets.Text`        | A single-line text input field with the string as a placeholder.           |
| `tuple`                     | `ipywidgets.Dropdown`    | A dropdown menu with the tuple values as options.                          |
| `dictionary`                | `...`                    | A collapsible sub-form with the dictionary mapped according to this table. |
| Other types                 | `ipywidgets.Label`       | A label displaying "Unsupported type: <type_name>".                        |
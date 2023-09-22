from IPython.core.magic import register_line_magic
import ipywidgets as widgets
import rich
from manager.util import Fairy

fairy = Fairy()

wid_login_file = widgets.FileUpload(
    description='Upload login file', accept='.login',  multiple=False)
wid_import_btn = widgets.Button(
    description='Import login file', disabled=False)

wid_account = widgets.Text(description='Account')
wid_password = widgets.Password(description='Password')
wid_username = widgets.Dropdown(options=list(fairy.data_config.keys()), description='Username')
wid_project = widgets.Text(description='Project')

wid_login_btn = widgets.Button(description='Login', disabled=False)

def import_btn(wid_import_btn):
    _key = list(wid_login_file.value.keys())[0]
    _content = eval(wid_login_file.value[_key]['content'].decode())
    wid_account.value = _content['account']
    wid_password.value = _content['password']
    wid_username.value = _content['username']
    wid_project.value = _content['project']

def login_btn(wid_login_btn):
    from manager.util import Cipher
    cipher = Cipher(wid_account.value, wid_password.value)
    if cipher.check(fairy.data_config[wid_username.value]):
        rich.print('設定完畢，歡迎使用。')

wid_import_btn.on_click(import_btn)
wid_login_btn.on_click(login_btn)

@register_line_magic
def login_tool(line):
    display(
        widgets.VBox(
            [
                widgets.HBox([wid_login_file, wid_import_btn]),
                widgets.HBox([wid_account, wid_password, wid_username, wid_project]),
                widgets.HBox([wid_login_btn]),]
        )
    )


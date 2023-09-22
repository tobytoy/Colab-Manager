import os
import rich
from pathlib import Path
import ipywidgets as widgets
from google.colab import files
from manager.util import Fairy
from IPython.display import clear_output
from IPython.core.magic import register_line_magic


fairy = Fairy()
cipher = None

wid_login_file = widgets.FileUpload(
    description='Upload login file', accept='.login',  multiple=False)
wid_import_btn = widgets.Button(
    description='Import login file', disabled=False)

wid_account = widgets.Text(description='Account')
wid_password = widgets.Password(description='Password')
wid_username = widgets.Dropdown(options=list(
    fairy.data_config.keys()), description='Username')
wid_project = widgets.Text(description='Project')

wid_login_btn = widgets.Button(description='Login', disabled=False)



wid_upload_videos_btn = widgets.Button(
    description='Upload Videos', disabled=False)
wid_upload_datas_btn = widgets.Button(
    description='Upload Datas', disabled=False)

wid_video = widgets.Dropdown(
    options=[(item.name, item)
             for i, item in enumerate(list(fairy.video_root_path.glob('*.mp4')) +
                                      list(fairy.video_output_root_path.glob('*.mp4')))
             ],
    description='Video : ',
)
wid_data = widgets.Dropdown(
    options=[(item.name, item)
             for i, item in enumerate(list(fairy.data_root_path.glob('*.*')) +
                                      list(fairy.data_output_root_path.glob('*.*')))
             ],
    description='Data : ',
)


def import_btn(wid_import_btn):
    _key = list(wid_login_file.value.keys())[0]
    _content = eval(wid_login_file.value[_key]['content'].decode())
    wid_account.value = _content['account']
    wid_password.value = _content['password']
    wid_username.value = _content['username']
    wid_project.value = _content['project']


def login_btn(wid_login_btn):
    global cipher
    from manager.util import Cipher
    cipher = Cipher(wid_account.value, wid_password.value)
    # user_2 設定完要拿掉
    if wid_username.value in fairy.data_config.keys() or wid_username.value == 'user_2':
        if cipher.check(fairy.data_config[wid_username.value]):
            rich.print('設定完畢，歡迎使用。')
    else:
        rich.print('你不是使用者。')


def focus_video_fun():
    return list(fairy.video_root_path.glob('*.mp4')) \
            + list(fairy.video_output_root_path.glob('*.mp4'))

def focus_data_fun():
    return list(fairy.data_root_path.glob('*.xlsx')) \
            + list(fairy.data_output_root_path.glob('*.xlsx')) \
            + list(fairy.data_root_path.glob('*.json')) \
            + list(fairy.data_output_root_path.glob('*.json')) \
            + list(fairy.data_root_path.glob('*.pickle')) \
            + list(fairy.data_output_root_path.glob('*.pickle'))

def upload_videos_btn(wid_upload_videos_btn):
    uploaded = files.upload()
    for filename, file_data in uploaded.items():
        os.rename(filename, (fairy.video_root_path/filename))
    # update the videos dropdown
    wid_video.options = [(item.name, item) for i, item in enumerate(focus_video_fun())]
    

def upload_datas_btn(wid_upload_datas_btn):
    uploaded = files.upload()
    for filename, file_data in uploaded.items():
        os.rename(filename, (fairy.data_root_path/filename))
    # update the datas dropdown
    wid_data.options = [(item.name, item) for i, item in enumerate(focus_data_fun())]
        


wid_import_btn.on_click(import_btn)
wid_login_btn.on_click(login_btn)
wid_upload_videos_btn.on_click(upload_videos_btn)
wid_upload_datas_btn.on_click(upload_datas_btn)


@register_line_magic
def login_tool(line):
    clear_output()
    display(
        widgets.VBox(
            [
                widgets.HBox([wid_login_file, wid_import_btn]),
                widgets.HBox([wid_account, wid_password,
                             wid_username, wid_project]),
                widgets.HBox([wid_login_btn]),
            ]
        )
    )

@register_line_magic
def path_manager(line):
    clear_output()
    if cipher.check:
        display(
            widgets.VBox(
                [
                    widgets.HBox([wid_video, wid_upload_videos_btn]),
                    widgets.HBox([wid_data, wid_upload_datas_btn]),
                ]
            )
        )

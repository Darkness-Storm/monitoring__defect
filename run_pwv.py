import logging
import os
import webview

from contextlib import redirect_stdout, suppress
from io import StringIO

import config
from app.app import create_web_app
from app.models import TMPDIR



logger = logging.getLogger(__name__)
PORT = 5000
ROOT_URL = f'http://localhost:{PORT}'



def on_closing(app, tmp_dir):
    app.logger.info('SQA end')
    clean_tmp_files(tmp_dir)


def clean_tmp_files(tmp_dir):
    list_files = os.listdir(tmp_dir)
    for file in list_files:
        file_name = os.path.join(tmp_dir, file)
        with suppress(FileNotFoundError):
            os.remove(file_name)


def on_shown(tmp_dir):

    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)


if __name__ == '__main__':

    stream = StringIO()
    with redirect_stdout(stream):
        app = create_web_app('config.ProductionConfig')
        tmp_dir = os.path.join(app.static_folder, TMPDIR)
        window = webview.create_window(ROOT_URL, app)
        window.closing += lambda: on_closing(app, tmp_dir)
        window.title = 'SQA'
        webview.start(gui='cef', debug=True)

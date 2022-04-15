import os
from re import template
from time import sleep

from flask import request, jsonify, abort, send_file, render_template, url_for, Blueprint
from flask_wtf.form import FlaskForm
from peewee import OperationalError, DoesNotExist, PeeweeException
from playhouse.shortcuts import model_to_dict, dict_to_model

#from app import app
from app.models import *
from app.views.servises import *
from app.forms import *


common_bp = Blueprint('common', __name__, url_prefix='')


@common_bp.route('/')
def index():

    return render_template("index.html")


@common_bp.route('/get_attachment/<int:id>')
def send_attachment(id):
    try:
        att = Attachment.get_by_id(id)
        name, full_name = att.write_attachment_for_send()
        return send_file(full_name, as_attachment=True,
                         attachment_filename=name)
    except DoesNotExist:

        abort(404)


@common_bp.route('/reports', methods=['GET', 'POST'])
def reports():
    if request.method == 'POST':
        form = ReportForm()
        if form.validate():
            if form.r_reports.data == '1':
                file_name = report_was_is(form)
                if file_name:
                    url_file = get_url_attachment(file_name)
                    return jsonify(file_name=file_name, url_file=url_file)
                else:
                    abort(400)
            else:
                return jsonify(success=True)
        else:
            return render_template('report_form.html', main_form=form)
    elif request.method == 'GET':
        form = ReportForm()
        return render_template('report_form.html', main_form=form)

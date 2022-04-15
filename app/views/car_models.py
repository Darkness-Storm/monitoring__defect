from flask import request, jsonify, render_template, url_for, Blueprint

#from app import app
from app.views.servises import *
from app.models import ModelBus


carmodel_bp = Blueprint('model', __name__, url_prefix='/model')


@carmodel_bp.route('/all')
def models():

    models = ModelBus.select().order_by(ModelBus.descr)
    return render_template('models.html', models=models)
    

@carmodel_bp.route('/add')
def add_model():
    return jsonify(succces=True)


@carmodel_bp.route('/<int:id>')
def get_model(id):
    return jsonify(succces=True, id=id)
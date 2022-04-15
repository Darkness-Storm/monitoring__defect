#!flask/bin/python
from app.app import create_web_app
from app import models
#import config

app = create_web_app('config.DevelopConfig')
#models.create_table(models.database)
app.run()

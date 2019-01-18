from flask import Flask

app = Flask(__name__)

from app import routes, errors

app.secret_key = 'supersecretkeyy'
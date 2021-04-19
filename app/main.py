from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify
from time import strftime

import logging
import traceback

logger = logging.getLogger(__name__)
app = Flask(__name__)

from logstash_async.handler import AsynchronousLogstashHandler
from logstash_async.formatter import FlaskLogstashFormatter

LOGSTASH_HOST = "172.25.0.4"
LOGSTASH_DB_PATH = "/docker/app/app-data/flask_logstash.db"
LOGSTASH_TRANSPORT = "logstash_async.transport.BeatsTransport"
LOGSTASH_PORT = 5044

logstash_handler = AsynchronousLogstashHandler(
    LOGSTASH_HOST,
    LOGSTASH_PORT,
    database_path=LOGSTASH_DB_PATH,
    transport=LOGSTASH_TRANSPORT,
)
logstash_handler.formatter = FlaskLogstashFormatter(metadata={"beat": "myapp"})
app.logger.addHandler(logstash_handler)

@app.route("/")
@app.route("/index")
def get_index():
    """ Function for / and /index routes. """
    return "Hello! "


@app.route("/data")
def get_data():
    """ Function for /data route. """
    data = {
            "Grupo":"Grupo 3",
            "Turma":"78 AOJ",
            "Materia":"Microservices"
    }
    return jsonify(data)


@app.route("/error")
def get_nothing():
    """ Route for intentional error. """
    return foobar # Intencional Variavel nao existe


@app.after_request
def after_request(response):
    """ Logging after every request. """
    if response.status_code != 500:
        ts = strftime('[%Y-%b-%d %H:%M]')
        logger.info('%s %s %s %s %s %s',
                      ts,
                      request.remote_addr,
                      request.method,
                      request.scheme,
                      request.full_path,
                      response.status)
    return response


@app.errorhandler(Exception)
def exceptions(e):
    """ Logging after every Exception. """
    ts = strftime('[%Y-%b-%d %H:%M]')
    tb = traceback.format_exc()
    logger.error('%s %s %s %s %s 5xx INTERNAL SERVER ERROR\n%s',
                  ts,
                  request.remote_addr,
                  request.method,
                  request.scheme,
                  request.full_path,
                  tb)
    return "Internal Server Error", 500

if __name__ == '__main__':
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)
    app.run(host="127.0.0.1",port=8080)

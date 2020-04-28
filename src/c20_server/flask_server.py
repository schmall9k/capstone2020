import json
import os
import fakeredis
import datetime
from flask import Flask, request
from dotenv import load_dotenv
from c20_server.user import User
from c20_server.job import DocumentsJob
from c20_server import compute_jobs
from c20_server.job_manager import JobManager
from c20_server.job_translator import job_to_json, handle_jobs



def create_app(job_manager):
    app = Flask(__name__)

    # Note: endpoint names begin with an "_" so that Pylint does not complain
    # about unused functions.

    @app.route('/get_job')
    def _get_job():
        print('Server: Requesting Job From Job Queue...\n')
        requested_job = job_manager.request_job(User(100))
        job = job_to_json(requested_job)
        print('Server: Sending Job to client...\n')
        return job

    @app.route('/return_result', methods=['POST'])
    def _return_result():
        print('Receiving Data from Client ...\n')
        client_data = request.json
        print(client_data)
        if client_data is None:
            return {}, 400

        json_data = json.dumps(client_data)
        job_list = handle_jobs(json_data)
        print()
        for job in job_list:
            job_manager.add_job(job)
            print('Adding Job To Job Manager...')
            print(job, '\n')
        return {}, 200
    return app


if __name__ == '__main__':
    REDIS_SERVER = fakeredis.FakeServer()
    REDIS_SERVER.connected = True
    REDIS = fakeredis.FakeStrictRedis(server=REDIS_SERVER)
    load_dotenv()
    JOB_MANAGER = JobManager(database=REDIS)
    APP = create_app(JOB_MANAGER)
    APP.run(host='0.0.0.0')

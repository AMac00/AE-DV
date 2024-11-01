from flask import Flask, request, jsonify
from flasgger import Swagger
from flask_pymongo import PyMongo
import logging,time

__file__ = 'loadgen_api_{0}.log'.format(time.strftime("%m-%d-%Y_%H"))
logging.basicConfig(filename='/var/AgentEmulator/logs/{0}'.format(__file__), level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

# Database and PWD
app = Flask(__name__, instance_relative_config=False)
app.config["MONGO_URI"] = "mongodb://127.0.0.1:27017/aedb"
mongo_client = PyMongo(app)
db = mongo_client.db


template= {
    'swagger': "2.0",
    'info': {
        'title': 'Agent Emulator and Load Generator API',
    }
}

app = Flask(__name__)
swagger = Swagger(app, template=template)

app.config['SWAGGER'] = {
    'title': 'AE and LoadGen API Documenation',
    'uiversion': 3,
    'specs_route': '/swagger/'
}


@app.route('/loadgen')
def loadgen():
    """
    ---
    parameters:
      - name: status
        in: query
        type: string
        enum: ['start', 'stop']
        required: true
        default: stop
      - name: cpm
        in: query
        type: integer
        required: true
        default: 8
        description: Calls per Minute
    responses:
      200:
        description: LoadGenerator Response
    """
    status = request.args.get('status')
    if 'start' in status:
        lg_status = 1
    else:
        lg_status = 0
    cpm = request.args.get('cpm')
    logging.debug("status = {0}, cpm ={1}".format(status,cpm))
    col = db['loadgen']
    insert = {'status': lg_status, 'cpm': int(cpm)}
    col.update_one({'loadgen_id': 0}, {"$set": insert})
    loadgen_status = col.find_one({'loadgen_id': 0},{"_id": 0})
    return(jsonify(loadgen_status))


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8445,debug=True)
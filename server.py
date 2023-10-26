from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from standalone import Simulator

simulator = Simulator()

FlaskApp = Flask(__name__, template_folder='templates')
CORS(FlaskApp, resources={r"/simulador/*": {"origins": ["http://localhost:5000", "http://127.0.0.1:8888"]}})

@FlaskApp.route('/simulador/telescope/position', methods=['GET'])
def get_telescope_position():
    simulator.update()
    global data
    return data

@FlaskApp.route('/simulador/telescope/position', methods=['POST'])
def set_telescope_position():
    global data
    data = request.get_json()
        
    return jsonify({'status': 200})

@FlaskApp.route('/simulador/telescope/move', methods=['POST'])
def move_telescope():
    data = request.get_json()
    
    print(simulator.slew(data))
        
    return jsonify({'status': 200})

@FlaskApp.route('/')
def home():    
    return render_template('index.html')

if __name__ == '__main__':
    FlaskApp.run(port=8888, debug=False)

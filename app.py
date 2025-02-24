from flask import Flask, jsonify, render_template
from pyModbusTCP.client import ModbusClient
import threading

class FlaskApp(threading.Thread):
    def __init__(self, shared_state):
        super().__init__()
        self.shared_state = shared_state
        
        self.app = Flask(__name__, static_url_path='', 
                        static_folder='static', 
                        template_folder='templates')
        
        self.client = ModbusClient(host="127.0.0.1", port=502, unit_id=1)
        self.client.open()
        
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/status_<coil>', 'get_status', self.get_status)
        self.app.add_url_rule('/toggle_<coil>', 'toggle_coil', self.toggle_coil)
        self.app.add_url_rule('/control_<coil>', 'toggle_control', self.toggle_control)
    
    def index(self):
        return render_template('index.html')
    
    def get_status(self, coil):
        if coil in self.shared_state.driverHasControl:
            return jsonify({
                "state": "DRIVER" if self.shared_state.driverHasControl[coil] else "OFF" if not self.shared_state.coils_state[coil] else "ON",
                "user_control": not self.shared_state.driverHasControl[coil]
            })
        return jsonify({"error": "Invalid coil"}), 400
    
    def toggle_coil(self, coil):
        if coil in self.shared_state.driverHasControl and not self.shared_state.driverHasControl[coil]:
            self.shared_state.coils_state[coil] = not self.shared_state.coils_state[coil]
            
            if coil in ["b", "g", "m"]:
                belt_address = 4 if coil == "b" else 6 if coil == "g" else 8
                turn_address = 3 if coil == "b" else 5 if coil == "g" else 7
                self.client.write_single_coil(belt_address, self.shared_state.coils_state[coil])
                self.client.write_single_coil(turn_address, self.shared_state.coils_state[coil])
            elif coil == "entry":
                self.client.write_single_coil(0, self.shared_state.coils_state[coil])
            elif coil == "exit":
                self.client.write_single_coil(2, self.shared_state.coils_state[coil])
                
            return jsonify({"state": "ON" if self.shared_state.coils_state[coil] else "OFF"})
        return jsonify({"error": "Unauthorized"}), 403
    
    def toggle_control(self, coil):
        if coil in self.shared_state.driverHasControl:
            #print(self.shared_state.driverHasControl)
            self.shared_state.driverHasControl[coil] = not self.shared_state.driverHasControl[coil]
            #print(self.shared_state.driverHasControl)

            if not self.shared_state.driverHasControl[coil]:
                self.shared_state.coils_state[coil] = False
                
                if coil in ["b", "g", "m"]:
                    belt_address = 4 if coil == "b" else 6 if coil == "g" else 8
                    turn_address = 3 if coil == "b" else 5 if coil == "g" else 7
                    self.client.write_single_coil(belt_address, False)
                    self.client.write_single_coil(turn_address, False)
                elif coil == "entry":
                    self.client.write_single_coil(0, False)
                elif coil == "exit":
                    self.client.write_single_coil(2, False)

            return jsonify({"user_control": not self.shared_state.driverHasControl[coil]})
        return jsonify({"error": "Invalid coil"}), 400
    
    def run(self):
        print("[Flask] Lancement de l'API Flask...")
        self.app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
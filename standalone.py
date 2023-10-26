import sys

import requests
import validators
import threading

#from server import FlaskApp
from utils.conversion import Convertion
from utils.coordinates import Coordinates
from telescope import Telescope

from utils.instances import verify_coord_format

class Simulator():
    def __init__(self):
        self.telescope_status = {}
        self.telescope = Telescope()

        self._abort = threading.Event()
        # server_thread = threading.Thread(target=self.start_server)
        # server_thread.daemon = True  # Set the thread as a daemon to stop it when the main thread exits
        # server_thread.start()

        self.connect_telescope()

    # def start_server(self):
    #     try:
    #         FlaskApp.run(host="127.0.0.1", port=8888)
    #         print("SERVER ONLINE")
    #     except Exception as e: 
    #         print("SERVER OFF: ", e)

    def update(self):
        if self.telescope.connected:
            self.telescope_status = self.telescope.get_position()
            self.update_telescope_position()

    def tracking(self):
        """turn on or off sidereal movement"""
        if self.telescope_status:
            if self.telescope_status["tracking"]:
                self.telescope.set_track(False)
            else:
                self.telescope.set_track(True)  
    
    def update_telescope_position(self):
        ha = self.telescope_status["hour angle"]
        dec = self.telescope_status["declination"]
        data = {
            'right_ascension': Convertion.hours_to_hms(self.telescope_status["right ascension"]),
            'hour_angle': Convertion.hours_to_hms(ha),
            'declination': Convertion.degrees_to_dms(dec),
            'dec': dec,
            'ha': ha,
            'azimuth': self.telescope_status["azimuth"],
            'elevation': round(self.telescope_status["elevation"], 2),
            'tracking': self.telescope_status["tracking"],
            'sidereal': Convertion.hours_to_hms(self.telescope_status["sidereal"])
        }        
        url = f"http://127.0.0.1"
        if validators.url(url):
            try:
                response = requests.post(f"{url.rstrip('/')}:8888/simulador/telescope/position", json=data)
                if response.status_code == 200:
                    print("Telescope position updated successfully.")
                else:
                    print("Failed to update telescope position.")
            except Exception as e:
                print(e)
    
    def move_axis(self, axis):
        """move telescope slightly
        :param axis: int (0: North, 1: South, 2: East, 3: West)"""
        if self.telescope:
            try:
                self.telescope.move_axis(axis, 10)
            except Exception as e:
                print(e)

    def stop(self):
        self.btnAbort.setEnabled(False)
        """stops any movement (dome and telescope)"""
        self._abort.set()  
        if self.telescope.connected:            
            self.telescope.abort_slew()
            if self.telescope_status["tracking"]:
                self.telescope.set_track(False)
    
    def connect_telescope(self):
        self.telescope.connect()
    
    def slew(self, data):
        """Points the telescope to a given Target"""        
        self._abort.clear()
        
        if not verify_coord_format(data["ra"]) or not verify_coord_format(data["dec"]):
            return("RA and DEC invalids.")
        elif self.telescope.connected:            
            ra = Convertion.hms_to_hours(data["ra"])
            dec = Convertion.dms_to_degrees(data["dec"]) 
            sidereal = self.telescope_status["sidereal"]          
            ha = Convertion.ra_to_ah(ra, sidereal)
            latitude = "-22 32 04"
           
            try:                
                elevation, azimuth = Coordinates.get_elevation_azimuth(ha, dec, latitude)
                if elevation > 0 and elevation<=90:                    
                    self.telescope.set_track(True)
                    self.telescope.slew_async(ra, dec)
                    return("Moving.")
                else:
                    return("Object is not above horizon.")
            except Exception as e:
                return("Error poiting: " +str(e))



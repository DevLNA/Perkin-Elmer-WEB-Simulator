from utils.conversion import Convertion
from utils.coordinates import Coordinates
import win32com.client
import pythoncom
from threading import Thread, Event

class Telescope():  
    def __init__(self): 
        pythoncom.CoInitialize()
        self._telescope = win32com.client.Dispatch("ASCOM.Simulator.Telescope")
        self.tel_id = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch, self._telescope)  
        self._telescope = win32com.client.Dispatch(
            pythoncom.CoGetInterfaceAndReleaseStream(self.tel_id, pythoncom.IID_IDispatch))     
        self.connected = False
        self.coord = {}
        self.telescope_thread = None
        self.stop_event = Event()        

    def connect(self): 
        try:
            # self._telescope = win32com.client.Dispatch("ASCOM.Simulator.Telescope")            
            self._telescope.Connected = True
            self.set_site("-22:32:04", "-45:34:57", 1864)            
            self.connected = True
            self.telescope_thread = Thread(target = self.telescope_position)
            self.telescope_thread.start()
            # self.get_position() 
            return self._telescope.Name
        except Exception as e:
            self.connected = False
            print("Error connecting Telescope: "+str(e))
            return "Error. Check Telescope LOG." 
    
    def disconnect(self):
        if self.connected:
            self.connected = False
            self._telescope.Connected = False
    
    def set_site(self, latitude, longitude, altitude):
        if self.connected:
            self._telescope.SiteLatitude = Convertion.dms_to_degrees(latitude)
            self._telescope.SiteLongitude = Convertion.dms_to_degrees(longitude)
            self._telescope.SiteElevation = altitude
    
    def get_position(self):
        if self.connected:            
            return self.coord
        else:
            return None
        
    def telescope_position(self):
        pythoncom.CoInitialize()
        # telescope_com = win32com.client.Dispatch(
        #     pythoncom.CoGetInterfaceAndReleaseStream(self.tel_id, pythoncom.IID_IDispatch))
        while not (self.stop_event.wait(.5)):
            if self.connected:
                ha = Convertion.ra_to_ah(self._telescope.RightAscension, self._telescope.SiderealTime)
                self.coord = {
                    "right ascension" : self._telescope.RightAscension,
                    "declination" : self._telescope.Declination,
                    "sidereal" : self._telescope.SiderealTime,
                    "hour angle": ha,
                    "time limit" : Coordinates.get_observing_time(ha),
                    "airmass": Coordinates.get_airmass(self._telescope.Altitude),
                    "latitude": self._telescope.SiteLatitude,
                    "longitude": self._telescope.SiteLongitude,
                    "altitude": self._telescope.SiteElevation,
                    "utc" : self._telescope.UTCDate,
                    "tracking" : self._telescope.Tracking,
                    "elevation" : self._telescope.Altitude,
                    "azimuth" : self._telescope.Azimuth,
                    "at park" : self._telescope.AtPark,
                    "at home" : self._telescope.AtHome,
                    "slewing" : self._telescope.Slewing,
                    "can slew" : self._telescope.CanSlewAsync,
                    "can home" : self._telescope.CanFindHome,
                    "can slew_altaz" : self._telescope.CanSlewAltAzAsync,
                    "can park" : self._telescope.CanPark,
                    "can move ra": False,
                    "can move dec": False
                }   
                         
    def abort_slew(self):
        if self.connected:
            if not self._telescope.AtPark and self._telescope.Slewing:
                self._telescope.AbortSlew()
    
    def slew_async(self, ra, dec):
        pythoncom.CoInitialize()
        if self.connected:
            if not self._telescope.AtPark:
                if self._telescope.CanSlewAsync:
                    self._telescope.Tracking = True
                    self._telescope.SlewToCoordinatesAsync(ra, dec)  
        
    def set_track(self, state):
        pythoncom.CoInitialize()
        if self.connected:
            try:
                if state and self._telescope.CanSetTracking:
                    self._telescope.Tracking = True
                elif not state and self._telescope.CanSetTracking:
                    self._telescope.Tracking = False
                return True
            except Exception as e:
                print("Error Tracking: "+str(e))
                return False
    
    

            
    

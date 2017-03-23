# System imports
import configparser
import importlib

# Local imports
import power_controller

class MultiTenantDeviceAccess:

    def __init__(self):
        self.config_files = [ 'mtda.ini' ]
        self.power_controller = None
        self.usb_switches = []

    def target_on(self):
        if self.power_controller is not None:
            self.power_controller.on()

    def target_off(self):
        if self.power_controller is not None:
            self.power_controller.off()

    def load_config(self):
        parser = configparser.ConfigParser()
        configs_found = parser.read(self.config_files)
        if parser.has_section('power'):
            self.load_power_config(parser)
        if parser.has_section('usb'):
            self.load_usb_config(parser)
    
    def load_power_config(self, parser):
       try:
           # Get variant
           variant = parser.get('power', 'variant')
           # Try loading its support class
           mod = importlib.import_module(variant)
           factory = getattr(mod, 'instantiate')
           self.power_controller = factory()
           # Configure and probe the power controller
           self.power_controller.configure(dict(parser.items('power')))
           self.power_controller.probe()
       except configparser.NoOptionError:
           print('power controller variant not defined!')
       except ImportError:
           print('power controller "%s" could not be found/loaded!' % (variant))
    
    def load_usb_config(self, parser):
        try:
           # Get number of ports
           usb_ports = int(parser.get('usb', 'ports'))
           for port in range(0, usb_ports):
               port = port + 1
               section = "usb" + str(port)
               if parser.has_section(section):
                   self.load_usb_port_config(parser, section)
        except configparser.NoOptionError:
            usb_ports = 0
    
    def load_usb_port_config(self, parser, section):
        try:
            # Get variant
            variant = parser.get(section, 'variant')
            # Try loading its support class
            mod = importlib.import_module(variant)
            factory = getattr(mod, 'instantiate')
            usb_switch = factory()
            # Configure and probe the USB switch
            usb_switch.configure(dict(parser.items(section)))
            usb_switch.probe()
            self.usb_switches.append(usb_switch)
        except configparser.NoOptionError:
            print('usb switch variant not defined!')
        except ImportError:
            print('usb switch "%s" could not be found/loaded!' % (variant))
   
if __name__ == '__main__':
    mtda = MultiTenantDeviceAccess()
    mtda.load_config()
    mtda.target_off()


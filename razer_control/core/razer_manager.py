import logging
from openrazer.client import DeviceManager
from openrazer.client import constants as razer_constants
from razer_control.core.fx import RazerFX

class RazerManager:
    """Manages Razer devices and synchronizes UI effect names with hardware capabilities."""
    
    def __init__(self):
        self.devices = []
        self._cap_map = {
            'breathSingle': 'breath_single',
            'breathRandom': 'breath_random',
            'breathDual':   'breath_dual'
        }
        self.re_scan()

    def get_current_state(self, device_serial=None):
        """Fetch state for a specific device by serial, or the first one if None."""
        target_dev = next((d for d in self.devices if d['fx']._serial == device_serial), None)
        if not target_dev:
            target_dev = self.devices[0] if self.devices else None
        
        if not target_dev: return None
        
        fx = target_dev['fx']
        raw_device = target_dev['raw'] # Zugriff auf das echte Device-Objekt
        try:
            rgb = list(fx.colors)
            return {
                'effect': fx.effect, 
                'r': rgb[0], 'g': rgb[1], 'b': rgb[2],
                'brightness': raw_device.brightness # Helligkeit auslesen
            }
        except Exception:
            return {'effect': 'none', 'r': 0, 'g': 0, 'b': 0, 'brightness': 100}
        
    def re_scan(self):
        """Re-initialize the device list from the hardware daemon."""
        try:
            self._raw_manager = DeviceManager()
            self._raw_manager.sync_effects = False
            
            self.devices = []
            for device in self._raw_manager.devices:
                self.devices.append({
                    'fx': RazerFX(device.serial, device.capabilities),
                    'raw': device, # Speichern für Brightness-Zugriff
                    'name': device.name
                })
            
            logging.info(f"Rescan complete. Found {len(self.devices)} devices.")
        except Exception as e:
            logging.error(f"Failed to rescan Razer devices: {e}")

    def set_brightness(self, value, device_serial=None):
        """Set brightness (0-100) for a specific device or all."""
        for dev in self.devices:
            if device_serial and dev['fx']._serial != device_serial:
                continue
            try:
                dev['raw'].brightness = value
            except Exception as e:
                logging.error(f"Could not set brightness for {dev['name']}: {e}")

    def set_effect(self, name, r=0, g=0, b=0, device_serial=None):
        """Apply effect to a specific device or all if serial is None."""
        for dev in self.devices:
            if device_serial and dev['fx']._serial != device_serial:
                continue
                
            fx = dev['fx']
            cap_name = self._cap_map.get(name, name)
            if not fx.has(cap_name): continue

            if name == 'static': fx.static(r, g, b)
            elif name == 'breathSingle': fx.breath_single(r, g, b)
            elif name == 'breathRandom': fx.breath_random()
            elif name == 'spectrum': fx.spectrum()
            elif name == 'wave': fx.wave(razer_constants.WAVE_RIGHT)
            elif name == 'reactive': fx.reactive(r, g, b, razer_constants.REACTIVE_1000MS)
            elif name == 'none': fx.none()  

    def get_all_supported_effects(self, device_serial=None):
        """Return effects supported by a specific device or all devices."""
        possible = ['static', 'breathSingle', 'breathRandom', 'spectrum', 'wave', 'reactive', 'none']
        supported = set()

        for dev in self.devices:
            if device_serial and dev['fx']._serial != device_serial:
                continue
                
            for eff in possible:
                if dev['fx'].has(self._cap_map.get(eff, eff)):
                    supported.add(eff)
                    
        return sorted(list(supported))
from mididings.live.osc_control import LiveOSC

'''
This class is the equivalent of the mididings.live.livedings.LiveDings class
'''
class FlaskDings(object):
    def __init__(self, options):

        self.osc = LiveOSC(
            self, options["control_port"], options["listen_port"])
        self.osc.start()
        self.osc.query()

        self.current_scene = -1
        self.current_subscene = -1
        self.data_offset = -1
        self.scenes = {}

    def set_data_offset(self, data_offset):
        self.data_offset = data_offset

    def set_scenes(self, value):
        self.scenes = value

    def set_current_scene(self, scene, subscene):
        self.current_scene = scene
        self.current_subscene = subscene

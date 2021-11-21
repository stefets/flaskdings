from mididings.live.osc_control import LiveOSC

import liblo

'''
OSC Server 
'''


class OscServer(LiveOSC):
    def __init__(self, dings, control_port, listen_port):
        super().__init__(dings, control_port, listen_port)

    
    ''' Quit mididings '''
    def quit(self):
        self.send(self.control_port, '/mididings/quit')


    @liblo.make_method('/frontend/refresh', '')
    def refresh(self, path, args):
        self.dings.notify_frontend()


'''
This class is the equivalent of the mididings.live.livedings.LiveDings
'''


class MididingsContext(object):
    def __init__(self, options):

        self.osc = OscServer(
            self, options["control_port"], options["listen_port"])

        self.osc.start()

        self.current_scene = -1
        self.current_subscene = -1
        self.data_offset = -1
        self.scenes = {}
        self.refresh = False

        self.osc.query()

    def notify_frontend(self):
        self.refresh = True

    def next_scene(self):
        self.osc.next_scene()

    def next_subscene(self):
        self.osc.next_subscene()

    def prev_scene(self):
        self.osc.prev_scene()

    def prev_subscene(self):
        self.osc.prev_subscene()

    def panic(self):
        self.osc.panic()

    def quit(self):
        self.osc.quit()

    def switch_scene(self, value):
        self.osc.switch_scene(value)

    def switch_subscene(self, value):
        self.osc.switch_subscene(value)

    '''
    Set by OscServer
    '''

    def set_data_offset(self, data_offset):
        self.data_offset = data_offset

    def set_scenes(self, value):
        self.scenes = value

    def set_current_scene(self, scene, subscene):
        self.current_scene = scene
        self.current_subscene = subscene

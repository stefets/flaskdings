# SPDX-License-Identifier: GPL-2.0-or-later


'''
    This class is the equivalent of the mididings.live.livedings.LiveDings
'''


import liblo
from mididings.live.osc_control import LiveOSC


class OscContext:
    def __init__(self, options):

        self.osc = LiveOSC(
            self, options["control_port"], options["listen_port"])

        self.osc.start()

        self.current_scene = -1
        self.scene_name = ""

        self.current_subscene = -1
        self.subscene_name = ""

        self.has_subscene = False

        self.data_offset = -1
        self.scenes = {}
        
        self.dirty = False
        self.running = False
        self.is_exiting = False

        self.osc.query()

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

    def restart(self):
        self.osc.restart()

    def query(self):
        self.osc.query()

    def quit(self):
        self.osc.quit()
        self.on_exit()

    def switch_scene(self, value):
        self.osc.switch_scene(value)

    def switch_subscene(self, value):
        self.osc.switch_subscene(value)

    ''' OscServer callbacks '''

    def set_data_offset(self, data_offset):
        self.data_offset = data_offset

    def set_scenes(self, value):
        self.scenes = value

    def set_current_scene(self, scene, subscene):
        self.current_scene = scene
        self.current_subscene = subscene

        self.scene_name = self.scenes[scene][0]

        self.has_subscene = self.scenes[scene][1]
        self.subscene_name = self.scenes[scene][1][subscene-1] if self.has_subscene else "..."        

        # This is the last OSC operation.
        self.dirty = True

    def on_start(self):
        self.running = True

    def on_exit(self):
        self.running = False

# SPDX-License-Identifier: GPL-2.0-or-later

import liblo
from mididings.live.osc_control import LiveOSC


class OscServer(LiveOSC):
    def __init__(self, dings, control_port, listen_port):
        super().__init__(dings, control_port, listen_port)


    '''
        Expose OSC paths that are not in LiveOSC
    '''
    def quit(self):
        self.send(self.control_port, '/mididings/quit')

    
    def restart(self):
        self.send(self.control_port, '/mididings/restart')

    
    def query(self):
        self.send(self.control_port, '/mididings/query')


    ''' 
        Future usage or tests 
    '''
    @liblo.make_method('/mididings/running', '')
    def running_cb(self, path, args):
        pass

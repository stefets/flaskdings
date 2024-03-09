#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later

'''
    Main context, driving the scene and osc context
'''


from .osc import OscContext
from .scene import SceneContext


class AppContext:
    def __init__(self, config) -> None:
        self.scene_logic = SceneContext()
        self.osc_logic = OscContext(config, self.scene_logic)

    def is_dirty(self):
        return self.osc_logic.dirty

    def set_dirty(self, value):
        self.osc_logic.dirty = value

    def is_running(self):
        return self.osc_logic.running

    def next_scene(self):
        self.osc_logic.osc.next_scene()

    def next_subscene(self):
        self.osc_logic.osc.next_subscene()

    def prev_scene(self):
        self.osc_logic.osc.prev_scene()

    def prev_subscene(self):
        self.osc_logic.osc.prev_subscene()

    def panic(self):
        self.osc_logic.osc.panic()

    def restart(self):
        self.osc_logic.osc.restart()

    def query(self):
        self.osc_logic.osc.query()

    def quit(self):
        self.osc_logic.osc.quit()

    def switch_scene(self, value):
        self.osc_logic.osc.switch_scene(value)

    def switch_subscene(self, value):
        self.osc_logic.osc.switch_subscene(value)


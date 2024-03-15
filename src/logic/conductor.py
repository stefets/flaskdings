#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later

'''
    Main context, driving the scene and osc context
'''


from .osc import OscContext
from .scene import SceneContext


class ContextManager:
    def __init__(self, config) -> None:
        self.scene_context = SceneContext()
        self.osc_context = OscContext(config, self.scene_context)

    def is_dirty(self):
        return self.osc_context.dirty

    def set_dirty(self, value):
        self.osc_context.dirty = value

    def is_running(self):
        return self.osc_context.running

    def next_scene(self):
        self.osc_context.osc.next_scene()

    def next_subscene(self):
        self.osc_context.osc.next_subscene()

    def prev_scene(self):
        self.osc_context.osc.prev_scene()

    def prev_subscene(self):
        self.osc_context.osc.prev_subscene()

    def panic(self):
        self.osc_context.osc.panic()

    def restart(self):
        self.osc_context.osc.restart()

    def query(self):
        self.osc_context.osc.query()

    def quit(self):
        self.osc_context.osc.quit()

    def switch_scene(self, value):
        self.osc_context.osc.switch_scene(value)

    def switch_subscene(self, value):
        self.osc_context.osc.switch_subscene(value)


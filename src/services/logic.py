#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: GPL-2.0-or-later

'''
    Main service, driving the scene and osc context
'''


from .osc import OscService
from .scene import SceneService


class LogicService:
    def __init__(self, config) -> None:
        self.scene_context = SceneService()
        self.osc_context = OscService(config, self.scene_context)

    def is_dirty(self):
        return self.osc_context.dirty

    def set_dirty(self, value):
        self.osc_context.dirty = value

    def is_running(self):
        return self.osc_context.running

    def next_scene(self):
        self.osc_context.server.next_scene()

    def next_subscene(self):
        self.osc_context.server.next_subscene()

    def prev_scene(self):
        self.osc_context.server.prev_scene()

    def prev_subscene(self):
        self.osc_context.server.prev_subscene()

    def panic(self):
        self.osc_context.server.panic()

    def restart(self):
        self.osc_context.server.restart()

    def query(self):
        self.osc_context.server.query()

    def quit(self):
        self.osc_context.server.quit()

    def switch_scene(self, value):
        self.osc_context.server.switch_scene(value)

    def switch_subscene(self, value):
        self.osc_context.server.switch_subscene(value)


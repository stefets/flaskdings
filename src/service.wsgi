#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
sys.path.insert(0, '/srv/services/dings')

from service import app as application
application.root_path = '/srv/services/dings'


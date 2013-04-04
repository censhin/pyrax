#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2012 Rackspace

# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from functools import wraps

import pyrax
from pyrax.client import BaseClient
import pyrax.exceptions as exc
from pyrax.manager import BaseManager
from pyrax.resource import BaseResource
import pyrax.utils as utils


class CloudMonitoringEntity(BaseResource):
    """
    This class represents a Cloud Monitoring Entity.
    """
    pass


class CloudMonitoringCheck(BaseResource):
    """
    This class represents a Cloud Monitoring Check.
    """
    pass


class CloudMonitoringCheckType(BaseResource):
    """
    This class represents a Cloud Monitoring Check Type.
    """
    pass


class CloudMonitoringClient(BaseClient):
    """
    This is the primary class for interacting with Cloud Monitoring.
    """
    def _configure_manager(self):
        """
        Create the manager to handle instances.
        """
        self._manager = BaseManager(self)
        self._check_manager = BaseManager(self)
        self._check_type_manager = BaseManager(self)


    def create(self):
        pass

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


class CloudMonitoringManager(BaseManager):
    """
    Created to override the methods _list, _get, and
    _create to change body[self.response_key] to body.
    """
    def _list(self, uri, obj_class=None, body=None):
        """
        Handles the communication with the API when gettings
        a full listing of the resources managed by this class.
        """
        if body:
            _resp, body = self.api.method_post(uri, body=body)
        else:
            _resp, body = self.api.method_get(uri)

        if obj_class is None:
            obj_class = self.resource_class

        data = body
        # Note(ja): keystone returns values as list as {"values": [ ... ]}
        #           unlike other services which just return the list...
        if isinstance(data, dict):
            try:
                data = data["values"]
            except KeyError:
                pass
        return [obj_class(self, res, loaded=False)
                for res in data if res]


    def _get(self, uri):
        """
        Handles the communication with the API when getting
        a specific resource managed by this class.
        """
        _resp, body = self.api.method_get(uri)
        return self.resource_class(self, body, loaded=True)


    def _create(self, uri, body, return_none=False, return_raw=False, **kwargs):
        """
        Handles the communication with the API when creating a new
        resource managed by this class.
        """
        self.run_hooks("modify_body_for_create", body, **kwargs)
        _resp, body = self.api.method_post(uri, body=body)
        if return_none:
            # No response body
            return
        if return_raw:
            return body
        return self.resource_class(self, body)


class CloudMonitoringClient(BaseClient):
    """
    This is the primary class for interacting with Cloud Monitoring.
    """
    def _configure_manager(self):
        """
        Create the manager to handle instances.
        """
        self._manager = BaseManager(self,
                resource_class=CloudMonitoringEntity, uri_base="entities")
        self._check_manager = BaseManager(self)
        self._check_type_manager = BaseManager(self)


    def create(self):
        pass

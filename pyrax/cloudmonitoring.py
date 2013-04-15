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
import re

import pyrax
from pyrax.client import BaseClient
import pyrax.exceptions as exc
from pyrax.manager import BaseManager
from pyrax.resource import BaseResource
import pyrax.utils as utils


AGENT_ID_PATTERN = re.compile(r"^[-\.\w]{1,255}$", re.VERBOSE)


class CloudMonitoringEntity(BaseResource):
    """
    This class represents a Cloud Monitoring Entity.
    """
    #TODO finish creating checks for attributes
    def update(self, label=None, ip_addresses=None, metadata=None,
            agent_id=None):
        """
        Provides a way to modify the following attributes of
        an entity if the account is not managed:
            - label
            - ip addresses
            - metadata
            - agent id
        If the account is managed, only the metadata and
        agent id fields can be updated.
        """
        if self.managed is False:
            return self.manager.update_entity(self, label=label,
                    ip_addresses=ip_addresses, metadata=metadata,
                    agent_id=agent_id)
        else:
            return self.manager.update_entity(self, metadata=metadata,
                    agent_id=agent_id)


    def list_checks(self):
        """
        Returns a list of all checks for this entity.
        """
        return [chk for chk in self.manager.list_checks(self)
                if chk.entity_id == self.id]


    def list_alarms(self):
        """
        Returns a list of all alarms for this entity.
        """
        return [alm for alm in self.manager.list_alarms(self)
                if alm.entity_id == self.id]


    #TODO
    def create_check(self):
        """
        Create a check for this entity.
        """
        pass


class CloudMonitoringCheck(BaseResource):
    """
    This class represents a Cloud Monitoring Check.
    """
    pass


class CloudMonitoringCheckType(BaseResource):
    """
    This class represents a type of Cloud Monitoring Check.
    """
    pass


class CloudMonitoringAlarm(BaseResource):
    """
    This class represents a Cloud Monitoring Alarm.
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
        resp_uri = "%s/%s" % (uri, _resp["x-object-id"])
        _resp, body = self.api.method_get(resp_uri)
        if return_none:
            # No response body
            return
        if return_raw:
            return body
        return self.resource_class(self, body)


    #TODO
    def update_entity(self, entity, metadata=None, agent_id=None):
        pass


    def list_checks(self, entity):
        """
        List the checks associated with a given entityId.
        """
        uri = "/entities/%s/checks" % (utils.get_id(entity))
        return self._list(uri)


    def list_alarms(self, entity):
        """
        List the alarms associated with a given entityId.
        """
        uri = "/entities/%s/alarms" % (utils.get_id(entity))
        return self._list(uri)


class CloudMonitoringClient(BaseClient):
    """
    This is the primary class for interacting with Cloud Monitoring.
    """
    def _configure_manager(self):
        """
        Create the manager to handle instances.
        """
        self._manager = CloudMonitoringManager(self,
                resource_class=CloudMonitoringEntity, uri_base="entities")
        self._check_manager = CloudMonitoringManager(self,
                resource_class=CloudMonitoringCheck, uri_base="entities")
        self._alarm_manager = CloudMonitoringManager(self,
                resource_class=CloudMonitoringAlarm, uri_base="entities")
        self._check_type_manager = CloudMonitoringManager(self,
                uri_base="check_types", resource_class=CloudMonitoringCheckType)


    def list_checks(self, entity):
        """
        Returns a list of all checks for a specified entity.
        """
        return self._check_manager.list_checks(entity)


    def list_check_types(self):
        """Returns a list of all available check types."""
        return self._check_type_manager.list()


    def list_alarms(self, entity):
        """
        Returns a list of all alarms for a specified entity.
        """
        return self._alarm_manager.list_alarms(entity)


    def _create_body(self, label, agent_id=None, ip_addresses=None,
            metadata=None):
        """
        Used to create the dict required to create a new entity.
        """
        if not (1 <= len(label) <= 255):
            raise exc.InvalidSize("The label must be between 1 and "
                    "255 characters long.")
        if ip_addresses is None:
            ip_addresses = {}
        elif len(ip_addresses) > 64:
            raise exc.InvalidSize("The number of ip addresses must be "
                    "between 0 and 64.")
        if metadata is None:
            metadata = {}
        elif len(metadata) > 256:
            raise exc.InvalidSize("There can only be a maximum of 256 "
                    "metadata entries.")
        if agent_id is not None:
            if not AGENT_ID_PATTERN.match(agent_id):
                raise exc.InvalidAgentID("The agent ID does not match its "
                        "regular expression pattern.")
            body = {"id": agent_id,
                    "label": label,
                    "ip_addresses": ip_addresses,
                    "metadata": metadata
                    }
        else:
            body = {"label": label,
                    "ip_addresses": ip_addresses,
                    "metadata": metadata
                    }
        return body

    
    def _create_check_body(self, check_type, details=None, disabled=False,
            label=None, metadata=None, period=None, timeout=None, remote=False,
            monitoring_zones_poll=None, target_alias=None, target_hostname=None,
            target_resolver=None):
        """
        Used to create the dict required to create or modify a check.
        """
        if not (1 <= len(check_type) <= 25):
            raise exc.InvalidSize("The type must be between 1 and 25 "
                    "characters long.")
        if details is None:
            details = {}
        elif len(details) > 256:
            raise exc.InvalidSize("There can only be a maximum of 256 "
                    "elements in details.")
        if label is None:
            label = ""
        elif not (1 <= len(label) <= 255):
            raise exc.InvalidSize("The label must be between 1 and "
                    "255 characters long.")
        if metadata is None:
            metadata = {}
        elif len(metadata) > 256:
            raise exc.InvalidSize("There can only be a maximum of 256 "
                    "metadata entries.")
        if not (30 <= len(period) <= 1800):
            raise exc.InvalidRange("The period can only be between 30 "
                    "and 1800 seconds.")
        if not (2 <= len(timeout) <= 1800):
            raise exc.InvalidRange("The timeout can only be between 2 "
                "and 1800 seconds.")
        if monitoring_zones_poll is None:
            monitoring_zones_poll = []
        if remote is True:
            if target_alias is None:
                target_alias = ""
            elif not (1 <= len(target_alias) <= 64):
                raise exc.InvalidSize("Target alias must be between 1 "
                        "and 64 characters long.")
            if target_hostname is None:
                target_hostname = ""
            elif not (1 <= len(target_hostname) <= 256):
                raise exc.InvalidSize("Target hostname must be between "
                        "1 and 256 characters long.")
            if target_resolver is None:
                target_resolver = ""
            body = {"label": label,
                    "type": check_type,
                    "details": details,
                    "monitoring_zones_poll": monitoring_zones_poll,
                    "timeout": timeout,
                    "period": period,
                    "target_alias": target_alias,
                    "target_hostname": target_hostname,
                    "target_resolver": target_resolver
                    }
        else:
            body = {"label": label,
                    "type": check_type,
                    "details": details,
                    "monitoring_zones_poll": monitoring_zones_poll,
                    "timeout": timeout,
                    "period": period,
                    "target_alias": "default"
                    }
        return body


    def _create_alarm_body(self, check_id, notification_plan_id, criteria=None,
            disabled=False, label=None, metadata=None):
        """
        Used to create the dict required to create or modify an alarm.
        """
        if criteria is None:
            criteria = ""
        elif not (1 <= len(criteria) <= 16384):
            raise exc.InvalidSize("The length of criteria must be between "
                    "1 and 16384 characters long.")
        if label is None:
            label = ""
        elif not (1 <= len(label) <= 255):
            raise exc.InvalidSize("The length of label must be between 1 "
                    "and 255 characters long.")
        if metadata is None:
            metadata = {}
        elif len(metadata) > 256:
            raise exc.InvalidSize("There can only be a maximium of 256 "
                    "elements in metadata.")
        body = {"label": label,
                "check_id": check_id,
                "criteria": criteria,
                "notification_plan_id": notification_plan_id,
                "metadata": metadata,
                }
        return body


    def _create_notification_plan_body(self, label, critical_state=None,
            ok_state=None, warning_state=None):
        """
        Used to create the dict required to create a notification
        plan."
        """
        if not (1 <= len(label) <= 255):
            raise exc.InvalidSize("The length of label must be between 1 "
                    "and 255 characters long.")
        if critical_state is None:
            critical_state = []
        if ok_state is None:
            ok_state = []
        if warning_state is None:
            warning_state = []
        body = {"label": label,
                "warning_state": warning_state,
                "ok_state": ok_state,
                "critical_state": critical_state
                }
        return body


    def _create_notification_body(self, details, label, notification_type):
        """
        Used to create the dict required to create a notification.
        """
        if len(details) > 256:
            raise exc.InvalidSize("There can only be a maximum of 256 "
                    "elements in details.")
        if not (1 <= len(label) <= 255):
            raise exc.InvalidSize("The length of label must be between 1 "
                    "and 255 characters long.")
        if "webhook" or "email" not in notification_type:
            raise exc.InvalidNotificationType("The notification type must "
                    "be \"webhook\" or \"email\".")
        body = {"label": label,
                "type": notification_type,
                "details": details
                }
        return body


    def _create_agent_token_body(self, label=None):
        """
        Used to create the dict required to create an agent token.
        """
        if label is None:
            label = ""
        body = {"label": label}
        return body

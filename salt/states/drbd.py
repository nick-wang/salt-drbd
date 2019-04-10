# -*- coding: utf-8 -*-
#
# Author: Nick Wang <nwang@suse.com>
#
# Copyright 2019 SUSE LINUX GmbH, Nuernberg, Germany.
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

'''
:maintainer:    Nick Wang <nwang@suse.com>
:maturity:      alpha
:depends:       None
:platform:      Linux
'''
from __future__ import absolute_import, print_function, unicode_literals
import logging

from salt.exceptions import CommandExecutionError
from salt.ext import six
import os

log = logging.getLogger(__name__)

__virtualname__ = 'drbd'


def _resource_not_exist(name):
    cmd = 'drbdadm dump {}'.format(name)
    result = __salt__['cmd.retcode'](cmd)

    if result != 0:
        return True

    return False


def _get_res_status(name):
    try:
        result = __salt__['drbd.status'](name=name)
    except Exception:
        # TODO: Fix in drbd module
        # Resource not start will raise error.
        return None

    for r in result:
        if r['resource name'] == name:
            log.debug(r)
            return r

    return None


def _get_resource_list():
    ret = []
    cmd = 'drbdadm dump all'

    for line in __salt__['cmd.run'](cmd).splitlines():
        if line.startswith('resource'):
            ret.append(line.split()[1])

    return ret


def initialized(name):
    '''
    Make sure the DRBD resource is initialized.

    name
        Name of the DRBD resource.

    '''

    ret = {
        'name': name,
        'result': False,
        'changes': {},
        'comment': '',
    }

    # Check resource exist
    if _resource_not_exist(name):
        ret['comment'] = 'Resource {} not defined in your config.'.format(name)
        return ret

    # Check already finished
    msg = 'There appears to be a v09| is configured!'
    cmd = 'echo no|drbdadm create-md {} 2>&1 |grep -E "{}" >/dev/null'.format(
        name, msg)
    result = __salt__['cmd.retcode'](cmd, python_shell=True)

    if result == 0:
        ret['result'] = True
        ret['comment'] = 'Resource {} has already initialized.'.format(name)
        return ret

    # Do nothing for test=True
    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Resource {} would be initialized.'.format(name)
        ret['changes']['name'] = name
        return ret

    try:
        # Do real job
        result = __salt__['drbd.createmd'](
            name = name,
            force = True)

        if result:
            ret['changes']['name'] = name
            ret['comment'] = 'Error in initialize {}.'.format(name)
            ret['result'] = False
            return ret

        ret['changes']['name'] = name
        ret['comment'] = 'Resource {} metadata initialized.'.format(name)
        ret['result'] = True
        return ret

    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret


def started(name):
    '''
    Make sure the DRBD resource is started.

    name
        Name of the DRBD resource

    '''

    ret = {
        'name': name,
        'result': False,
        'changes': {},
        'comment': '',
    }

    # Check resource exist
    if _resource_not_exist(name):
        ret['comment'] = 'Resource {} not defined in your config.'.format(name)
        return ret

    res = _get_res_status(name)

    if res:
        ret['result'] = True
        ret['comment'] = 'Resource {} has already started.'.format(name)
        ret['changes']['name'] = name
        return ret


    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Resource {} will be started.'.format(name)
        ret['changes']['name'] = name
        return ret

    return ret













def drbd_stoped(name):
    '''
    Make sure the DRBD resource is stopped.

    name
        Name of the DRBD resource

    '''

    ret = {
        'name': name,
        'result': False,
        'changes': {},
        'comment': '',
    }

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Resource {} is stopped.'.format(name)
        ret['changes']['name'] = name
        return ret

    return ret


def drbd_connected(name, peer):
    '''
    Make sure the DRBD resource is connected to the peer.

    name
        Name of the DRBD resource

    '''

    ret = {
        'name': name,
        'result': False,
        'changes': {},
        'comment': '',
    }

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Resource {} connected to node {}.'.format(
            name, peer)
        ret['changes']['name'] = name
        return ret

    return ret


def drbd_all_connected(name):
    '''
    Make sure the DRBD resource is connected to all peers.

    name
        Name of the DRBD resource

    '''

    ret = {
        'name': name,
        'result': False,
        'changes': {},
        'comment': '',
    }

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Resource {} is connected to all peers:{}.'.format(
            name, "FIXME with peer list")
        ret['changes']['name'] = name
        return ret

    return ret


def drbd_promoted(name):
    '''
    Make sure the DRBD resource is being primary.

    name
        Name of the DRBD resource

    '''

    ret = {
        'name': name,
        'result': False,
        'changes': {},
        'comment': '',
    }

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Resource {} is primary.'.format(name)
        ret['changes']['name'] = name
        return ret

    return ret


def drbd_demoted(name):
    '''
    Make sure the DRBD resource is being secondary.

    name
        Name of the DRBD resource

    '''

    ret = {
        'name': name,
        'result': False,
        'changes': {},
        'comment': '',
    }

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'Resource {} is secondary.'.format(name)
        ret['changes']['name'] = name
        return ret

    return ret


def drbd_uptodated(name):
    ret = {}
    return ret


def drbd_outdated(name):
    ret = {}
    return ret

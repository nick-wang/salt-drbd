# -*- coding: utf-8 -*-
'''
    :codeauthor: Nick Wang <nwang@suse.com>
'''

# Import Python libs
from __future__ import absolute_import, print_function, unicode_literals

from salt import exceptions

# Import Salt Testing Libs
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.unit import TestCase, skipIf
from tests.support.mock import (
    MagicMock,
    patch,
    NO_MOCK,
    NO_MOCK_REASON
)

# Import Salt Libs
import salt.states.drbd as drbd

RES_NAME = 'dummy'


@skipIf(NO_MOCK, NO_MOCK_REASON)
class DrbdStatesTestCase(TestCase, LoaderModuleMockMixin):
    '''
    Test cases for salt.states.drbd
    '''
    def setup_loader_modules(self):
        return {drbd: {'__opts__': {'test': False}}}

    def test_initialized(self):
        '''
        Test to check drbd resource is initialized.
        '''
        # SubTest 1: Resource not exist
        ret = {
            'name': RES_NAME,
            'result': False,
            'changes': {},
            'comment': 'Resource {} not defined in your config.'.format(RES_NAME),
        }

        mock = MagicMock(return_value=1)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            self.assertDictEqual(drbd.initialized(RES_NAME), ret)
            mock.assert_called_once_with('drbdadm dump {}'.format(RES_NAME))

        # SubTest 2: Resource have already initialized
        ret = {
            'name': RES_NAME,
            'result': True,
            'changes': {},
            'comment': 'Resource {} has already initialized.'.format(RES_NAME),
        }

        mock = MagicMock(side_effect=[0, 0])

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            self.assertDictEqual(drbd.initialized(RES_NAME), ret)

        # SubTest 3: The test option
        ret = {
            'name': RES_NAME,
            'result': None,
            'changes': {'name': RES_NAME},
            'comment': 'Resource {} would be initialized.'.format(RES_NAME),
        }

        mock = MagicMock(side_effect=[0, 1])

        with patch.dict(drbd.__opts__, {'test': True}):
            with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
                self.assertDictEqual(drbd.initialized(RES_NAME), ret)

        # SubTest 4: Error in initialize
        ret = {
            'name': RES_NAME,
            'result': False,
            'changes': {},
            'comment': 'Error in initialize {}.'.format(RES_NAME),
        }

        mock = MagicMock(side_effect=[0, 1])
        mock_createmd = MagicMock(return_value=1)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.createmd': mock_createmd}):
                self.assertDictEqual(drbd.initialized(RES_NAME, force=True), ret)

        # SubTest 5: Succeed in initialize
        ret = {
            'name': RES_NAME,
            'result': True,
            'changes': {'name': RES_NAME},
            'comment': 'Resource {} metadata initialized.'.format(RES_NAME),
        }

        mock = MagicMock(side_effect=[0, 1])
        mock_createmd = MagicMock(return_value=0)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.createmd': mock_createmd}):
                self.assertDictEqual(drbd.initialized(RES_NAME, force=True), ret)

        # SubTest 6: Command error
        ret = {
            'name': RES_NAME,
            'result': False,
            'changes': {},
            'comment': 'drdbadm createmd error.',
        }

        mock = MagicMock(side_effect=[0, 1])
        mock_createmd = MagicMock(side_effect=exceptions.CommandExecutionError(
            'drdbadm createmd error.'))

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.createmd': mock_createmd}):
                self.assertDictEqual(drbd.initialized(RES_NAME, force=True), ret)

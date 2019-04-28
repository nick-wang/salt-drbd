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
                mock_createmd.assert_called_once_with(force=True, name=RES_NAME)

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
                mock_createmd.assert_called_once_with(force=True, name=RES_NAME)

        # SubTest 6: Command error
        ret = {
            'name': RES_NAME,
            'result': False,
            'changes': {},
            'comment': 'drdbadm createmd {} error.'.format(RES_NAME),
        }

        mock = MagicMock(side_effect=[0, 1])
        mock_createmd = MagicMock(side_effect=exceptions.CommandExecutionError(
            'drdbadm createmd {} error.'.format(RES_NAME)))

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.createmd': mock_createmd}):
                self.assertDictEqual(drbd.initialized(RES_NAME, force=True), ret)
                mock_createmd.assert_called_once_with(force=True, name=RES_NAME)

    def test_status(self):
        '''
        Test drbd status(_get_res_status) return none.
        '''
        # Test 1: drbd status raise Exception
        ret = {
            'name': RES_NAME,
            'result': True,
            'changes': {},
            'comment': 'Resource {} has already stopped.'.format(RES_NAME),
        }

        mock = MagicMock(return_value=0)
        mock_status = MagicMock(side_effect=Exception)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                self.assertDictEqual(drbd.stopped(RES_NAME), ret)

        # Test 2: drbd status return empty []
        ret = {
            'name': RES_NAME,
            'result': True,
            'changes': {},
            'comment': 'Resource {} has already stopped.'.format(RES_NAME),
        }

        mock = MagicMock(return_value=0)
        mock_status = MagicMock(return_value=[{'resource name': 'not_the_same'}])

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                self.assertDictEqual(drbd.stopped(RES_NAME), ret)


    def test_started(self):
        '''
        Test to check drbd resource is started.
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
            self.assertDictEqual(drbd.started(RES_NAME), ret)
            mock.assert_called_once_with('drbdadm dump {}'.format(RES_NAME))

        # SubTest 2: Resource have already started
        ret = {
            'name': RES_NAME,
            'result': True,
            'changes': {},
            'comment': 'Resource {} has already started.'.format(RES_NAME),
        }

        # A full resource example
        # res_status = [{'resource name': RES_NAME,
        #                'local role': 'Primary',
        #                'local volumes': [{'disk': 'UpToDate'}],
        #                'peer nodes': [{'peernode name': 'salt-node3',
        #                                'role': 'Secondary',
        #                                'peer volumes': [{'peer-disk': 'UpToDate'}]
        #                               }
        #                              ]
        #               }
        #              ]
        res_status = [{'resource name': RES_NAME}]

        mock = MagicMock(return_value=0)
        mock_status = MagicMock(return_value=res_status)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                self.assertDictEqual(drbd.started(RES_NAME), ret)

        # SubTest 3: The test option
        ret = {
            'name': RES_NAME,
            'result': None,
            'changes': {'name': RES_NAME},
            'comment': 'Resource {} would be started.'.format(RES_NAME),
        }

        res_status = None

        mock = MagicMock(return_value=0)
        mock_status = MagicMock(return_value=res_status)

        with patch.dict(drbd.__opts__, {'test': True}):
            with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
                with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                    self.assertDictEqual(drbd.started(RES_NAME), ret)

        # SubTest 4: Error in start
        ret = {
            'name': RES_NAME,
            'result': False,
            'changes': {},
            'comment': 'Error in start {}.'.format(RES_NAME),
        }

        res_status = None

        mock = MagicMock(side_effect=[0, 1])
        mock_status = MagicMock(return_value=res_status)
        mock_up = MagicMock(return_value=1)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                with patch.dict(drbd.__salt__, {'drbd.up': mock_up}):
                    self.assertDictEqual(drbd.started(RES_NAME), ret)
                    mock_up.assert_called_once_with(name=RES_NAME)

        # SubTest 5: Succeed in start
        ret = {
            'name': RES_NAME,
            'result': True,
            'changes': {'name': RES_NAME},
            'comment': 'Resource {} is started.'.format(RES_NAME),
        }

        res_status = None

        mock = MagicMock(side_effect=[0, 1])
        mock_status = MagicMock(return_value=res_status)
        mock_up = MagicMock(return_value=0)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                with patch.dict(drbd.__salt__, {'drbd.up': mock_up}):
                    self.assertDictEqual(drbd.started(RES_NAME), ret)
                    mock_up.assert_called_once_with(name=RES_NAME)

        # SubTest 6: Command error
        ret = {
            'name': RES_NAME,
            'result': False,
            'changes': {},
            'comment': 'drdbadm up {} error.'.format(RES_NAME),
        }

        res_status = None

        mock = MagicMock(side_effect=[0, 1])
        mock_status = MagicMock(return_value=res_status)
        mock_up = MagicMock(side_effect=exceptions.CommandExecutionError(
            'drdbadm up {} error.'.format(RES_NAME)))

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                with patch.dict(drbd.__salt__, {'drbd.up': mock_up}):
                    self.assertDictEqual(drbd.started(RES_NAME), ret)
                    mock_up.assert_called_once_with(name=RES_NAME)

    def test_stopped(self):
        '''
        Test to check drbd resource is stopped.
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
            self.assertDictEqual(drbd.stopped(RES_NAME), ret)
            mock.assert_called_once_with('drbdadm dump {}'.format(RES_NAME))

        # SubTest 2: Resource have already stopped
        ret = {
            'name': RES_NAME,
            'result': True,
            'changes': {},
            'comment': 'Resource {} has already stopped.'.format(RES_NAME),
        }

        # A full resource example
        # res_status = [{'resource name': RES_NAME,
        #                'local role': 'Primary',
        #                'local volumes': [{'disk': 'UpToDate'}],
        #                'peer nodes': [{'peernode name': 'salt-node3',
        #                                'role': 'Secondary',
        #                                'peer volumes': [{'peer-disk': 'UpToDate'}]
        #                               }
        #                              ]
        #               }
        #              ]
        res_status = None

        mock = MagicMock(return_value=0)
        mock_status = MagicMock(return_value=res_status)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                self.assertDictEqual(drbd.stopped(RES_NAME), ret)

        # SubTest 3: The test option
        ret = {
            'name': RES_NAME,
            'result': None,
            'changes': {'name': RES_NAME},
            'comment': 'Resource {} would be stopped.'.format(RES_NAME),
        }

        res_status = [{'resource name': RES_NAME}]

        mock = MagicMock(return_value=0)
        mock_status = MagicMock(return_value=res_status)

        with patch.dict(drbd.__opts__, {'test': True}):
            with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
                with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                    self.assertDictEqual(drbd.stopped(RES_NAME), ret)

        # SubTest 4: Error in stop
        ret = {
            'name': RES_NAME,
            'result': False,
            'changes': {},
            'comment': 'Error in stop {}.'.format(RES_NAME),
        }

        res_status = [{'resource name': RES_NAME}]

        mock = MagicMock(side_effect=[0, 1])
        mock_status = MagicMock(return_value=res_status)
        mock_down = MagicMock(return_value=1)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                with patch.dict(drbd.__salt__, {'drbd.down': mock_down}):
                    self.assertDictEqual(drbd.stopped(RES_NAME), ret)
                    mock_down.assert_called_once_with(name=RES_NAME)

        # SubTest 5: Succeed in stop
        ret = {
            'name': RES_NAME,
            'result': True,
            'changes': {'name': RES_NAME},
            'comment': 'Resource {} is stopped.'.format(RES_NAME),
        }

        res_status = [{'resource name': RES_NAME}]

        mock = MagicMock(side_effect=[0, 1])
        mock_status = MagicMock(return_value=res_status)
        mock_down = MagicMock(return_value=0)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                with patch.dict(drbd.__salt__, {'drbd.down': mock_down}):
                    self.assertDictEqual(drbd.stopped(RES_NAME), ret)
                    mock_down.assert_called_once_with(name=RES_NAME)

        # SubTest 6: Command error
        ret = {
            'name': RES_NAME,
            'result': False,
            'changes': {},
            'comment': 'drdbadm down {} error.'.format(RES_NAME),
        }

        res_status = [{'resource name': RES_NAME}]

        mock = MagicMock(side_effect=[0, 1])
        mock_status = MagicMock(return_value=res_status)
        mock_down = MagicMock(side_effect=exceptions.CommandExecutionError(
            'drdbadm down {} error.'.format(RES_NAME)))

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                with patch.dict(drbd.__salt__, {'drbd.down': mock_down}):
                    self.assertDictEqual(drbd.stopped(RES_NAME), ret)
                    mock_down.assert_called_once_with(name=RES_NAME)

    def test_promoted(self):
        '''
        Test to check drbd resource is promoted.
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
            self.assertDictEqual(drbd.promoted(RES_NAME), ret)
            mock.assert_called_once_with('drbdadm dump {}'.format(RES_NAME))

        # SubTest 2.1: Resource have already promoted
        ret = {
            'name': RES_NAME,
            'result': True,
            'changes': {},
            'comment': 'Resource {} has already been promoted.'.format(RES_NAME),
        }

        # A full resource example
        # res_status = [{'resource name': RES_NAME,
        #                'local role': 'Primary',
        #                'local volumes': [{'disk': 'UpToDate'}],
        #                'peer nodes': [{'peernode name': 'salt-node3',
        #                                'role': 'Secondary',
        #                                'peer volumes': [{'peer-disk': 'UpToDate'}]
        #                               }
        #                              ]
        #               }
        #              ]
        res_status = [{'resource name': RES_NAME, 'local role': 'Primary'}]

        mock = MagicMock(return_value=0)
        mock_status = MagicMock(return_value=res_status)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                self.assertDictEqual(drbd.promoted(RES_NAME), ret)

        # SubTest 2.2: Resource is stopped
        ret = {
            'name': RES_NAME,
            'result': False,
            'changes': {},
            'comment': 'Resource {} is currently stop.'.format(RES_NAME),
        }

        # A full resource example
        # res_status = [{'resource name': RES_NAME,
        #                'local role': 'Primary',
        #                'local volumes': [{'disk': 'UpToDate'}],
        #                'peer nodes': [{'peernode name': 'salt-node3',
        #                                'role': 'Secondary',
        #                                'peer volumes': [{'peer-disk': 'UpToDate'}]
        #                               }
        #                              ]
        #               }
        #              ]
        res_status = None

        mock = MagicMock(return_value=0)
        mock_status = MagicMock(return_value=res_status)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                self.assertDictEqual(drbd.promoted(RES_NAME), ret)

        # SubTest 3: The test option
        ret = {
            'name': RES_NAME,
            'result': None,
            'changes': {'name': RES_NAME},
            'comment': 'Resource {} would be promoted.'.format(RES_NAME),
        }

        res_status = [{'resource name': RES_NAME, 'local role': 'Secondary'}]

        mock = MagicMock(return_value=0)
        mock_status = MagicMock(return_value=res_status)

        with patch.dict(drbd.__opts__, {'test': True}):
            with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
                with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                    self.assertDictEqual(drbd.promoted(RES_NAME), ret)

        # SubTest 4: Error in promotion
        ret = {
            'name': RES_NAME,
            'result': False,
            'changes': {},
            'comment': 'Error in promoting {}.'.format(RES_NAME),
        }

        res_status = [{'resource name': RES_NAME, 'local role': 'Secondary'}]

        mock = MagicMock(side_effect=[0, 1])
        mock_status = MagicMock(return_value=res_status)
        mock_primary = MagicMock(return_value=1)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                with patch.dict(drbd.__salt__, {'drbd.primary': mock_primary}):
                    self.assertDictEqual(drbd.promoted(RES_NAME), ret)
                    mock_primary.assert_called_once_with(force=False, name=RES_NAME)

        # SubTest 5: Succeed in promotion
        ret = {
            'name': RES_NAME,
            'result': True,
            'changes': {'name': RES_NAME},
            'comment': 'Resource {} is promoted.'.format(RES_NAME),
        }

        res_status = [{'resource name': RES_NAME, 'local role': 'Secondary'}]

        mock = MagicMock(side_effect=[0, 1])
        mock_status = MagicMock(return_value=res_status)
        mock_primary = MagicMock(return_value=0)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                with patch.dict(drbd.__salt__, {'drbd.primary': mock_primary}):
                    self.assertDictEqual(drbd.promoted(RES_NAME), ret)
                    mock_primary.assert_called_once_with(force=False, name=RES_NAME)

        # SubTest 6: Command error
        ret = {
            'name': RES_NAME,
            'result': False,
            'changes': {},
            'comment': 'drdbadm primary {} error.'.format(RES_NAME),
        }

        res_status = [{'resource name': RES_NAME, 'local role': 'Secondary'}]

        mock = MagicMock(side_effect=[0, 1])
        mock_status = MagicMock(return_value=res_status)
        mock_primary = MagicMock(side_effect=exceptions.CommandExecutionError(
            'drdbadm primary {} error.'.format(RES_NAME)))

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                with patch.dict(drbd.__salt__, {'drbd.primary': mock_primary}):
                    self.assertDictEqual(drbd.promoted(RES_NAME), ret)
                    mock_primary.assert_called_once_with(force=False, name=RES_NAME)

    def test_demoted(self):
        '''
        Test to check drbd resource is demoted.
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
            self.assertDictEqual(drbd.demoted(RES_NAME), ret)
            mock.assert_called_once_with('drbdadm dump {}'.format(RES_NAME))

        # SubTest 2.1: Resource have already demoted
        ret = {
            'name': RES_NAME,
            'result': True,
            'changes': {},
            'comment': 'Resource {} has already been demoted.'.format(RES_NAME),
        }

        # A full resource example
        # res_status = [{'resource name': RES_NAME,
        #                'local role': 'Primary',
        #                'local volumes': [{'disk': 'UpToDate'}],
        #                'peer nodes': [{'peernode name': 'salt-node3',
        #                                'role': 'Secondary',
        #                                'peer volumes': [{'peer-disk': 'UpToDate'}]
        #                               }
        #                              ]
        #               }
        #              ]
        res_status = [{'resource name': RES_NAME, 'local role': 'Secondary'}]

        mock = MagicMock(return_value=0)
        mock_status = MagicMock(return_value=res_status)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                self.assertDictEqual(drbd.demoted(RES_NAME), ret)

        # SubTest 2.2: Resource is stopped
        ret = {
            'name': RES_NAME,
            'result': False,
            'changes': {},
            'comment': 'Resource {} is currently stop.'.format(RES_NAME),
        }

        # A full resource example
        # res_status = [{'resource name': RES_NAME,
        #                'local role': 'Primary',
        #                'local volumes': [{'disk': 'UpToDate'}],
        #                'peer nodes': [{'peernode name': 'salt-node3',
        #                                'role': 'Secondary',
        #                                'peer volumes': [{'peer-disk': 'UpToDate'}]
        #                               }
        #                              ]
        #               }
        #              ]
        res_status = None

        mock = MagicMock(return_value=0)
        mock_status = MagicMock(return_value=res_status)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                self.assertDictEqual(drbd.demoted(RES_NAME), ret)

        # SubTest 3: The test option
        ret = {
            'name': RES_NAME,
            'result': None,
            'changes': {'name': RES_NAME},
            'comment': 'Resource {} would be demoted.'.format(RES_NAME),
        }

        res_status = [{'resource name': RES_NAME, 'local role': 'Primary'}]

        mock = MagicMock(return_value=0)
        mock_status = MagicMock(return_value=res_status)

        with patch.dict(drbd.__opts__, {'test': True}):
            with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
                with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                    self.assertDictEqual(drbd.demoted(RES_NAME), ret)

        # SubTest 4: Error in demotion
        ret = {
            'name': RES_NAME,
            'result': False,
            'changes': {},
            'comment': 'Error in demoting {}.'.format(RES_NAME),
        }

        res_status = [{'resource name': RES_NAME, 'local role': 'Primary'}]

        mock = MagicMock(side_effect=[0, 1])
        mock_status = MagicMock(return_value=res_status)
        mock_secondary = MagicMock(return_value=1)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                with patch.dict(drbd.__salt__, {'drbd.secondary': mock_secondary}):
                    self.assertDictEqual(drbd.demoted(RES_NAME), ret)
                    mock_secondary.assert_called_once_with(name=RES_NAME)

        # SubTest 5: Succeed in demotion
        ret = {
            'name': RES_NAME,
            'result': True,
            'changes': {'name': RES_NAME},
            'comment': 'Resource {} is demoted.'.format(RES_NAME),
        }

        res_status = [{'resource name': RES_NAME, 'local role': 'Primary'}]

        mock = MagicMock(side_effect=[0, 1])
        mock_status = MagicMock(return_value=res_status)
        mock_secondary = MagicMock(return_value=0)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                with patch.dict(drbd.__salt__, {'drbd.secondary': mock_secondary}):
                    self.assertDictEqual(drbd.demoted(RES_NAME), ret)
                    mock_secondary.assert_called_once_with(name=RES_NAME)

        # SubTest 6: Command error
        ret = {
            'name': RES_NAME,
            'result': False,
            'changes': {},
            'comment': 'drdbadm secondary {} error.'.format(RES_NAME),
        }

        res_status = [{'resource name': RES_NAME, 'local role': 'Primary'}]

        mock = MagicMock(side_effect=[0, 1])
        mock_status = MagicMock(return_value=res_status)
        mock_secondary = MagicMock(side_effect=exceptions.CommandExecutionError(
            'drdbadm secondary {} error.'.format(RES_NAME)))

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                with patch.dict(drbd.__salt__, {'drbd.secondary': mock_secondary}):
                    self.assertDictEqual(drbd.demoted(RES_NAME), ret)
                    mock_secondary.assert_called_once_with(name=RES_NAME)

    def test_wait_for_successful_synced(self):
        '''
        Test to check all volumes of a drbd resource is fully synced.
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
            self.assertDictEqual(drbd.wait_for_successful_synced(RES_NAME), ret)
            mock.assert_called_once_with('drbdadm dump {}'.format(RES_NAME))

        # SubTest 2.1: Resource have already been synced
        ret = {
            'name': RES_NAME,
            'result': True,
            'changes': {},
            'comment': 'Resource {} has already been synced.'.format(RES_NAME),
        }

        # A full resource example
        # res_status = [{'resource name': RES_NAME,
        #                'local role': 'Primary',
        #                'local volumes': [{'disk': 'UpToDate'}],
        #               'peer nodes': [{'peernode name': 'salt-node3',
        #                                'role': 'Secondary',
        #                                'peer volumes': [{'peer-disk': 'UpToDate'}]
        #                               }
        #                              ]
        #               }
        #              ]
        res_status = [{'resource name': RES_NAME}]

        mock = MagicMock(return_value=0)
        mock_status = MagicMock(return_value=res_status)
        mock_sync_status = MagicMock(return_value=1)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                with patch.dict(drbd.__salt__, {'drbd.check_sync_status': mock_sync_status}):
                    self.assertDictEqual(drbd.wait_for_successful_synced(RES_NAME), ret)

        # SubTest 2.2: Resource is stopped
        ret = {
            'name': RES_NAME,
            'result': False,
            'changes': {},
            'comment': 'Resource {} is currently stop.'.format(RES_NAME),
        }

        # A full resource example
        # res_status = [{'resource name': RES_NAME,
        #                'local role': 'Primary',
        #                'local volumes': [{'disk': 'UpToDate'}],
        #                'peer nodes': [{'peernode name': 'salt-node3',
        #                                'role': 'Secondary',
        #                                'peer volumes': [{'peer-disk': 'UpToDate'}]
        #                               }
        #                              ]
        #               }
        #              ]
        res_status = None

        mock = MagicMock(return_value=0)
        mock_status = MagicMock(return_value=res_status)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                self.assertDictEqual(drbd.wait_for_successful_synced(RES_NAME), ret)

        # SubTest 3: The test option
        ret = {
            'name': RES_NAME,
            'result': None,
            'changes': {'name': RES_NAME},
            'comment': 'Check {} whether be synced within {}.'.format(RES_NAME, 600),
        }

        # Fake res is enough, since mock drbd.check_sync_status
        res_status = [{'resource name': RES_NAME}]

        mock = MagicMock(return_value=0)
        mock_status = MagicMock(return_value=res_status)
        mock_sync_status = MagicMock(return_value=0)

        with patch.dict(drbd.__opts__, {'test': True}):
            with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
                with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                    with patch.dict(drbd.__salt__, {'drbd.check_sync_status': mock_sync_status}):
                        self.assertDictEqual(drbd.wait_for_successful_synced(RES_NAME), ret)
                        mock_sync_status.assert_called_once_with(name=RES_NAME)

        # SubTest 4: Not finish sync in time
        ret = {
            'name': RES_NAME,
            'result': False,
            'changes': {},
            'comment': 'Resource {} is not synced within {}s.'.format(RES_NAME, 1),
        }

        res_status = [{'resource name': RES_NAME}]

        mock = MagicMock(side_effect=[0, 1])
        mock_status = MagicMock(return_value=res_status)
        mock_sync_status = MagicMock(return_value=0)

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                with patch.dict(drbd.__salt__, {'drbd.check_sync_status': mock_sync_status}):
                    self.assertDictEqual(drbd.wait_for_successful_synced(
                                         RES_NAME, interval=0.3, timeout=1), ret)
                    # Should call 5 times, when timeout is 1, interval is 0.3
                    mock_sync_status.assert_called_with(name=RES_NAME)

        # SubTest 5: Succeed in syncing in time
        ret = {
            'name': RES_NAME,
            'result': True,
            'changes': {'name': RES_NAME},
            'comment': 'Resource {} is synced.'.format(RES_NAME),
        }

        res_status = [{'resource name': RES_NAME}]

        mock = MagicMock(side_effect=[0, 1])
        mock_status = MagicMock(return_value=res_status)
        mock_sync_status = MagicMock(side_effect=[0, 0, 0, 1])

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                with patch.dict(drbd.__salt__, {'drbd.check_sync_status': mock_sync_status}):
                    self.assertDictEqual(drbd.wait_for_successful_synced(
                                         RES_NAME, interval=0.3, timeout=1), ret)
                    mock_sync_status.assert_called_with(name=RES_NAME)

        # SubTest 6: Command error
        ret = {
            'name': RES_NAME,
            'result': False,
            'changes': {},
            'comment': 'drbd.check_sync_status: (drdbadm status {}) error.'.format(
                       RES_NAME),
        }

        res_status = [{'resource name': RES_NAME}]

        mock = MagicMock(side_effect=[0, 1])
        mock_status = MagicMock(return_value=res_status)
        mock_sync_status = MagicMock(side_effect=[0, 0, 0, exceptions.CommandExecutionError(
            'drbd.check_sync_status: (drdbadm status {}) error.'.format(RES_NAME))])

        with patch.dict(drbd.__salt__, {'cmd.retcode': mock}):
            with patch.dict(drbd.__salt__, {'drbd.status': mock_status}):
                with patch.dict(drbd.__salt__, {'drbd.check_sync_status': mock_sync_status}):
                    self.assertDictEqual(drbd.wait_for_successful_synced(RES_NAME, interval=0.3, timeout=1), ret)
                    mock_sync_status.assert_called_with(name=RES_NAME)

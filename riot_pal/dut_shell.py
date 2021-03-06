# Copyright (c) 2018 Kevin Weiss, for HAW Hamburg  <kevin.weiss@haw-hamburg.de>
#
# This file is subject to the terms and conditions of the MIT License. See the
# file LICENSE in the top level directory for more details.
# SPDX-License-Identifier:    MIT
"""Device Under Tests Shell for RIOT PAL
This module handles parsing of information from RIOT shell base tests.
"""
import logging
from .base_device import BaseDevice


class DutShell(BaseDevice):
    """Parses commands and resposes from the shell."""
    COMMAND = 'Command: '
    SUCCESS = 'Success: '
    ERROR = 'Error: '
    TIMEOUT = 'Timeout: '
    RESULT_SUCCESS = 'Success'
    RESULT_ERROR = 'Error'
    RESULT_TIMEOUT = 'Timeout'

    @staticmethod
    def _try_parse_data(data):
        if ('[' in data) and (']' in data):
            parsed_data = []
            data = data[data.find("[")+1:data.find("]")]
            data_list = data.split(', ')
            for value in data_list:
                try:
                    parsed_data.append(int(value, 0))
                except ValueError:
                    parsed_data.append(value)
            logging.debug(parsed_data)
            return parsed_data
        return None

    def send_cmd(self, send_cmd):
        """Returns a dictionary with information from the event.

        Returns:
            dict:
            The return hold dict values in the following keys::
                msg - The message from the response, only used for information.
                cmd - The command sent, used to track what has occured.
                data - Parsed information of the data requested.
                result - Either success, error or timeout.
        """
        self._write(send_cmd)
        response = self._readline()
        cmd_info = {'cmd': send_cmd, 'data': None}
        while response != '':
            if self.COMMAND in response:
                cmd_info['msg'] = response.replace(self.COMMAND, '')
                cmd_info['cmd'] = cmd_info['msg'].replace('\n', '')

            if self.SUCCESS in response:
                clean_msg = response.replace(self.SUCCESS, '')
                cmd_info['msg'] = clean_msg.replace('\n', '')
                cmd_info['result'] = self.RESULT_SUCCESS
                cmd_info['data'] = self._try_parse_data(cmd_info['msg'])
                break

            if self.ERROR in response:
                clean_msg = response.replace(self.ERROR, '')
                cmd_info['msg'] = clean_msg.replace('\n', '')
                cmd_info['result'] = self.RESULT_ERROR
                break
            response = self._readline()

        if response == '':
            cmd_info['result'] = self.RESULT_TIMEOUT
            logging.debug(self.RESULT_TIMEOUT)
        return cmd_info

#!/opt/python-2.7.13/bin/python -u

from netmiko.base_connection import BaseConnection
from ParseHelpers import parse_info
import re
import socket

class RouterConnection:
    """
    This class is written on top of the Netmiko library, and provides several commands that I thought would be useful
    for smoother usage and better applicability to the network health check script.
    """

    # CONSTANTS
    # used for log in to all devices
    __USERNAME = 'network-team'
    __PASSWORD = 'Iltw@S2017'

    # maximum number of attempts at sending command
    __MAX_TRIES = 3

    # maximum waiting time for execute, ~5 minutes
    __LONG_MAX_LOOPS = 1600

    # maximum waiting time for execute_short, ~10 seconds
    __SHORT_MAX_LOOPS = 50


    ### CONSTRUCTOR
    def __init__(self, device_type, device_alias, need_src=True):
        """
        :type device_type: string
        :type device_alias: string
        :type need_src: boolean
        :rtype: void

        CONSTRUCTOR:
        Establishes a SSH connection for the given device_type and device_alias. Device_type can either be 'cisco_ios' or
        'cisco_xe', which are used for mpls / vpn routers and core switches respectively. The device_alias is just the name / ip
        of the device. 

        need_src is an optional boolean value that represents whether or not the connection needs to find its source IP. Some commands will not
        need to have this information, and specifying need_src=False will avoid sending unneeded commands.

        EXAMPLE USAGE:
        connect = RouterConnection('cisco_ios', 'netlab-vpn-router')
        """

        try:
            # creates a dictionary to store the information for the device  
            self.__connect = BaseConnection(device_type=device_type, ip=device_alias, username=self.__USERNAME, password=self.__PASSWORD)
            # assuming cisco device, used so that no data is truncated
            self.__connect.send_command('term length 0')

            self.__type = device_type
            self.__prompt = self.__connect.find_prompt()
            self.__alias = device_alias.lower()
            if (need_src and 'vpn' in self.__alias):
                self.__initialize_source()
            else:
                self.__source = None
        except:
            self.__connect = None
            self.__prompt = None
            self.__source = None
            self.__alias = None
            self.__type = None        


    ### PUBLIC METHODS ###
    def is_connected(self):
        """
        :rtype: boolean

        PUBLIC METHOD:
        Used to see whether or not the connection was successful. Returns a boolean.

        EXAMPLE USAGE:
        is_connected = connect.is_connected()
        """
        return self.__connect != None


    def get_name(self):
        """
        :rtype: string

        PUBLIC METHOD:
        Used to get the name of the device. This is the "formal" name of the device, not to be confused with the alias
        of the device (ie. alias: 'us11-core-switch', name: 'us11-c3560x-1'). Returns a string if connected, None otherwise.

        EXAMPLE USAGE:
        name = connect.get_name()
        """      
        if not self.is_connected():
            return None

        # get rid of # at the end
        return self.__prompt[:-1].lower()


    def get_alias(self):
        """
        :rtype: string

        PUBLIC METHOD:
        Used to get the alias of the device. This is the "informal" name of the device, not to be confused with the actual name
        of the device (ie. alias: 'us11-core-switch', name: 'us11-c3560x-1'). Returns a string if connected, None otherwise.

        EXAMPLE USAGE:
        alias = connect.get_alias()
        """
        if not self.is_connected():
            return None

        return self.__alias


    def execute(self, command, expect_string=None):
        """
        :type command: string
        :type expect_string: string
        :rtype: string

        PUBLIC METHOD:
        Used to get the output of a long command (ie. 'trace 198.182.41.251'). Sends the command up to MAX_TRIEs times, and limits the waiting time to about 5 minutes
        for each try. By default, this command expects to see the prompt of the router before returning the output. If the command does not re-display the prompt upon completion, 
        then expect_string should be specified, or else this command will hang for the maximum waiting time before returning None. Returns a string if success,
        None object otherwise.

        EXAMPLE USAGE:
        output = connect.execute('trace 198.182.41.251')
        """
        # around 5 minutes
        return self.__execute_loop(command, expect_string, self.__LONG_MAX_LOOPS)


    def execute_short(self, command, expect_string=None):
        """
        :type command: string
        :type expect_string: string
        :rtype: string

        PUBLIC METHOD:
        Used to get the output of a short command (ie. 'show'). Sends the command up to MAX_TRIEs times, and limits the waiting time to about 10 seconds. By default, this command 
        expects to see the prompt of the router before returning the output. If the command does not re-display the prompt upon completion, then expect_string
        should be specified, or else this command will hang for the maximum waiting time before returning None. Returns a string if success,
        None object otherwise.

        Note: The only difference between execute and execute_short is the length of the maximum wait time.

        EXAMPLE USAGE:
        output = connect.execute_short('show interface')
        output = connect.execute_short('trace', expect_string=":")
        """
        # around 10 seconds
        return self.__execute_loop(command, expect_string, self.__SHORT_MAX_LOOPS)


    def get_source(self):
        """
        :rtype: string

        PUBLIC METHOD:
        Used to get the source of the device. Returns a string if connected, None object otherwise.

        EXAMPLE USAGE:
        source = connect.get_source()
        """
        if not self.is_connected():
            return None

        return self.__source


    def get_prompt(self):
        """
        :rtype: string

        PUBLIC METHOD:
        Used to get the prompt of the SSH connection. Returns a string if connected, None object otherwise.

        EXAMPLE USAGE:
        prompt = connect.get_prompt()
        """
        if not self.is_connected():
            return None

        return self.__prompt


    def disconnect(self):
        """
        :rtype: void

        PUBLIC METHOD:
        Properly disconnects from the SSH session. No return value.

        EXAMPLE USAGE:
        connect.disconnect()
        """
        if self.is_connected():
            self.__connect.disconnect()
            self.__connect = None


    ### PRIVATE METHODS ###
    def __initialize_source(self):
        """
        :rtype: void

        PRIVATE METHOD:
        Used to set the source of the device. If successful, self.__source will be set to a string value. Else,
        it will remain a None object. This function does not have a return value.

        EXAMPLE USAGE:
        self.__initialize_source()
        """
        if not self.is_connected():
            self.__source = None
            return

        output = self.execute('sh run int tu 1000 | in source')

        if output != None and 'source' in output:
            self.__source = parse_info(r'source (\S+)', output, 1)[0]
        else:
            self.__source = None


    def __execute_loop(self, command, expect_string, max_loops):
        """
        :type command: string
        :type expect_string: string
        :type max_loops: int
        :rtype: string

        PRIVATE METHOD:
        Helper method used in execute and execute_short. Loops MAX_TRIES times to attempt to get the output. If 
        the output is not properly obtained after the maximum number of tries, returns None object. Else, returns a string output.

        EXAMPLE USAGE:
        output = self.__execute_loop('trace 198.182.41.251', None, 50)
        """
        # short test to see if connected
        for i in range(self.__MAX_TRIES):
            try:
                output = self.__connect.send_command_expect(command, delay_factor=1, max_loops=max_loops, expect_string=expect_string)
                return output
            except socket.error as e:
                if str(e) == 'Socket is closed':
                    # reconnect, connection timed out
                    self.__init__(self.__type, self.__alias, need_src=False)
            except:
                # just try again
                pass

        # if all failed    
        return None

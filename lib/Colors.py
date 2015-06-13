# no shebang here
# -*- coding: UTF-8 -*-
# borja@libcrack.so
# sab ene 10 11:57:36 CET 2015

from Logger import Logger
logger = Logger.logger

class Colors(object):
    """
        Base class for coloring the terminal output

        >>> import Colors
        >>> colors = Colors.Colors()
        >>> print colors.red + "THIS IS RED" + colors.reset
        >>> THIS IS RED
        >>> print colors.blue + "THIS IS BLUE" + colors.reset
        >>> THIS IS BLUE
        >>> print colors.purple + "THIS IS PURPLE" + colors.reset
        >>> THIS IS PURPLE
        >>>
        >>> colors.error('Error MSG')
        >>> ERROR MSG
        >>> colors.info('OK MSG')
        >>> OK MSG
        >>>

    """

    def __init__(self):
        self.purple = '\033[95m'
        self.blue = '\033[94m'
        self.green = '\033[92m'
        self.yellow = '\033[93m'
        self.red = '\033[91m'
        self.reset = '\033[0m'

    @classmethod
    def error(self,msg,pre=''):
        logger.error(msg)
        print ("%s[%sERROR%s] %s" % (pre,self.red,self.reset,msg))

    @classmethod
    def warning(self,msg,pre=''):
        logger.warning(msg)
        print ("%s[%sWARNING%s] %s" % (pre,self.yellow,self.reset,msg))

    @classmethod
    def info (self,msg,pre=''):
        logger.info(msg)
        print ("%s[%sINFO%s] %s" % (pre,self.blue,self.reset,msg))

    @classmethod
    def ok (self,msg,pre=''):
        logger.info(msg)
        print ("%s[%sOK%s] %s" % (pre,self.green,self.reset,msg))

    @classmethod
    def debug (self,msg,pre=''):
        logger.debug(msg)
        print ("%s[%sDEBUG%s] %s" % (pre,self.purple,self.reset,msg))

    @classmethod
    def normal (self,msg,pre=''):
        logger.info(msg)
        print ("%s%s" % (pre,msg))

    @classmethod
    def plain (self,msg,pre=''):
        self.normal (msg,pre)

# vim:ts=4 sts=4 tw=79 expandtab:

# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Provides an INI storage class to the Exact Online REST API Library.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015-2018 Walter Doekes, OSSO B.V.

Usage:

    storage = IniStorage('read_and_writable.ini')

Example ini file:

    [server]
    auth_url = https://start.exactonline.co.uk/api/oauth2/auth
    rest_url = https://start.exactonline.co.uk/api
    token_url = https://start.exactonline.co.uk/api/oauth2/token

    [application]
    base_url = https://example.com
    client_id = {12345678-abcd-1234-abcd-0123456789ab}
    client_secret = ZZZ999xxx000

    [transient]
    access_expiry = 1426492503
    access_token = dAfjGhB1k2tE2dkG12sd1Ff1A1fj2fH2Y1j1fKJl2f1sD1ON275zJNUy...
    code = dAfj!hB1k2tE2dkG12sd1Ff1A1fj2fH2Y1j1fKJl2f1sD1ON275zJNUy...
    division = 123456
    refresh_token = SDFu!12SAah-un-56su-1fj2fH2Y1j1fKJl2f1sDfKJl2f1sD11FfUn1...

"""
from .base import ExactOnlineConfig, MissingSetting

try:
    from configparser import NoSectionError, NoOptionError, ConfigParser
except ImportError:  # python2
    from ConfigParser import (
        NoSectionError, NoOptionError,
        SafeConfigParser as ConfigParserOldStyle)

    class ConfigParser(ConfigParserOldStyle, object):
        """
        We require this adapter to upgrade the RawConfigParser to a
        new-style class. Only needed in Python2.
        """
        def __init__(self, **kwargs):
            # Must call this __init__ manually :(
            ConfigParserOldStyle.__init__(self, **kwargs)
            super(ConfigParser, self).__init__(**kwargs)


class IniStorage(ExactOnlineConfig, ConfigParser):
    """
    Configuration based on the SafeConfigParser and the
    ExactOnlineConfig.

    Takes a ``filename_or_fp`` which can either be a filename or a file
    pointer. If it is a filename, all set() operations are destructive:
    the file will be automatically updated.
    """
    def __init__(self, filename_or_fp, **kwargs):
        super(IniStorage, self).__init__(**kwargs)

        if hasattr(filename_or_fp, 'read'):
            if hasattr(self, 'read_file'):
                self.read_file(filename_or_fp)
            else:
                self.readfp(filename_or_fp)  # python<3.2
            self.overwrite = False
        else:
            self.read([filename_or_fp])
            self.overwrite = filename_or_fp

    def get(self, section, option, **kwargs):
        """
        Get method that raises MissingSetting if the value was unset.

        This differs from the SafeConfigParser which may raise either a
        NoOptionError or a NoSectionError.

        We take extra **kwargs because the Python 3.5 configparser extends the
        get method signature and it calls self with those parameters.

            def get(self, section, option, *, raw=False, vars=None,
                    fallback=_UNSET):
        """
        try:
            ret = super(ExactOnlineConfig, self).get(section, option, **kwargs)
        except (NoOptionError, NoSectionError):
            raise MissingSetting(option, section)

        return ret

    def set(self, section, option, value):
        """
        Set method that (1) auto-saves if possible and (2) auto-creates
        sections.
        """
        try:
            super(ExactOnlineConfig, self).set(section, option, value)
        except NoSectionError:
            self.add_section(section)
            super(ExactOnlineConfig, self).set(section, option, value)

        # Save automatically!
        self.save()

    def save(self):
        if self.overwrite:
            with open(self.overwrite, 'w') as output:
                self.write(output)

# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Provides storage classes to the Exact Online REST API Library.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015-2018 Walter Doekes, OSSO B.V.

Usage:

    from exactonline.storage.ini import IniStorage

    # See example ini contents in ini.py
    storage = IniStorage('read_and_writable.ini')

Or, if you want to use your own storage backend, you may provide a set()
and get() method and inherit from the ExactOnlineConfig.

    from exactonline.storage.base import ExactOnlineConfig, MissingSetting

    class MyStorage(ExactOnlineConfig):
        def get(self, section, option):
            try:
                return self.fetch_stuff_from_somewhere(...)
            except:
                raise MissingSetting()

        def set(self, section, option, value):
            self.store_stuff_somewhere(...)

"""
from warnings import warn

from .base import ExactOnlineConfig, MissingSetting
from .ini import IniStorage as _IniStorage

__all__ = ('ExactOnlineConfig', 'IniStorage', 'MissingSetting')


class IniStorage(_IniStorage):
    def __init__(self, *args, **kwargs):
        warn(
            'IniStorage has been moved to exactonline.storage.ini. '
            'Please update your imports.',
            DeprecationWarning)
        super(IniStorage, self).__init__(*args, **kwargs)

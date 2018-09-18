# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Helper for bankaccounts resources.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2018 Walter Doekes, OSSO B.V.
"""
from .manager import Manager


class BankAccounts(Manager):
    resource = 'crm/BankAccounts'

    def filter(self, account_id=None, **kwargs):
        if account_id is not None:
            remote_id = self._remote_guid(account_id)
            # Filter by our account number.
            self._filter_append(kwargs, u'Account eq %s' % (remote_id,))

        return super(BankAccounts, self).filter(**kwargs)

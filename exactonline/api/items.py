# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Helper for items resources.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2018 Walter Doekes, OSSO B.V.
"""
from .manager import Manager


class Items(Manager):
    # https://start.exactonline.co.uk/docs/HlpRestAPIResourcesDetails.aspx?name=LogisticsItems
    resource = 'logistics/Items'

    def filter(self, code=None, **kwargs):
        if 'select' not in kwargs:
            kwargs['select'] = 'ID,Code,Name'

        if code is not None:
            remote_id = self._remote_code(code)
            # Filter by our item code.
            self._filter_append(kwargs, u'Code eq %s' % (remote_id,))

        return super(Items, self).filter(**kwargs)

    def _remote_code(self, code):
        return u"'%18s'" % (code.replace("'", "''"),)

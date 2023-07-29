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

    def filter(self, code=None, modified_since_date=None, **kwargs):
        if code and modified_since_date:
            raise ValueError("You can only filter on either code, or modified_since_date")

        if 'select' not in kwargs:
            kwargs['select'] = ','.join(['ID', 'Code', 'CostPriceStandard', 'Description'])

        if code is not None:
            self._filter_append(kwargs, f"Code eq '{code}'")

        if modified_since_date:
            datestring = modified_since_date.strftime('%Y-%m-%d')
            self._filter_append(kwargs, f"Modified gt datetime'{datestring}'")

        return super().filter(**kwargs)

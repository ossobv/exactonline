# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Helper for BulkSalesItemPrices resources.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2018 Walter Doekes, OSSO B.V.
"""
from .manager import Manager


class BulkSalesItemPrices(Manager):
    resource = 'bulk/Logistics/SalesItemPrices'
    # https://start.exactonline.co.uk/docs/HlpRestAPIResourcesDetails.aspx?
    #   name=BulkLogisticsSalesItemPrices

    def filter(self, item_id=None, **kwargs):
        if 'select' not in kwargs:
            kwargs['select'] = (
                'ID,Account,AccountName,Item,ItemCode,Price,Currency')

        if item_id:
            self._filter_append(kwargs, f"Item eq {item_id}")

        return super().filter(**kwargs)

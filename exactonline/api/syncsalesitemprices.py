# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Helper for SyncSalesItemPrices resources.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2018 Walter Doekes, OSSO B.V.
"""
from .manager import Manager


class SyncSalesItemPrices(Manager):
    resource = 'sync/Logistics/SalesItemPrices'
    # https://start.exactonline.co.uk/docs/HlpRestAPIResourcesDetails.aspx?name=SyncLogisticsSalesItemPrices

    def filter(self, timestamp_gt, **kwargs):
        if 'select' not in kwargs:
            kwargs['select'] = 'ID,Account,AccountName,Item,ItemCode,Price,Currency'

        self._filter_append(kwargs, f"Timestamp gt {timestamp_gt}")

        return super().filter(**kwargs)

# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Helper for items resources.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2018 Walter Doekes, OSSO B.V.
"""
from .manager import Manager


class SupplierItems(Manager):
    # https://start.exactonline.co.uk/docs/HlpRestAPIResourcesDetails.aspx?
    #   name=LogisticsSupplierItem
    resource = 'logistics/SupplierItem'

    def filter(self, **kwargs):
        if 'select' not in kwargs:
            kwargs['select'] = (
                'ID,ItemCode,Supplier,SupplierDescription,'
                'CountryOfOrigin,PurchasePrice')

        return super().filter(**kwargs)

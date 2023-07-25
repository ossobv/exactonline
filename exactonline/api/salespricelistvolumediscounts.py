# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Helper for SalesPriceListVolumeDiscounts resources.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2018 Walter Doekes, OSSO B.V.
"""
from .manager import Manager


class SalesPriceListVolumeDiscounts(Manager):
    resource = 'sales/SalesPriceListVolumeDiscounts'
    # https://start.exactonline.co.uk/docs/HlpRestAPIResourcesDetails.aspx?name=SalesSalesPriceListVolumeDiscounts

    def filter(self, pricelistperiod_id=None, **kwargs):
        if 'select' not in kwargs:
            kwargs['select'] = 'ID,BasePriceAmount,Item,ItemCode,Discount,NewPrice,Quantity'

        if pricelistperiod_id:
            self._filter_append(kwargs, f"PriceListPeriod eq guid'{pricelistperiod_id}'")

        return super().filter(**kwargs)

# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Helper for SalesPriceListPeriods resources.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2018 Walter Doekes, OSSO B.V.
"""
from .manager import Manager


class SalesPriceListPeriods(Manager):
    resource = 'sales/SalesPriceListPeriods'
    # https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=SalesSalesPriceListPeriods

    def filter(self, pricelist_id=None, **kwargs):
        if pricelist_id:
            self._filter_append(kwargs, f"PriceList eq guid'{pricelist_id}'")

        return super().filter(**kwargs)

    def latest(self, pricelist_id):
        all_periods = self.filter(pricelist_id=pricelist_id)
        all_periods = sorted(all_periods, key=lambda x: x['StartDate'])
        return all_periods[-1]
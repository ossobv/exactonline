# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Helper for SalesPriceLists resources.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2018 Walter Doekes, OSSO B.V.
"""
from .manager import Manager


class SalesPriceLists(Manager):
    resource = 'sales/SalesPriceLists'
    # https://start.exactonline.nl/docs/HlpRestAPIResourcesDetails.aspx?name=SalesSalesPriceLists

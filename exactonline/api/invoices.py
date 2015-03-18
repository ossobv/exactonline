# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Helper for invoice resources.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015 Walter Doekes, OSSO B.V.
"""
from .manager import Manager


class Invoices(Manager):
    resource = 'salesentry/SalesEntries'

    def get(self, **kwargs):
        invoice_dict = super(Invoices, self).get(**kwargs)
        try:
            uri = invoice_dict[u'SalesEntryLines'][u'__deferred']['uri']
        except KeyError:
            # Perhaps there is a 'select' filter.
            pass
        else:
            invoicelines_dict = self._api.restv1('GET', str(uri))
            invoice_dict[u'SalesEntryLines'] = invoicelines_dict
        return invoice_dict

    def filter(self, invoice_number=None, reporting_period=None, **kwargs):
        if invoice_number is not None:
            remote_id = self._remote_invoice_number(invoice_number)
            # Filter by our invoice_number.
            self._filter_append(kwargs, u'YourRef eq %s' % (remote_id,))
            # # Let the query return the invoice lines too. <-- DOES NOT WORK
            # assert 'expand' not in kwargs
            # kwargs['expand'] = 'SalesInvoiceLines'
            # kwargs['select'] = ('Amount,SalesInvoiceLines/LineNumber,'
            #                     'SalesInvoiceLines/Amount,'
            #                     'SalesInvoiceLines/VATAmount')

        if reporting_period is not None:
            # Filter by our invoice_number.
            self._filter_append(kwargs, u'ReportingYear eq %d' % (reporting_period.year,))
            self._filter_append(kwargs, u'ReportingPeriod eq %d' % (reporting_period.month,))

        return super(Invoices, self).filter(**kwargs)

    def _remote_invoice_number(self, invoice_number):
        return u"'%s'" % (invoice_number.replace("'", "''"),)

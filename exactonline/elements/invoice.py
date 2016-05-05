# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Data structures for communication with remote.

Example usage::

    class BossoExactInvoice(ExactInvoice):
        def __init__(self, bosso_invoice=None, **kwargs):
            super(BossoExactInvoice, self).__init__(**kwargs)

            self._bosso_invoice = bosso_invoice

        def get_customer(self):
            return BossoExactCustomer(
                bosso_relation=self._bosso_invoice.relation, api=self._api)

        def get_created_data(self):
            return self._bosso_invoice.open_date

        # ...

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015 Walter Doekes, OSSO B.V.
"""
from .base import ExactElement
from ..exceptions import ExactOnlineError, ObjectDoesNotExist


class UnknownLedgerCodes(ExactOnlineError):
    def __init__(self, ledger_codes):
        super(UnknownLedgerCodes, self).__init__(
            'One or more ledger codes are not found in Exact: %s' % (
                ', '.join(ledger_codes),))
        self.ledger_codes = ledger_codes


class ExactInvoice(ExactElement):
    def get_guid(self):
        exact_invoice = self.__get_remote()
        return exact_invoice['EntryID']

    def get_customer(self):
        # The ExactOnline customer id.
        raise NotImplementedError()

    def get_created_date(self):
        # Period used for both EntryDate and ReportingPeriod. Use the
        # "open_date" if available.
        return NotImplementedError()

    def get_exact_journal(self):
        # E.g. "70" for "Verkoopboek"
        raise NotImplementedError()

    def get_ledger_code_to_guid_map(self, codes):
        """
        Convert set of human codes and to a dict of code to exactonline
        guid mappings.

        Example::

            ret = inv.get_ledger_code_to_guid_map(['1234', '5555'])
            ret == {'1234': '<guid1_from_exactonline_ledgeraccounts>',
                    '5555': '<guid2_from_exactonline_ledgeraccounts>'}
        """
        if codes:
            codes = set(str(i) for i in codes)
            ledger_ids = self._api.ledgeraccounts.filter(code__in=codes)
            ret = dict((str(i['Code']), i['ID']) for i in ledger_ids)
            found = set(ret.keys())
            missing = (codes - found)
            if missing:
                raise UnknownLedgerCodes(missing)
            return ret
        return {}

    def get_ledger_lines(self):
        # Return a bunch of ledger lines, like this:
        # {'code': '1234',          # ledger code
        #  'vat_percentage': '21',  # 21%
        #  'total_amount_excl_vat': Decimal(12.5),
        #  'description': '200 items of foo bar'}
        raise NotImplementedError()

    def get_invoice_number(self):
        raise NotImplementedError()

    def get_total_amount_incl_vat(self):
        # Used in AmountDC (default currency) and AmountFC (foreign
        # currency).
        raise NotImplementedError()

    def get_total_vat(self):
        raise NotImplementedError()

    def hint_exact_invoice_number(self):
        # Exact does not honor all requests.
        raise NotImplementedError()

    def assemble(self):
        invoice_number = self.get_invoice_number()
        customer = self.get_customer()

        total_amount_incl_vat = self.get_total_amount_incl_vat()
        total_vat = self.get_total_vat()
        created_date = self.get_created_date()
        description = u'%s - %s, %s' % (invoice_number, customer.get_name(),
                                        created_date.strftime('%m-%Y'))

        # Make sure the customer exists.
        try:
            customer_guid = customer.get_guid()
        except ObjectDoesNotExist:
            customer.commit()
            customer_guid = customer.get_guid()

        # Compile data to send.
        data = {
            # Converting to string is better than converting to float.
            'AmountDC': str(total_amount_incl_vat),  # DC=default_currency
            'AmountFC': str(total_amount_incl_vat),  # FC=foreign_currency

            # Strange! We receive the date(time) objects as
            # '/Date(unixmilliseconds)/' (mktime(d.timetuple())*1000),
            # but we must send them as ISO8601.
            # NOTE: invoice.open_date is a date, not a datetime, so
            # tzinfo calculations won't work on it, and we cannot use
            # '%z' in the strftime format. Unused code:
            #   import pytz; tzinfo = pytz.timezone('Europe/Amsterdam')
            #   entry_date = tzinfo.localize(invoice.open_date)
            # Pretend we're in UTC and send "Z" zone.
            'EntryDate': created_date.strftime('%Y-%m-%dT%H:%M:%SZ'),

            'Customer': customer_guid,
            'Description': description,
            'Journal': self.get_exact_journal(),
            'ReportingPeriod': created_date.month,
            'ReportingYear': created_date.year,
            'SalesEntryLines': self.assemble_lines(),
            'VATAmountDC': str(total_vat),  # str>float, DC=default_currency
            'VATAmountFC': str(total_vat),  # str>float, FC=foreign_currency
            'YourRef': invoice_number,

            'InvoiceNumber': self.hint_exact_invoice_number(),
        }

        return data

    def assemble_lines(self):
        ret = []

        # Fetch ledger lines.
        ledger_lines = self.get_ledger_lines()

        # Cache ledger codes to ledger GUIDs.
        ledger_ids = self.get_ledger_code_to_guid_map(
            set(i['code'] for i in ledger_lines))

        for ledger_line in self.get_ledger_lines():
            # We must use VATCode. It accepts VATPercentages, but only
            # when it is higher than 0. Not using:
            # 'VATPercentage': str(ledger_line['vat_percentage'] / 100)
            if ledger_line['vat_percentage'] == 0:
                vatcode = '0  '  # FIXME: hardcoded.. fetch from API?
            elif ledger_line['vat_percentage'] == 21:
                vatcode = '2  '  # FIXME: hardcoded.. fetch from API?
            else:
                raise NotImplementedError(
                    'Unknown VAT: %s' % (ledger_line['vat_percentage'],))

            # Again, convert from decimal to str to get more precision.
            line = {'AmountDC': str(ledger_line['total_amount_excl_vat']),
                    'AmountFC': str(ledger_line['total_amount_excl_vat']),
                    'Description': ledger_line['description'],
                    'GLAccount': ledger_ids[ledger_line['code']],
                    'VATCode': vatcode}
            ret.append(line)

        return ret

    def commit(self):
        try:
            exact_guid = self.get_guid()
        except ObjectDoesNotExist:
            exact_guid = None

        data = self.assemble()

        if exact_guid:
            # We cannot supply the SalesEntryLines in the dict like
            # usual when we update (PUT). Instead, we add the new ones
            # and remove the old ones by hand.
            #
            # You don't want to do that the other way around, because
            # deleting the last item removes the entire invoice.
            old_salesentrylines = self.__get_remote()['SalesEntryLines']

            # Add new (and pop the SalesEntryLines from the invoice
            # dict).
            new_salesentrylines = data.pop('SalesEntryLines')
            for line in new_salesentrylines:
                line['EntryID'] = exact_guid
                self._api.restv1('POST', 'salesentry/SalesEntryLines', line)

            # Remove old.
            for line in old_salesentrylines:
                self._api.restv1(
                    'DELETE', ("salesentry/SalesEntryLines(guid'%s')" %
                               line['ID']))

            # Update the invoice (without the SalesEntryLines).
            ret = self._api.invoices.update(exact_guid, data)
            # ret is None
        else:
            ret = self._api.invoices.create(data)
            # ret is a exact_invoice

        # Drop cache, if used.
        if hasattr(self, '_cached_remote'):
            del self._cached_remote

        return ret

    def __get_remote(self):
        if not hasattr(self, '_cached_remote'):
            try:
                self._cached_remote = self._api.invoices.get(
                    invoice_number=self.get_invoice_number())
            except ObjectDoesNotExist as e:
                self._cached_remote = e
        if isinstance(self._cached_remote, Exception):
            raise self._cached_remote
        return self._cached_remote

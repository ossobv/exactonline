"""
Helpers to work with Quotations in exact online.

Written by Ties Verschuren
"""
import datetime

from .manager import Manager
from ..resource import GET


class QuotationStatus:
    """
    The status of the quotation version.
    5 = Rejected, 6 = Reviewed and closed, 10 = Recovery, 20 = Draft,
    25 = Open, 35 = Processing... , 40 = Printed, 50 = Accepted
    """
    REJECTED = 5
    CLOSED = 6
    RECOVERY = 10
    DRAFT = 20
    OPEN = 25
    PROCESSING = 35
    PRINTED = 40
    ACCEPTED = 50


class QuotationAcceptAction:
    """
    The action undertaken during the AcceptQuotationCall
    0 = No action (Default)
    1 = create sales order
    2 = create sales invoice
    3 = create project
    """
    NO_ACTION = 0
    CREATE_SALES_ORDER = 1
    CREATE_SALES_INVOICE = 2
    CREATE_PROJECT = 3


class Quotations(Manager):
    resource = 'crm/Quotations'

    def get(self, **kwargs):
        quotations_dict = super(Quotations, self).get(**kwargs)
        try:
            uri = quotations_dict[u'QuotationLines'][u'__deferred']['uri']
        except KeyError:
            # Perhaps there is a 'select' filter.
            pass
        else:
            quotation_lines_dict = self._api.restv1(GET(str(uri)))
            quotations_dict[u'QuotationLines'] = quotation_lines_dict

        return self.parse_result(quotations_dict)

    def filter(self, **kwargs):
        return self.parse_result(super(Quotations, self).filter(**kwargs))

    def parse_result(self, result):
        """
        Pares the response from the api
        by making datetime objects of the json date strings

        :param result: The response to parse
        :return: Parsed response
        """
        # Converts dates
        date_fields = ('CloseDate',
                       'ClosingDate',
                       'Created',
                       'DueDate',
                       'Modified',
                       'QuotationDate')
        for quotation in result:
            for date_field in date_fields:
                if date_field in quotation:
                    quotation[date_field] = self.json_date_to_datetime(
                        quotation[date_field])

        return result

    def json_date_to_datetime(self, json):
        """
        Converts a .NET json date to a datetime object.

        :param json: A .NET json date like /Date(1516741035800)/
        :return: datetime The date as an datetime object
        """
        # sign in case a timezone is also in the date
        sign = json[-7]
        if sign not in '-+' or len(json) == 13:
            milliseconds = int(json[6:-2])
        else:
            milliseconds = int(json[6:-7])
            hh = int(json[-7:-4])
            mm = int(json[-4:-2])
            if sign == '-':
                mm = -mm
            milliseconds += (hh * 60 + mm) * 60000

        return datetime.datetime(1970, 1, 1) + datetime.timedelta(
            milliseconds=milliseconds)

# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Combines the helper superclasses and the helper resource managers into the
ExactApi class.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015-2018 Walter Doekes, OSSO B.V.
"""
from ..rawapi import ExactRawApi

from .autorefresh import Autorefresh
from .unwrap import Unwrap
from .v1division import V1Division

from .bankaccounts import BankAccounts
from .contacts import Contacts
from .documents import Documents
from .documentattachments import DocumentAttachments
from .invoices import Invoices
from .ledgeraccounts import LedgerAccounts
from .quotations import Quotations
from .receivables import Receivables
from .relations import Relations
from .vatcodes import VatCodes


class ExactApi(
    # Talk to /api/v1/{division} directly.
    V1Division,
    # Strip the surrounding "d" and "results" dictionary
    # items.
    Unwrap,
    # Ensure that tokens are refreshed: if we get a 401, refresh the
    # tokens.
    Autorefresh,
    # The base class comes last: talk to /api.
    ExactRawApi
):
    bankaccounts = BankAccounts.as_property()
    contacts = Contacts.as_property()
    documents = Documents.as_property()
    documentattachments = DocumentAttachments.as_property()
    invoices = Invoices.as_property()
    ledgeraccounts = LedgerAccounts.as_property()
    quotations = Quotations.as_property()
    receivables = Receivables.as_property()
    relations = Relations.as_property()
    vatcodes = VatCodes.as_property()

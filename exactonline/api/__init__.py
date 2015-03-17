# vim: set ts=8 sw=4 sts=4 et ai tw=79:
from ..rawapi import ExactRawApi

from .autorefresh import Autorefresh
from .unwrap import Unwrap
from .v1division import V1Division

from .invoices import Invoices
from .ledgeraccounts import LedgerAccounts
from .relations import Relations


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
    invoices = Invoices.as_property()
    ledgeraccounts = LedgerAccounts.as_property()
    relations = Relations.as_property()

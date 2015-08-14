Exact Online REST API Library in Python
=======================================

Exact Online provides accounting software in a Software-as-a-Service
delivery model. It implements an API through a REST interface. This
library aims to ease its use.



Quick jump
----------

* `Usage by example`_
* `Setting up the link`_
* `Implemented resources`_
* `Other benefits`_
* `License`_
* `TODO`_
* `Further reading`_
* `Changes`_



Usage by example
----------------

Set up the basics:

.. code-block:: python

    from exactonline.api import ExactApi
    from exactonline.exceptions import ObjectDoesNotExist
    from exactonline.storage import IniStorage

    # Create a function to get the api with your own storage backend.
    def get_api():
        storage = IniStorage('/path/to/config.ini')
        return ExactApi(storage=storage)
    api = get_api()

Get an invoice:

.. code-block:: python

    # Get an invoice by your own invoice number (YourRef).
    # Returns a dictionary, or raises ObjectDoesNotExist.
    invoice = api.invoices.get(invoice_number='F0005555')

It looks somewhat like this:

.. code-block:: python

    invoice == {
        u'AmountDC': 50.8,
        u'AmountFC': 50.8,
    # ...
        u'SalesEntryLines': [
            {u'AmountDC': 41.98,
             u'AmountFC': 41.98,
    # ...
             u'Description': u'Omzet backups',
             u'VATBaseAmountDC': 41.98,
             u'VATBaseAmountFC': 41.98},
        ],
    # ...
        u'VATAmountDC': 8.82,
        u'VATAmountFC': 8.82,
        u'YourRef': u'F0005555',
        u'__metadata': {u'type': u'Exact.Web.Api.Models.SalesEntry',
                        u'uri': u"https://start.exactonline.nl/api/v1/..."},
    }

Get relations:

.. code-block:: python

    relations_limit_2 = api.relations.filter(top=2)
    # that was cheaper than: api.relations.all()[0:2]

    relations_limit_2 == [
        {u'Code': u'              1068',
         u'ID': u'11111111-2222-3333-4444-555555555555',
         u'Name': u'ACME Corporation',
         u'__metadata': {u'type': u'Exact.Web.Api.Models.Account',
                         u'uri': u"https://start.exactonline.nl/api/v1/...')"}},
        {u'Code': u'               555',
         u'ID': u'22222222-3333-4444-5555-666666666666',
         u'Name': u'Daffy Duck Ltd.',
         u'__metadata': {u'type': u'Exact.Web.Api.Models.Account',
                         u'uri': u"https://start.exactonline.nl/api/v1/...')"}}
    ]

Update a relation:

.. code-block:: python

    daffy_duck = api.relations.get(relation_code='555')
    api.relations.update(daffy_duck['ID'], {'Name': 'Daffy Duck and sons'})

Delete a relation:

.. code-block:: python

    daffy_duck = api.relations.get(relation_code='555')
    api.relations.delete(daffy_duck['ID'])

Create an invoice:

.. code-block:: python

    customer_data = api.relations.get(relation_code='123')  # local relation_code
    customer_guid = customer_data['ID']
    invoice_data = {
        'AmountDC': str(amount_with_vat),  # DC = default currency
        'AmountFC': str(amount_with_vat),  # FC = foreign currency
        'EntryDate': invoice_date.strftime('%Y-%m-%dT%H:%M:%SZ'),  # pretend we're in UTC
        'Customer': customer_guid,
        'Description': u'Invoice description',
        'Journal': remote_journal,  # 70 "Verkoopboek"
        'ReportingPeriod': invoice_date.month,
        'ReportingYear': invoice_date.year,
        'SalesEntryLines': [],
        'VATAmountDC': str(vat_amount),
        'VATAmountFC': str(vat_amount),
        'YourRef': local_invoice_number,
        # must start uniquely at the start of a year, defaults to:
        # YYJJ0001 where YY=invoice_date.year, and JJ=remote_journal
        'InvoiceNumber': '%d%d%04d' % (invoice_date.year, remote_journal,
                                       int(local_invoice_number),
    }
    # The SalesEntryLines need to be filled with a bunch of dictionaries
    # with these keys: AmountDC, AmountFC, Description, GLAccount,
    # VATCode where GLAccount holds the Journal remote GUID, and the
    # amounts are without VAT.

    api.invoices.create(invoice_dict)

You may need to play around a bit to find out which fields are
mandatory, and what kind of values the fields need.  The `Exact Online
REST resources list`_ isn't always clear on that.



Setting up the link
-------------------

You'll need a storage backend. The default ``IniStorage`` can be taken from
``exactonline.storage``.

.. code-block:: python

    from exactonline.storage import IniStorage

    class MyIniStorage(IniStorage):
        def get_response_url():
            "Configure your custom response URL."
            return self.get_base_url() + '/oauth/success/'

    storage = MyIniStorage('/path/to/config.ini')

(Note that you're not tied to using ``.ini`` files. See
``exactonline/storage.py`` if you want to use a different storage
backend.)

You need to set up access to your Exact Online SaaS instance, by creating an
export link. See `Exact Online creating credentials`_ for more info.

Take that info, and configure it in your ``config.ini``.

.. code-block:: ini

    [server]
    auth_url = https://start.exactonline.co.uk/api/oauth2/auth
    rest_url = https://start.exactonline.co.uk/api
    token_url = https://start.exactonline.co.uk/api/oauth2/token

    [application]
    base_url = https://example.com
    client_id = {12345678-abcd-1234-abcd-0123456789ab}
    client_secret = ZZZ999xxx000

Create an initial URL:

.. code-block:: python

    api = ExactApi(storage=storage)
    url = api.create_auth_request_url()

The URL will look like this; redirect the user there so he may
authenticate and allow your application access to Exact Online (this is
OAuth):

.. code-block::

    https://start.exactonline.nl/api/oauth2/auth?
      client_id=%7B12345678-abcd-1234-abcd-0123456789ab%7D&
      redirect_uri=https%3A//example.com/oauth/success/&
      response_type=code

After authentication he will get redirected back to:

.. code-block:: python

    https://example.com/oauth/success/?code=...

You should implement a view on that URL, that does basically this:

.. code-block:: python

    api.request_token(code)

At this point, you should configure your default division, if you
haven't already:

.. code-block:: python

    division_choices, current_division = api.get_divisions()
    api.set_division(division_choices[0][0])  # select ID of first division

Now you're all set!



Implemented resources
---------------------

View ``exactonline/api/__init__.py`` to see which resource helpers are
implemented.

Currently, it looks like this:

.. code-block:: python

    invoices = Invoices.as_property()
    ledgeraccounts = LedgerAccounts.as_property()
    receivables = Receivables.as_property()
    relations = Relations.as_property()

But you can call resources which don't have a helper directly. The
following two three are equivalent:

.. code-block:: python

    api.relations.all()
    api.restv1('GET', 'crm/Accounts')
    api.rest('GET', 'v1/%d/crm/Accounts' % selected_division)

As are the following three:

.. code-block:: python

    api.relations.filter(top=2)
    api.restv1('GET', 'crm/Accounts?$top=2')
    api.rest('GET', 'v1/%d/crm/Accounts?$top=2' % selected_division)

And these:

.. code-block:: python

    api.invoices.filter(filter="EntryDate gt datetime'2015-01-01'")
    api.restv1('GET', 'salesentry/SalesEntries?' +
      '$filter=EntryDate%20gt%20datetime%272015-01-01%27')
    api.rest('GET', 'v1/%d/salesentry/SalesEntries?' +
      '$filter=EntryDate%%20gt%%20datetime%%272015-01-01%%27' %
      selected_division)
    # convinced yet that the helpers are useful?

See the `Exact Online REST resources list`_ for all available resources.



Other benefits
--------------

The ExactApi class ensures that:

* Tokens are refreshed as needed (see: ``exactonline/api/autorefresh.py``).
* Paginated lists are automatically downloaded in full (see:
  ``exactonline/api/unwrap.py``).



License
-------

Exact Online REST API Library in Python is free software: you can
redistribute it and/or modify it under the terms of the GNU Lesser
General Public License as published by the Free Software Foundation,
version 3 or any later version.



TODO
----

* Replace base_url with response_url?
* Add travis build stuff.



Further reading
---------------

* `Exact Online REST API`_.
* `Exact Online creating credentials`_.
* `Exact Online REST resources list`_
* `Tips by Bas van Beek`_.

.. _`Exact Online REST API`: https://developers.exactonline.com/#RestIntro.html%3FTocPath%3DExact%2520Online%2520REST%2520API%7C_____0
.. _`Exact Online creating credentials`: https://developers.exactonline.com/Content/restauthoauth.html
.. _`Exact Online REST resources list`: https://start.exactonline.co.uk/docs/HlpRestAPIResources.aspx?SourceAction=10
.. _`Tips by Bas van Beek`: http://www.basvanbeek.nl/exact-online-tips/



Changes
-------

* v0.1.3:

  - Add ``receivables`` manager to the API. This manager allows you to
    build a list similar to the *Outstanding Receivables* page of
    *Financial Reporting*.
  - Add ``api.invoices.map_exact2foreign_invoice_numbers`` and
    ``api.invoices.map_foreign2exact_invoice_numbers`` methods to
    quickly get a mapping between our own and the ExactOnline invoice
    numbers.
  - Python3 compatibility.
  - Minor fixes.

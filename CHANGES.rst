Changes
-------

* vHEAD:

  - ...

* v0.2.4:

  - Improve HTTP functions for better error reporting and better Py23
    compatibility.

* v0.2.3:

  - Add api.invoices.filter(invoice_number__in=LIST) filter.
  - Iterate over resultsets instead of using recursion (api.unwrap).
  - Fix python3 compatibility issue: bytestring found on autorefresh.
    Thanks @wpxgit.

* v0.2.2:

  - Correct RST source in CHANGES file. Did not display properly on
    PyPI.

* v0.2.1:

  - Correct example Python code in docs. Thanks @alexBaizeau.
  - Add ``exactonline.elements`` that were missing in the 0.2.0
    distributed package. Thanks @hcwsegers.
  - Add overridable ``get_ledger_code_to_guid_maps()`` helper to the
    invoices elements class.

* v0.2.0:
  
  - Update build/PyPI info: move to Stable, add Python 3.4 and 3.5
    version, fix Python 3 compatibility.
  - Fix a few README RST issues. Update OAuth documentation.
  - Add initial ``exactonline.elements`` to use for easier object
    oriented data submissions.
  - Add and improve SSL, API and Python3 tests.

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

# vim: set ts=8 sw=4 sts=4 et ai tw=79:
"""
Provides a base storage class to the Exact Online REST API Library.

This file is part of the Exact Online REST API Library in Python
(EORALP), licensed under the LGPLv3+.
Copyright (C) 2015-2018 Walter Doekes, OSSO B.V.

If you subclass this, it is easiest to implement get()/set() methods, where the
get() raises MissingSetting when a setting wasn't found.

Of course you could also implement all individual getters and setters yourself.

See the IniStorage() class for a sample implementation.

    from exactonline.storage.base import ExactOnlineConfig, MissingSetting

    class MyStorage(ExactOnlineConfig):
        def get(self, section, option):
            try:
                return self.fetch_stuff_from_somewhere(...)
            except:
                raise MissingSetting()

        def set(self, section, option, value):
            self.store_stuff_somewhere(...)

"""
try:
    unicode
except NameError:
    # python3
    def native_string(value):
        if isinstance(value, str):
            return value
        if isinstance(value, bytes):
            return value.decode('utf-8')
        return str(value)
else:
    # python2
    def native_string(value):
        if isinstance(value, str):
            return value
        if isinstance(value, unicode):  # noqa: no NameError for flake8.3
            return value.encode('utf-8')
        return str(value)


class MissingSetting(ValueError):
    pass


class ExactOnlineConfig(object):
    """
    The configuration class.

    The getters all assert that a native-string type is returned (unless
    a different type is explicitly mentioned). This way the callers
    won't have to think about what they get.
    """
    def get_or_set_default(self, section, option, value):
        """
        Base method to fetch values and to set defaults in case they
        don't exist.
        """
        try:
            ret = self.get(section, option)
        except MissingSetting:
            self.set(section, option, value)
            ret = value

        return ret

    # [server]
    # ; These always return something. They may write their default to
    # ; your config object if they are unset.
    # ; If you want to change the values from your application, you need
    # ; to write your own routines.

    def get_auth_url(self):
        return native_string(self.get_or_set_default(
            'server', 'auth_url',
            'https://start.exactonline.nl/api/oauth2/auth'))

    def get_rest_url(self):
        return native_string(self.get_or_set_default(
            'server', 'rest_url',
            'https://start.exactonline.nl/api'))

    def get_token_url(self):
        return native_string(self.get_or_set_default(
            'server', 'token_url',
            'https://start.exactonline.nl/api/oauth2/token'))

    # [application]
    # ; These return something, or raise MissingSetting if they are
    # ; unset.
    # ; If you want to change the values from your application, you need
    # ; to write your own routines.

    def get_base_url(self):
        return native_string(self.get('application', 'base_url'))

    def get_iteration_limit(self):
        return int(self.get_or_set_default(
            'application', 'iteration_limit', '50'))

    def get_response_url(self):
        """
        Get a default value for get_response_url() where the user is
        redirected back to after the OAuth step on the ExactOnline site.

        You'll probably want to subclass this method to return a more
        specific location.
        """
        return self.get_base_url()

    def get_client_id(self):
        return native_string(self.get('application', 'client_id'))

    def get_client_secret(self):
        return native_string(self.get('application', 'client_secret'))

    # [transient]
    # ; These return something, or raise MissingSetting if they are
    # ; unset.
    # ; These will be written to by this exactonline library, so all
    # ; their get methods have set counterparts.

    def get_access_expiry(self):
        return int(self.get('transient', 'access_expiry'))

    def set_access_expiry(self, value):
        self.set('transient', 'access_expiry', native_string(value))

    def get_access_token(self):
        return native_string(self.get('transient', 'access_token'))

    def set_access_token(self, value):
        self.set('transient', 'access_token', native_string(value))

    def get_code(self):
        return native_string(self.get('transient', 'code'))

    def set_code(self, value):
        self.set('transient', 'code', native_string(value))

    def get_division(self):
        return int(self.get('transient', 'division'))

    def set_division(self, value):
        self.set('transient', 'division', native_string(value))

    def get_refresh_token(self):
        return native_string(self.get('transient', 'refresh_token'))

    def set_refresh_token(self, value):
        self.set('transient', 'refresh_token', native_string(value))

    def get_refresh_url(self):
        # Alias for get_token_url().
        return self.get_token_url()

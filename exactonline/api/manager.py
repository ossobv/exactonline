# vim: set ts=8 sw=4 sts=4 et ai tw=79:
from ..exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from ..http import binquote


class Manager(object):
    """
    Inherit from this when you're creating a property on the ExactApi,
    like this:

        class Relations(Manager):
            resource = 'some/resource'

        class ExactApi(...):
            relations = Relations.as_property()

        storage = SomeStorage()
        api = ExactApi(storage=storage)
        api.relations.all()
    """
    resource = None  # set this in your subclass

    @classmethod
    def as_property(cls):
        @property
        def cached_getter(exactapi):
            propname = '_prop_%s' % (cls.__name__,)
            if not hasattr(exactapi, propname):
                setattr(exactapi, propname, cls(exactapi))
            return getattr(exactapi, propname)

        return cached_getter

    def __init__(self, api):
        self._api = api

    # == GET / get one / get many ==

    def all(self):
        # Select all without filtering.
        return self.filter()

    def get(self, **kwargs):
        assert 'top' not in kwargs
        ret = self.filter(top=2, **kwargs)
        if not ret:
            raise ObjectDoesNotExist()
        if len(ret) > 1:
            raise MultipleObjectsReturned()
        return ret[0]

    def filter(self, **kwargs):
        # kwargs = {'filter': "EntryDate+gt+datetime'2014-01-01'", 'top': 5}
        args = []
        for key, value in kwargs.items():
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            else:
                value = str(value)
            args.append('$%s=%s' % (str(key), binquote(value)))
        if args:
            args = ('?' + '&'.join(args))
        else:
            args = ''

        assert isinstance(args, str)
        ret = self._api.restv1('GET', str(self.resource) + args)
        return ret

    # == POST / create ==

    def create(self, relation_dict):
        ret = self._api.restv1('POST', str(self.resource), relation_dict)
        return ret

    # == DELETE / remove ==

    def delete(self, remote_guid):
        remote_id = self._remote_guid(remote_guid)
        uri = '%s(%s)' % (self.resource, remote_id)
        ret = self._api.restv1('DELETE', str(uri))
        return ret

    # == PUT / update ==

    def update(self, remote_guid, relation_dict):
        remote_id = self._remote_guid(remote_guid)
        uri = '%s(%s)' % (self.resource, remote_id)
        ret = self._api.restv1('PUT', str(uri), relation_dict)
        return ret

    # == helpers ==

    def _filter_append(self, kwargs, extra_filter):
        if 'filter' in kwargs:
            kwargs['filter'] = u'(%s) and %s' % (kwargs['filter'],
                                                 extra_filter)
        else:
            kwargs['filter'] = extra_filter

    def _remote_guid(self, remote_guid):
        return "guid'%s'" % (remote_guid,)

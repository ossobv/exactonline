from .manager import Manager


class Documents(Manager):
    resource = 'documents/Documents'

    def filter(self, subject=None, **kwargs):
        if 'select' not in kwargs:
            kwargs['select'] = 'ID,Subject,Type'

        if subject is not None:
            self._filter_append(kwargs, u"trim(Subject) eq '{}'".format(subject))
        return super(Documents, self).filter(**kwargs)

from .manager import Manager


class DocumentAttachments(Manager):
    resource = 'documents/DocumentAttachments'

    def filter(self, file_name=None, **kwargs):
        if 'select' not in kwargs:
            kwargs['select'] = 'ID,Document,FileName'

        if file_name is not None:
            self._filter_append(kwargs, u"trim(FileName) eq '{}'".format(file_name))
        return super(DocumentAttachments, self).filter(**kwargs)

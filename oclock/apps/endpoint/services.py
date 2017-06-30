'''
Created on 06-06-2014

@author: carriagadad
'''
#from django.forms.models import model_to_dict
from oclock.apps.endpoint.models import User


class ApiUtils(object):
    """Utility API functions."""

    @staticmethod
    def serialize_clocks(clocks):
        pass
        """Function to serialize a queryset of Book models.

        Args:
            books: a queryset
        Returns:
            A list of Book ProtoRPC messages
        """

        """items = []
        for clock in clocks:
            item = model_to_dict(clock, fields=['title', 'author', 'ebook_available'])
            item['publication_year'] = clock.publication_year.year
            items.append(User(**item))

        return items"""
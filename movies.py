import logging

from movies_app.models import Movie
from django.db.models import Q

from unicornviews import UnicornFilteredListView, UnicornViewPermissionMixin

logger = logging.getLogger(__name__)


class MoviesView(UnicornViewPermissionMixin, UnicornFilteredListView):
    permission_required = 'movies_app.view_movie'

    # FilteredMixin
    _filtering_name = "my_filter"
    my_filter = ""

    # # UnicornFilteredListView
    model = Movie
    # how you want the list of object to be called in the context
    context_object_name = 'movies'
    # # MultipleObjectMixin pagination
    paginate_by = 15
    ordering = '-title'

    def filter(self):
        # filtering on some Movie attributes
        _filtering_value = getattr(self, self._filtering_name, '')
        if len(_filtering_value) > 0:
            _filter = Q(title__contains=_filtering_value) | Q(genre__contains=_filtering_value) | \
                      Q(year__contains=_filtering_value)
            return _filter


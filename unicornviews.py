import logging

from django_unicorn.components import UnicornView
from django.views.generic.list import MultipleObjectMixin
from django.contrib.auth.mixins import PermissionRequiredMixin


class UnicornViewPermissionMixin(PermissionRequiredMixin, UnicornView):
    """Mixins Permission on a component"""
    permission_required = None

    def mount(self):
        if not self.has_permission():
            return self.handle_no_permission()
        super().mount()
        return

    def handle_no_permission(self):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied(self.get_permission_denied_message())


class UnicornFilteredListView(MultipleObjectMixin, UnicornView):
    """
    Merges MultipleObjectMixin, pagination, Unicorn and a filtered queryset
    """
    page_kwarg = 'page'
    page = 1
    _filtering_name = None

    def filter(self):
        # implement this with django.db.models.Q
        raise NotImplementedError

    def get_queryset(self):
        queryset = super().get_queryset()
        _filter = self.filter()
        if _filter:
            queryset = queryset.filter(_filter)
        logging.debug(f"Filters: {queryset.count()}")
        return queryset

    def updated(self, name, value):
        super().updated(name, value)
        # logger.info(f"Updated called - {name=} {value=}")
        if name == self._filtering_name:
            # reset pagination
            setattr(self, self.page_kwarg, 1)
        elif name == self.page_kwarg:
            self.kwargs[self.page_kwarg] = getattr(self, self.page_kwarg, 1)

    def get_context_data(self, **kwargs):
        # 1. force kwargs.object_list for super().get_context_data
        # 2. force self.kwargs.get(page_kwarg) so you don't have to rewrite paginate_queryset
        self.kwargs[self.page_kwarg] = getattr(self, self.page_kwarg, 1)
        return super().get_context_data(object_list=self.get_queryset(), **kwargs)

    class Meta:
        # ignore all members pushed by MultipleObjectMixin
        exclude = ('model', 'ordering', 'queryset', 'paginator_class', 'paginate_by', 'page',
                   'allow_empty', 'context_object_name', 'paginate_orphans', 'page_kwarg', )


from datetime import datetime

from django.utils.translation import gettext_lazy as _
from django.contrib.admin import SimpleListFilter


class GSoCYearFilter(SimpleListFilter):
    """
    Custom filter made for HiddenUserProfileAdmin which sets up a
    GSoC year filter with the current year as default value.
    """
    title = _("GSoC year")
    parameter_name = 'gsoc_year'

    def lookups(self, request, model_admin):
        current_year = datetime.now().year
        year_list = [('All', _('All')), (None, _(str(current_year)))]

        for year in range(current_year - 1, 2004, -1):
            year_list.append((str(year), _(str(year))))

        return tuple(year_list)

    def choices(self, changelist):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': changelist.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() is None:                    # current year selected
            return queryset.filter(gsoc_year__gsoc_year=datetime.now().year)
        elif self.value() == 'All':                 # all year selected
            return queryset
        # specific year selected
        return queryset.filter(gsoc_year__gsoc_year=self.value())

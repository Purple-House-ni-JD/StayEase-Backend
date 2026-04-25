import django_filters
from django.db.models import Q
from .models import Room


class RoomFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category', lookup_expr='exact')
    min_price = django_filters.NumberFilter(field_name='price_per_night', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price_per_night', lookup_expr='lte')
    guests = django_filters.NumberFilter(field_name='max_guest', lookup_expr='gte')
    is_featured = django_filters.BooleanFilter(field_name='is_featured')
    available = django_filters.BooleanFilter(field_name='availability_status')

    # Date availability — used together: ?check_in=YYYY-MM-DD&check_out=YYYY-MM-DD
    check_in = django_filters.DateFilter(method='filter_by_dates')
    check_out = django_filters.DateFilter(method='filter_by_dates')

    class Meta:
        model = Room
        fields = ['category', 'min_price', 'max_price', 'guests', 'is_featured', 'available']

    def filter_by_dates(self, queryset, name, value):
        """
        Exclude rooms that have a confirmed/pending booking overlapping the
        requested check_in / check_out window.
        Only applied when BOTH check_in and check_out are provided.
        """
        check_in = self.data.get('check_in')
        check_out = self.data.get('check_out')

        if not (check_in and check_out):
            return queryset

        # Overlap condition: existing booking starts before requested end
        # AND existing booking ends after requested start
        booked_room_ids = (
            Room.objects.filter(
                bookingroom__booking__status__in=['pending', 'confirmed'],
                bookingroom__booking__check_in__lt=check_out,
                bookingroom__booking__check_out__gt=check_in,
            )
            .values_list('id', flat=True)
            .distinct()
        )

        return queryset.exclude(id__in=booked_room_ids)
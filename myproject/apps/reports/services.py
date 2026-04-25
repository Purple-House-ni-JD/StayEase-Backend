from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils import timezone
from datetime import timedelta

from apps.bookings.models import Booking, BookingRoom
from apps.payments.models import Payment
from apps.rooms.models import Room


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _trunc_fn(period: str):
    return {'daily': TruncDay, 'weekly': TruncWeek, 'monthly': TruncMonth}[period]


def _date_range(period: str, reference_date=None):
    """Return (start, end) for the requested period relative to reference_date."""
    today = reference_date or timezone.now().date()
    if period == 'daily':
        return today, today + timedelta(days=1)
    if period == 'weekly':
        start = today - timedelta(days=today.weekday())  # Monday
        return start, start + timedelta(days=7)
    if period == 'monthly':
        from datetime import date
        import calendar
        last_day = calendar.monthrange(today.year, today.month)[1]
        return date(today.year, today.month, 1), date(today.year, today.month, last_day)
    raise ValueError(f"Unknown period: {period}")


# ---------------------------------------------------------------------------
# Revenue report
# ---------------------------------------------------------------------------

def revenue_report(period: str, year: int = None, month: int = None):
    """
    Aggregate paid payment amounts grouped by the requested period.

    Returns a list of dicts: [{period_label, total_revenue, booking_count}]
    """
    trunc = _trunc_fn(period)
    qs = (
        Payment.objects
        .filter(status='paid')
        .annotate(period=trunc('paid_at'))
        .values('period')
        .annotate(
            total_revenue=Sum('amount'),
            booking_count=Count('id'),
        )
        .order_by('period')
    )

    # Optional year/month filters
    if year:
        qs = qs.filter(paid_at__year=year)
    if month:
        qs = qs.filter(paid_at__month=month)

    return [
        {
            'period': entry['period'].strftime('%Y-%m-%d') if entry['period'] else None,
            'total_revenue': float(entry['total_revenue'] or 0),
            'booking_count': entry['booking_count'],
        }
        for entry in qs
    ]


# ---------------------------------------------------------------------------
# Occupancy report
# ---------------------------------------------------------------------------

def occupancy_report(period: str, reference_date=None):
    """
    Occupancy rate per room category for the given period.

    occupancy_rate = bookings_count / total_rooms_in_category * 100
    """
    start, end = _date_range(period, reference_date)

    # Bookings active during the window (overlap logic)
    active_bookings = (
        BookingRoom.objects
        .filter(
            booking__status__in=['confirmed', 'completed'],
            booking__check_in__lt=end,
            booking__check_out__gt=start,
        )
        .select_related('room')
    )

    # Count by category
    category_counts = {}
    for br in active_bookings:
        cat = br.room.category
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # Total rooms per category
    total_by_cat = {
        item['category']: item['count']
        for item in Room.objects.values('category').annotate(count=Count('id'))
    }

    result = []
    for category, display in Room.CATEGORY_CHOICES:
        total = total_by_cat.get(category, 0)
        booked = category_counts.get(category, 0)
        result.append({
            'category': category,
            'category_display': display,
            'total_rooms': total,
            'booked_rooms': booked,
            'occupancy_rate': round((booked / total * 100) if total else 0, 2),
        })

    return result


# ---------------------------------------------------------------------------
# Top rooms report
# ---------------------------------------------------------------------------

def top_rooms_report(limit: int = 10, order_by: str = 'revenue'):
    """
    Top rooms ranked by revenue or booking count.
    order_by: 'revenue' | 'bookings'
    """
    qs = (
        BookingRoom.objects
        .filter(booking__status__in=['confirmed', 'completed'])
        .values('room__id', 'room__name', 'room__category')
        .annotate(
            total_revenue=Sum('price_snapshot'),
            booking_count=Count('id'),
        )
    )

    if order_by == 'revenue':
        qs = qs.order_by('-total_revenue')
    else:
        qs = qs.order_by('-booking_count')

    return [
        {
            'room_id': entry['room__id'],
            'room_name': entry['room__name'],
            'category': entry['room__category'],
            'total_revenue': float(entry['total_revenue'] or 0),
            'booking_count': entry['booking_count'],
        }
        for entry in qs[:limit]
    ]


# ---------------------------------------------------------------------------
# Dashboard summary
# ---------------------------------------------------------------------------

def dashboard_summary():
    """Summary cards for the admin dashboard."""
    today = timezone.now().date()
    month_start = today.replace(day=1)

    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    confirmed_bookings = Booking.objects.filter(status='confirmed').count()
    cancelled_bookings = Booking.objects.filter(status='cancelled').count()

    total_revenue = Payment.objects.filter(status='paid').aggregate(
        total=Sum('amount')
    )['total'] or 0

    monthly_revenue = Payment.objects.filter(
        status='paid',
        paid_at__date__gte=month_start
    ).aggregate(total=Sum('amount'))['total'] or 0

    available_rooms = Room.objects.filter(availability_status=True).count()
    total_rooms = Room.objects.count()

    checkins_today = Booking.objects.filter(
        check_in=today,
        status__in=['confirmed', 'completed']
    ).count()

    checkouts_today = Booking.objects.filter(
        check_out=today,
        status__in=['confirmed', 'completed']
    ).count()

    return {
        'bookings': {
            'total': total_bookings,
            'pending': pending_bookings,
            'confirmed': confirmed_bookings,
            'cancelled': cancelled_bookings,
        },
        'revenue': {
            'total': float(total_revenue),
            'this_month': float(monthly_revenue),
        },
        'rooms': {
            'total': total_rooms,
            'available': available_rooms,
        },
        'today': {
            'check_ins': checkins_today,
            'check_outs': checkouts_today,
        },
    }
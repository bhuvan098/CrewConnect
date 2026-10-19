import calendar
from datetime import date
from urllib.request import urlopen

from django import forms
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from hr.models import Leave

User = get_user_model()

GOOGLE_HOLIDAY_FEED = "https://calendar.google.com/calendar/ical/en.indian%23holiday%40group.v.calendar.google.com/public/basic.ics"


def get_public_holidays(year):
    cache_key = f"public_holidays_{year}"
    cached_holidays = cache.get(cache_key)
    if cached_holidays is not None:
        return cached_holidays
    holidays = {}
    try:
        with urlopen(GOOGLE_HOLIDAY_FEED, timeout=3) as response:
            lines = response.read().decode("utf-8").replace("\r\n ", "").splitlines()
        holiday_date = None
        holiday_name = None
        for line in lines:
            if line.startswith("DTSTART"):
                value = line.rsplit(":", 1)[1][:8]
                holiday_date = date(int(value[:4]), int(value[4:6]), int(value[6:8]))
            elif line.startswith("SUMMARY:"):
                holiday_name = line.removeprefix("SUMMARY:")
            elif line == "END:VEVENT" and holiday_date and holiday_name and holiday_date.year == year:
                name = holiday_name.lower()
                if "gandhi" not in name and "eid al-adha" not in name and "bakrid" not in name:
                    holidays[holiday_date] = holiday_name
                holiday_date = None
                holiday_name = None
    except (OSError, ValueError):
        pass
    cache.set(cache_key, holidays, 86400)
    return holidays


def set_password(request, uidb64, token):
    uid = urlsafe_base64_decode(uidb64).decode()
    user = User.objects.filter(pk=uid).first()
    if user is None or not default_token_generator.check_token(user, token):
        return render(request, "invalid_link.html")
    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("set_password", uidb64=uidb64, token=token)
        user.set_password(password)
        user.save()
        messages.success(request, "Password created successfully. You can now login.")
        return redirect("login")
    return render(request, "set_password.html")


@login_required
def employee_dashboard(request):
    return render(request, "employee_dashboard.html", {"employee": request.user.employee, "is_employee": True})


@login_required
def employee_profile(request):
    return render(request, "profile.html", {"employee": request.user.employee, "is_employee": True})


@login_required
def apply_leave(request):
    employee = request.user.employee
    if request.method == "POST":
        Leave.objects.create(
            employee=employee,
            leave_type=request.POST.get("leave_type"),
            start_date=request.POST.get("start_date"),
            end_date=request.POST.get("end_date"),
            reason=request.POST.get("reason"),
        )
        messages.success(request, "Leave application submitted successfully.")
        return redirect("my_leaves")
    return render(request, "apply_leave.html", {"leave_types": Leave.LEAVE_TYPES, "is_employee": True})


@login_required
def my_leaves(request):
    employee = request.user.employee
    leaves = Leave.objects.filter(employee=employee).order_by("-applied_date")
    return render(request, "my_leaves.html", {"leaves": leaves, "is_employee": True})


class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ("leave_type", "start_date", "end_date", "reason")
        widgets = {
            "leave_type": forms.Select(attrs={"class": "form-select"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "reason": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("start_date") and cleaned.get("end_date") and cleaned["end_date"] < cleaned["start_date"]:
            self.add_error("end_date", "End date cannot be before the start date.")
        return cleaned


@login_required
def leave_calendar(request):
    today = date.today()
    year_value = request.GET.get("year", "")
    month_value = request.GET.get("month", "")
    year = int(year_value) if year_value.isdigit() and 1 <= int(year_value) <= 9999 else today.year
    month = int(month_value) if month_value.isdigit() and 1 <= int(month_value) <= 12 else today.month
    displayed = date(year, month, 1)
    next_month = date(displayed.year + (displayed.month == 12), 1 if displayed.month == 12 else displayed.month + 1, 1)
    previous_month = date(displayed.year - (displayed.month == 1), 12 if displayed.month == 1 else displayed.month - 1, 1)
    leaves = request.user.employee.leaves.filter(start_date__lt=next_month, end_date__gte=displayed).exclude(status="Rejected")
    public_holidays = get_public_holidays(displayed.year)
    weeks = []
    for week in calendar.Calendar(firstweekday=6).monthdatescalendar(displayed.year, displayed.month):
        weeks.append([
            {
                "date": day,
                "in_month": day.month == displayed.month,
                "is_weekend": day.weekday() >= 5,
                "holiday_name": public_holidays.get(day),
                "leaves": [leave for leave in leaves if leave.start_date <= day <= leave.end_date],
            }
            for day in week
        ])
    return render(request, "leave_calendar.html", {"is_employee": True, "weeks": weeks, "month_name": displayed.strftime("%B %Y"), "previous_month": previous_month, "next_month": next_month})


@login_required
def leave_edit(request, pk):
    leave = get_object_or_404(Leave, pk=pk, employee=request.user.employee, status="Pending")
    form = LeaveForm(request.POST or None, instance=leave)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Leave request updated.")
        return redirect("my_leaves")
    return render(request, "leave_form.html", {"form": form, "title": "Edit Leave Request", "is_employee": True})


@login_required
@require_POST
def leave_delete(request, pk):
    leave = get_object_or_404(Leave, pk=pk, employee=request.user.employee, status="Pending")
    leave.delete()
    messages.success(request, "Leave request deleted.")
    return redirect("my_leaves")

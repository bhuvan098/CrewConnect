from django.urls import path

from . import views

urlpatterns = [
    path("set_password/<uidb64>/<token>/", views.set_password, name="set_password"),
    path("dashboard/", views.employee_dashboard, name="employee_dashboard"),
    path("profile/", views.employee_profile, name="my_profile"),
    path("apply-leave/", views.apply_leave, name="apply_leave"),
    path("my-leaves/", views.my_leaves, name="my_leaves"),
    path("leave-calendar/", views.leave_calendar, name="leave_calendar"),
    path("leaves/<int:pk>/edit/", views.leave_edit, name="leave_edit"),
    path("leaves/<int:pk>/delete/", views.leave_delete, name="leave_delete"),
]

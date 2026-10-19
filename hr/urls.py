from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
    path("employees/", views.viewemployees, name="employee_list"),
    path("employees/create/", views.employee_create, name="employee_create"),
    path("employees/<int:id>/", views.employee_detail, name="employee_detail"),
    path("employees/<int:id>/edit/", views.employee_update, name="employee_update"),
    path("employees/<int:id>/delete/", views.employee_delete, name="employee_delete"),
    path("leave-approve/", views.leave_approve, name="leave_approve"),
    path("leave/<int:id>/action/", views.leave_action, name="leave_action"),
    path("departments/", views.department_list, name="department_list"),
    path("departments/add/", views.department_add, name="department_add"),
    path("departments/<int:pk>/edit/", views.department_edit, name="department_edit"),
    path("departments/<int:pk>/delete/", views.department_delete, name="department_delete"),
    path("designations/", views.designation_list, name="designation_list"),
    path("designations/add/", views.designation_add, name="designation_add"),
    path("designations/<int:pk>/edit/", views.designation_edit, name="designation_edit"),
    path("designations/<int:pk>/delete/", views.designation_delete, name="designation_delete"),
]

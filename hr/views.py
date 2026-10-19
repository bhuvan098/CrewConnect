from django.conf import settings
from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from .models import Department, Designation, Employee, Leave


def login_view(request):
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get("username"), password=request.POST.get("password"))
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect("dashboard")
            if Employee.objects.filter(user=user).exists():
                return redirect("employee_dashboard")
            return redirect("login")
        return render(request, "login.html", {"error": "Invalid username or password"})
    return render(request, "login.html")


@login_required
@never_cache
def dashboard(request):
    return render(request, "dashboard.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
@never_cache
def viewemployees(request):
    employees = Employee.objects.select_related("department", "designation")
    return render(request, "employee_list.html", {"employees": employees})


@login_required
@never_cache
def employee_create(request):
    departments, designations = Department.objects.all(), Designation.objects.all()
    if request.method == "POST":
        email = request.POST.get("email")
        if Employee.objects.filter(email=email).exists():
            messages.error(request, "Employee with this email already exists.")
            return redirect("employee_create")
        user = User.objects.create_user(username=email, email=email, first_name=request.POST.get("name"))
        user.set_unusable_password(); user.save()
        employee = Employee.objects.create(user=user, employee_id=request.POST.get("employee_id"), name=request.POST.get("name"), email=email, phone=request.POST.get("phone"), department_id=request.POST.get("department"), designation_id=request.POST.get("designation"), joining_date=request.POST.get("joining_date"), employment_type=request.POST.get("employment_type"), salary=request.POST.get("salary"), address=request.POST.get("address"), status=request.POST.get("status") == "on")
        uid, token = urlsafe_base64_encode(force_bytes(user.pk)), default_token_generator.make_token(user)
        setup_link = request.build_absolute_uri(reverse("set_password", kwargs={"uidb64": uid, "token": token}))
        send_mail("CrewConnect - Set Your Password", f"Hello {employee.name},\n\nSet your CrewConnect password:\n{setup_link}", settings.DEFAULT_FROM_EMAIL, [email])
        return redirect("employee_list")
    return render(request, "employee_add_update.html", {"departments": departments, "designations": designations, "employment_types": Employee.EMPLOYMENT_TYPES, "is_update": False})


@login_required
@never_cache
def employee_detail(request, id):
    return render(request, "employee_detail.html", {"employee": get_object_or_404(Employee.objects.select_related("department", "designation"), id=id)})


@login_required
@never_cache
def employee_update(request, id):
    employee = get_object_or_404(Employee, id=id)
    if request.method == "POST":
        employee.employee_id, employee.name, employee.email = request.POST.get("employee_id"), request.POST.get("name"), request.POST.get("email")
        employee.phone, employee.department_id, employee.designation_id = request.POST.get("phone"), request.POST.get("department"), request.POST.get("designation")
        employee.joining_date, employee.employment_type, employee.salary, employee.address = request.POST.get("joining_date"), request.POST.get("employment_type"), request.POST.get("salary"), request.POST.get("address")
        employee.status = request.POST.get("status") == "on"; employee.save()
        return redirect("employee_list")
    return render(request, "employee_add_update.html", {"employee": employee, "departments": Department.objects.all(), "designations": Designation.objects.all(), "employment_types": Employee.EMPLOYMENT_TYPES, "is_update": True})


@login_required
@require_POST
def employee_delete(request, id):
    employee = get_object_or_404(Employee, id=id)
    employee.delete()
    return redirect("employee_list")


@login_required
def leave_approve(request):
    leaves = Leave.objects.select_related("employee", "employee__department", "employee__designation").order_by("-applied_date")
    return render(request, "leave_approval.html", {"leaves": leaves, "is_employee": False})


@login_required
def leave_action(request, id):
    if request.method == "POST":
        leave = get_object_or_404(Leave, id=id)
        if request.POST.get("action") == "approve": leave.status = "Approved"; leave.save()
        elif request.POST.get("action") == "reject": leave.status = "Rejected"; leave.save()
    return redirect("leave_approve")


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ("name",)
        widgets = {"name": forms.TextInput(attrs={"class": "form-control", "autofocus": True})}


class DesignationForm(forms.ModelForm):
    class Meta:
        model = Designation
        fields = ("name",)
        widgets = {"name": forms.TextInput(attrs={"class": "form-control", "autofocus": True})}


def management_list(request, model, title, add_name, edit_name, delete_name):
    return render(request, "management_list.html", {"items": model.objects.order_by("name"), "title": title, "add_name": add_name, "edit_name": edit_name, "delete_name": delete_name})


def management_form(request, form_class, instance, title, list_name):
    form = form_class(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{title} saved.")
        return redirect(list_name)
    return render(request, "management_form.html", {"form": form, "title": title, "list_name": list_name})


@login_required
def department_list(request):
    return management_list(request, Department, "Departments", "department_add", "department_edit", "department_delete")


@login_required
def department_add(request):
    return management_form(request, DepartmentForm, None, "Add Department", "department_list")


@login_required
def department_edit(request, pk):
    return management_form(request, DepartmentForm, get_object_or_404(Department, pk=pk), "Edit Department", "department_list")


@login_required
@require_POST
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if department.employee_set.exists():
        messages.error(request, "This department has employees assigned and cannot be deleted.")
    else:
        department.delete()
        messages.success(request, "Department deleted.")
    return redirect("department_list")


@login_required
def designation_list(request):
    return management_list(request, Designation, "Designations", "designation_add", "designation_edit", "designation_delete")


@login_required
def designation_add(request):
    return management_form(request, DesignationForm, None, "Add Designation", "designation_list")


@login_required
def designation_edit(request, pk):
    return management_form(request, DesignationForm, get_object_or_404(Designation, pk=pk), "Edit Designation", "designation_list")


@login_required
@require_POST
def designation_delete(request, pk):
    designation = get_object_or_404(Designation, pk=pk)
    if designation.employee_set.exists():
        messages.error(request, "This designation has employees assigned and cannot be deleted.")
    else:
        designation.delete()
        messages.success(request, "Designation deleted.")
    return redirect("designation_list")

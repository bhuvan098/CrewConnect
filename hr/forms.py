from django import forms

from .models import Employee


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            "employee_id", "name", "email", "phone", "department", "designation",
            "joining_date", "employment_type", "salary", "address", "status",
        ]
        widgets = {
            "joining_date": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
        }


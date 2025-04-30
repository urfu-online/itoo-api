from django.contrib import admin
from .models import CohortRule

@admin.register(CohortRule)
class CohortRuleAdmin(admin.ModelAdmin):
    list_display = (
        "course_id", 
        "target_cohort_name", 
        "email_domain", 
        "provider", 
        "is_active"
    )
    search_fields = ("course_id", "target_cohort_name")
    list_filter = ("is_active", "provider")
    fieldsets = (
        (None, {
            "fields": ("course_id", "is_active")
        }),
        ("Настройки когорты", {
            "fields": ("target_cohort_name", "email_domain", "provider", "forbidden_cohorts")
        }),
    )
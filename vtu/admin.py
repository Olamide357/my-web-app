from django.contrib import admin

# Register your models here.
from .models import DataPlan, TVPlan

@admin.register(DataPlan)
class DataPlanAdmin(admin.ModelAdmin):
    list_display = ("network", "plan_name", "volume", "validity", "amount")
    list_filter = ("network",)
    search_fields = ("plan_name", "plan_code")

@admin.register(TVPlan)
class TVPlanAdmin(admin.ModelAdmin):
    list_display = ("plan_name", "provider", "plan_code", "amount")   # show in admin table
    list_filter = ("provider",)   # filter sidebar by provider (DSTV, GOTV, Startimes)
    search_fields = ("plan_name", "plan_code")   # add search box
    ordering = ("provider", "amount")

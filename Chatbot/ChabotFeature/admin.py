from django.contrib import admin
from .models import UserProfile, SymptomLog, Flow, FlowStep, FlowOption, UserResponse
import nested_admin

# Inline classes for related models
class SymptomLogInline(nested_admin.NestedStackedInline):
    model = SymptomLog
    extra = 1

class FlowStepInline(nested_admin.NestedStackedInline):
    model = FlowStep
    extra = 1
    show_change_link = True

class FlowOptionInline(nested_admin.NestedStackedInline):
    model = FlowOption
    extra = 1
    fk_name = 'step'

class UserResponseInline(nested_admin.NestedStackedInline):
    model = UserResponse
    extra = 1

# Admin classes
class UserProfileAdmin(nested_admin.NestedModelAdmin):
    inlines = [SymptomLogInline, UserResponseInline]
    list_display = ['user', 'period_start_date']

class FlowAdmin(nested_admin.NestedModelAdmin):
    inlines = [FlowStepInline]
    list_display = ['name', 'description']

class FlowStepAdmin(nested_admin.NestedModelAdmin):
    inlines = [FlowOptionInline]
    list_display = ['flow', 'step_number', 'text', 'is_final_step']

class FlowOptionAdmin(nested_admin.NestedModelAdmin):
    list_display = ['step', 'text']

# Registering models with nested admin
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Flow, FlowAdmin)
admin.site.register(FlowStep, FlowStepAdmin)
admin.site.register(FlowOption, FlowOptionAdmin)

# Optionally registering these separately
admin.site.register(SymptomLog)
admin.site.register(UserResponse)

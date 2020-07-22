from django.contrib import admin

from .models import Hvac, Command

class CommandAdmin(admin.ModelAdmin):
    list_filter = ['date_issued', 'mode', 'target_temperature']
    list_display = ('mode', 'fan_speed', 'target_temperature', 'date_issued')
    fieldsets = [
        (None, {'fields': ['mode']}),
        ('Command Detail', {'fields': ['target_temperature', 'fan_speed'], 'classes': ['']}),
        ('Date information', {'fields': ['date_issued'], 'classes': ['']}),
    ]

admin.site.register(Hvac)
admin.site.register(Command, CommandAdmin)

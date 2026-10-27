from django.contrib import admin
from .models import TelegramBot, MessageTemplate, Activity, UserPreference


@admin.register(TelegramBot)
class TelegramBotAdmin(admin.ModelAdmin):
    list_display = ("name", "username", "is_active", "created_at")
    # Token deliberately omitted from list display.
    
@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "updated_at")
admin.site.register(Activity)
admin.site.register(UserPreference)

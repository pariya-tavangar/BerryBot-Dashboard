from django.contrib import admin
from django.urls import path
from berryapp import views

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.dashboard, name="dashboard"),
    path("bots/", views.bots, name="bots"),
    path("bots/<int:bot_id>/delete/", views.delete_bot, name="delete_bot"),

    path("bots/<int:bot_id>/", views.bot_detail, name="bot_detail"),
    path("bots/<int:bot_id>/toggle/", views.toggle_bot_status, name="toggle_bot_status"),
    
    path("messages/", views.messages_page, name="messages"),
    path("messages/send/", views.send_message, name="send_message"),
    path("reactions/", views.reactions_page, name="reactions"),
    path("reactions/apply/", views.apply_reaction, name="apply_reaction"),

    path("bots/<int:bot_id>/check/",views.check_bot_connection,name="check_bot_connection"),

    path("customization/", views.customization, name="customization"),
    path("settings/", views.settings_page, name="settings"),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

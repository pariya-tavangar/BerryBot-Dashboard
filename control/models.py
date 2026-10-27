from django.db import models

class TelegramBot(models.Model):
    
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, blank=True)
    token = models.CharField(max_length=255)

    profile_image = models.ImageField(
        upload_to="bot_profiles/",
        blank=True,
        null=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_checked = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.name

class MessageTemplate(models.Model):
    name = models.CharField(max_length=100)
    body = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class Activity(models.Model):
    kind = models.CharField(max_length=30, default="note")
    text = models.CharField(max_length=240)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return self.text

class UserPreference(models.Model):
    theme = models.CharField(max_length=30, default="strawberry")
    display_name = models.CharField(max_length=100, default="Berry")
    compact_mode = models.BooleanField(default=False)
    animations = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return "Dashboard preferences"

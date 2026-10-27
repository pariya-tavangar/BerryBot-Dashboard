import json
import requests
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import TelegramBot, MessageTemplate, Activity, UserPreference

from .utils import fetch_bot_profile_image

def get_prefs():
    pref, _ = UserPreference.objects.get_or_create(pk=1)
    return pref


def log_activity(kind, text):
    Activity.objects.create(kind=kind, text=text)


def base_context(active):
    return {"active": active, "bots": TelegramBot.objects.all().order_by("-created_at"),
            "prefs": get_prefs(), "bot_count": TelegramBot.objects.count()}


def dashboard(request):
    ctx = base_context("dashboard")
    ctx.update({"templates": MessageTemplate.objects.order_by("-updated_at")[:4],
                "activities": Activity.objects.all()[:6],
                "active_bots": TelegramBot.objects.filter(is_active=True).count(),
                "sent_count": Activity.objects.filter(kind="sent").count()})
    return render(request, "control/dashboard.html", ctx)


def bots(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        token = request.POST.get("token", "").strip()
        if not name or not token:
            messages.error(request, "Add a name and API token to continue.")
        else:
            try:
                response = requests.get(
                    f"https://api.telegram.org/bot{token}/getMe",
                    timeout=12,)

                data = response.json()
                if response.ok and data.get("ok"):
                    info = data["result"]
                    bot = TelegramBot.objects.create(name=name, username=info.get("username", ""), token=token)
                    fetch_bot_profile_image(bot)
                    log_activity("bot", f"Connected @{bot.username or bot.name}")
                    messages.success(request, f"Connected @{info.get('username', name)} successfully!")
                else:
                    messages.error(request, "Telegram could not validate this token. Check it with BotFather.")
            except (requests.RequestException, ValueError):
                messages.error(request, "Could not reach Telegram. Check your connection and try again.")
        return redirect("bots")
    
    ctx = base_context("bots")
    ctx["bot_list"] = ctx["bots"]
    return render(request, "control/bots.html", ctx)


@require_POST
def delete_bot(request, bot_id):
    bot = get_object_or_404(TelegramBot, pk=bot_id)
    name = bot.name
    bot.delete()
    log_activity("bot", f"Removed {name}")
    messages.success(request, f"{name} was removed.")
    return redirect("bots")


def messages_page(request):
    if request.method == "POST":
        name = request.POST.get("template_name", "").strip()
        body = request.POST.get("body", "").strip()
        if name and body:
            MessageTemplate.objects.create(name=name, body=body)
            log_activity("template", f"Saved template “{name}”")
            messages.success(request, "Your message template is saved.")
        else:
            messages.error(request, "Give your template a name and some text.")
        return redirect("messages")
    ctx = base_context("messages")
    ctx["templates"] = MessageTemplate.objects.order_by("-updated_at")
    return render(request,"control/messages.html", ctx)


@require_POST
def send_message(request):

    bot = get_object_or_404(TelegramBot, pk=request.POST.get("bot_id"))
    chat_id = request.POST.get("chat_id", "").strip()
    body = request.POST.get("body", "").strip()
    if not chat_id or not body:
        messages.error(request, "Choose a recipient and write a message first.")
        return redirect("messages")
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{bot.token}/sendMessage",
            json={"chat_id": chat_id, "text": body}, timeout=15)
        data = response.json()
        if response.ok and data.get("ok"):
            log_activity("sent", f"Sent a message with {bot.name} to {chat_id}")
            messages.success(request, "Message sent! ✨")
        else:
            messages.error(request, "Telegram could not send it: " + data.get("description", "unknown error"))
    except (requests.RequestException, ValueError):
        messages.error(request, "Could not reach Telegram. Please try again.")
    return redirect("messages")


def reactions_page(request):

    ctx = base_context("reactions")
    ctx["emoji_choices"] = ["💔", "🥰", "👍", "🔥", "✨", "🎉","👏", "🤍", "🌸","❤️‍🔥"]
    return render(request, "control/reactions.html", ctx)


@require_POST
def apply_reaction(request):
    
    bot = get_object_or_404(TelegramBot, pk=request.POST.get("bot_id"))
    chat_id = request.POST.get("chat_id", "").strip()
    message_id = request.POST.get("message_id", "").strip()
    emoji = request.POST.get("emoji", "❤️")
    
    if not chat_id or not message_id:
        messages.error(request, "Add both a chat ID and message ID.")
        return redirect("reactions")
    try:
        response = requests.post(
            f"https://api.telegram.org/bot{bot.token}/setMessageReaction",
            json={"chat_id": chat_id, "message_id": int(message_id),
                  "reaction": [{"type": "emoji", "emoji": emoji}], "is_big": False}, timeout=15)
        data = response.json()
        if response.ok and data.get("ok"):
            log_activity("reaction", f"Left {emoji} on message {message_id}")
            messages.success(request, f"Reaction {emoji} added!")
        else:
            messages.error(request, "Telegram could not add that reaction: " + data.get("description", "unknown error"))
    except (requests.RequestException, ValueError):
        messages.error(request, "Could not reach Telegram, or the message ID was invalid.")
    return redirect("reactions")


def customization(request):
    pref = get_prefs()
    if request.method == "POST":
        theme = request.POST.get("theme", "strawberry")
        pref.theme = theme if theme in {"strawberry", "lavender", "matcha", "midnight"} else "strawberry"
        pref.compact_mode = request.POST.get("compact_mode") == "on"
        pref.animations = request.POST.get("animations") == "on"
        pref.save()
        messages.success(request, "Your space is looking lovely. Preferences saved!")
        return redirect("customization")
    ctx = base_context("customization")
    return render(request, "control/customization.html", ctx)


def settings_page(request):
    pref = get_prefs()
    if request.method == "POST":
        pref.display_name = request.POST.get("display_name", "Berry").strip()[:100] or "Berry"
        pref.save()
        messages.success(request, "Settings saved.")
        return redirect("settings")
    ctx = base_context("settings")
    return render(request, "control/settings.html", ctx)
    

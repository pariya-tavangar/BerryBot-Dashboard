import requests
from django.core.files.base import ContentFile
from .models import TelegramBot


def fetch_bot_profile_image(bot_record: TelegramBot):
    """
    Fetch a bot's profile image from Telegram
    and save it to Django's media storage.
    """

    token = bot_record.token

    try:
        # 1. Get the bot's Telegram ID.
        me_response = requests.get(
            f"https://api.telegram.org/bot{token}/getMe",
            timeout=15
        )
        me_response.raise_for_status()

        me_data = me_response.json()

        if not me_data.get("ok"):
            return False

        bot_id = me_data["result"]["id"]

        # 2. Request profile photos for this bot.
        photos_response = requests.get(
            f"https://api.telegram.org/bot{token}/getUserProfilePhotos",
            params={
                "user_id": bot_id,
                "limit": 1,
            },
            timeout=15
        )
        photos_response.raise_for_status()

        photos_data = photos_response.json()

        if not photos_data.get("ok"):
            return False

        photos = photos_data["result"]["photos"]

        # No profile photo was returned.
        if not photos:
            return False

        # 3. Select the largest available version.
        photo_sizes = photos[0]

        largest_photo = max(
            photo_sizes,
            key=lambda photo: photo.get("file_size", 0)
        )

        file_id = largest_photo["file_id"]

        # 4. Retrieve the downloadable file path.
        file_response = requests.get(
            f"https://api.telegram.org/bot{token}/getFile",
            params={"file_id": file_id},
            timeout=15
        )
        file_response.raise_for_status()

        file_data = file_response.json()

        if not file_data.get("ok"):
            return False

        file_path = file_data["result"]["file_path"]

        # 5. Download the image.
        image_url = (
            f"https://api.telegram.org/file/bot{token}/{file_path}"
        )

        image_response = requests.get(
            image_url,
            timeout=30
        )
        image_response.raise_for_status()

        # 6. Save the image to Django media storage.
        filename = f"bot_{bot_record.pk}.jpg"

        bot_record.profile_image.save(
            filename,
            ContentFile(image_response.content),
            save=False
        )

        bot_record.save(update_fields=["profile_image"])

        return True

    except requests.RequestException:
        return False
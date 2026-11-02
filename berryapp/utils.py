import requests
from django.core.files.base import ContentFile
from .models import TelegramBot


def _telegram_result(response):
    data = response.json()
    if not isinstance(data, dict) or data.get("ok") is not True:
        return None

    result = data.get("result")
    return result if isinstance(result, dict) else None


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

        me_data = _telegram_result(me_response)
        if not me_data or me_data.get("id") is None:
            return False

        bot_id = me_data["id"]

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

        photos_data = _telegram_result(photos_response)
        if not photos_data:
            return False

        photos = photos_data.get("photos")

        # No profile photo was returned.
        if (
            not isinstance(photos, list)
            or not photos
            or not isinstance(photos[0], list)
            or not photos[0]
        ):
            return False

        # 3. Select the largest available version.
        photo_sizes = photos[0]

        largest_photo = max(
            photo_sizes,
            key=lambda photo: (
                photo.get("file_size", 0) if isinstance(photo, dict) else 0
            ),
        )
        if not isinstance(largest_photo, dict) or not largest_photo.get("file_id"):
            return False

        file_id = largest_photo["file_id"]

        # 4. Retrieve the downloadable file path.
        file_response = requests.get(
            f"https://api.telegram.org/bot{token}/getFile",
            params={"file_id": file_id},
            timeout=15
        )
        file_response.raise_for_status()

        file_data = _telegram_result(file_response)
        if not file_data:
            return False

        file_path = file_data.get("file_path")
        if not isinstance(file_path, str) or not file_path:
            return False

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

    except (requests.RequestException, ValueError):
        return False
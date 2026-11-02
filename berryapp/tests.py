from unittest.mock import Mock, patch

from django.test import TestCase
from django.urls import reverse

from berryapp.models import (
    Activity,
    MessageTemplate,
    TelegramBot,
    TelegramChat,
    UserPreference,
)
from berryapp.utils import fetch_bot_profile_image


def telegram_response(data, *, ok=True):
    response = Mock()
    response.ok = ok
    response.json.return_value = data
    return response


class DashboardViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        UserPreference.objects.create(pk=1)

    def test_dashboard_renders(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_limits_bot_rows_and_uses_six_queries(self):
        TelegramBot.objects.bulk_create(
            [TelegramBot(name=f"Bot {index}", token="token") for index in range(10)]
        )

        with self.assertNumQueries(6):
            response = self.client.get(reverse("dashboard"))

        self.assertEqual(len(response.context["bots"]), 4)
        self.assertEqual(response.context["bot_count"], 10)

    def test_bot_list_pages_do_not_count_the_same_rows_again(self):
        TelegramBot.objects.create(name="Garden", token="token")

        with self.assertNumQueries(2):
            bots_response = self.client.get(reverse("bots"))
        with self.assertNumQueries(3):
            messages_response = self.client.get(reverse("messages"))
        with self.assertNumQueries(2):
            reactions_response = self.client.get(reverse("reactions"))

        self.assertEqual(bots_response.status_code, 200)
        self.assertEqual(messages_response.status_code, 200)
        self.assertEqual(reactions_response.status_code, 200)

    def test_all_pages_render_and_shared_scripts_load(self):
        page_names = (
            "dashboard",
            "bots",
            "messages",
            "reactions",
            "customization",
            "settings",
        )
        for page_name in page_names:
            with self.subTest(page=page_name):
                response = self.client.get(reverse(page_name))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'src="/static/js/base.js"')
                self.assertNotContains(response, "{ % static")

        self.assertContains(
            self.client.get(reverse("reactions")),
            'src="/static/js/scripts/reactions.js"',
        )

    def test_bot_page_reports_actual_active_count(self):
        TelegramBot.objects.create(name="Active", token="token")
        TelegramBot.objects.create(name="Paused", token="token", is_active=False)

        response = self.client.get(reverse("bots"))

        self.assertContains(response, '<div class="stat-number">1</div>')

    def test_message_template_is_saved_and_empty_template_is_rejected(self):
        response = self.client.post(
            reverse("messages"),
            {"template_name": "Greeting", "body": "Hello"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(MessageTemplate.objects.filter(name="Greeting").exists())

        response = self.client.post(
            reverse("messages"),
            {"template_name": " ", "body": ""},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(MessageTemplate.objects.count(), 1)

    def test_long_template_keeps_full_text_for_composer(self):
        body = "A" * 250
        MessageTemplate.objects.create(name="Long note", body=body)

        response = self.client.get(reverse("messages"))

        self.assertContains(response, f'data-template-body="{body}"')

    def test_reaction_default_matches_selected_emoji(self):
        response = self.client.get(reverse("reactions"))

        self.assertContains(response, 'data-emoji="💔">💔</button>')
        self.assertContains(response, 'id="chosen-emoji" value="💔"')

    @patch("berryapp.views.fetch_bot_profile_image", return_value=False)
    @patch("berryapp.views.requests.get")
    def test_bot_is_created_after_telegram_validation(
        self, mock_get, _mock_fetch_profile
    ):
        mock_get.return_value = telegram_response(
            {"ok": True, "result": {"id": 123, "username": "garden_bot"}}
        )

        response = self.client.post(
            reverse("bots"), {"name": "Garden", "token": "123:secret"}, follow=True
        )

        self.assertEqual(response.status_code, 200)
        bot = TelegramBot.objects.get()
        self.assertEqual(bot.username, "garden_bot")
        mock_get.assert_called_once()

    @patch("berryapp.views.fetch_bot_profile_image")
    @patch("berryapp.views.requests.get")
    def test_bot_is_not_created_from_malformed_telegram_result(
        self, mock_get, _mock_fetch_profile
    ):
        mock_get.return_value = telegram_response({"ok": True, "result": []})

        response = self.client.post(
            reverse("bots"), {"name": "Garden", "token": "123:secret"}, follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(TelegramBot.objects.exists())

    @patch("berryapp.views.requests.post")
    def test_send_message_updates_saved_chat_and_activity(self, mock_post):
        mock_post.return_value = telegram_response(
            {
                "ok": True,
                "result": {
                    "chat": {
                        "id": 123,
                        "type": "private",
                        "first_name": "Ada",
                        "username": "ada",
                    }
                },
            }
        )
        bot = TelegramBot.objects.create(name="Garden", token="token")

        response = self.client.post(
            reverse("send_message"),
            {"bot_id": bot.pk, "chat_id": "123", "body": "Hello"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(TelegramChat.objects.get().title, "Ada")
        self.assertEqual(Activity.objects.get().kind, "sent")

    @patch("berryapp.views.requests.post")
    def test_malformed_telegram_response_does_not_raise_server_error(self, mock_post):
        bot = TelegramBot.objects.create(name="Garden", token="token")

        for data in (
            ["unexpected"],
            {"ok": True, "result": []},
            {"ok": False, "description": []},
        ):
            with self.subTest(data=data):
                mock_post.return_value = telegram_response(data)
                response = self.client.post(
                    reverse("send_message"),
                    {"bot_id": bot.pk, "chat_id": "123", "body": "Hello"},
                    follow=True,
                )

                self.assertEqual(response.status_code, 200)
        self.assertFalse(Activity.objects.exists())

    def test_invalid_bot_id_returns_not_found(self):
        response = self.client.post(
            reverse("send_message"),
            {"bot_id": "not-a-number", "chat_id": "123", "body": "Hello"},
        )
        self.assertEqual(response.status_code, 404)

    @patch("berryapp.utils.requests.get")
    def test_profile_fetch_rejects_malformed_telegram_json(self, mock_get):
        mock_get.return_value = telegram_response(["unexpected"])
        bot = TelegramBot.objects.create(name="Garden", token="token")

        self.assertFalse(fetch_bot_profile_image(bot))
    @patch("berryapp.views.requests.post")
    def test_invalid_reaction_message_id_is_reported_without_api_call(self, mock_post):
        bot = TelegramBot.objects.create(name="Garden", token="token")

        response = self.client.post(
            reverse("apply_reaction"),
            {"bot_id": bot.pk, "chat_id": "123", "message_id": "invalid"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        mock_post.assert_not_called()
        self.assertContains(response, "message ID was invalid")

    @patch("berryapp.views.requests.post")
    def test_reaction_is_sent_and_logged(self, mock_post):
        mock_post.return_value = telegram_response({"ok": True})
        bot = TelegramBot.objects.create(name="Garden", token="token")

        response = self.client.post(
            reverse("apply_reaction"),
            {
                "bot_id": bot.pk,
                "chat_id": "123",
                "message_id": "42",
                "emoji": "🔥",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        mock_post.assert_called_once()
        self.assertEqual(Activity.objects.get().kind, "reaction")

    def test_settings_page_persists_preferences(self):
        response = self.client.post(
            reverse("settings"),
            {"display_name": "Strawberry Keeper"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        pref = UserPreference.objects.get(pk=1)
        self.assertEqual(pref.display_name, "Strawberry Keeper")

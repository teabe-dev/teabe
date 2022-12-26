from django.db.models import (BooleanField, CharField, DateTimeField,
                              DecimalField, ImageField, UUIDField)
from django.test import TestCase
from django.urls import resolve

from user.models import UserProfile
from user.views import Index


class TestUserProfileFieldType(TestCase):
    # 測試 資料庫型態
    def test_avatar_field_type(self):
        assert_same_type(self, "avatar", ImageField)

    def test_user_token_field_type(self):
        assert_same_type(self, "user_token", UUIDField)

def assert_same_type(self, field_name, field_type):
    self.assertTrue(
        isinstance(
            get_UserProfile_field(field_name),
            field_type
        )
    )

def get_UserProfile_field(field_name):
    return UserProfile._meta.get_field(field_name)


class TestUserPageView(TestCase):
    # 測試 網頁回應
    def test_reachable_user(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_template_user(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'base.html')
		# 期望這頁面的 template 是 base.html 這個檔案


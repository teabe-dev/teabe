import json
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from share.enums import MemberRole

# Create your models here.

class CustomJSONField(models.JSONField):
    ''' json 的 Field'''
    def get_prep_value(self, value):
        if value is None:
            return value
        return json.dumps(value, ensure_ascii=False)


class ShareGroup(models.Model):
    title = models.CharField(max_length=20, verbose_name='標題')
    token = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='授權碼')
    create_time = models.DateTimeField(default=timezone.now, verbose_name='建立時間')
    update_time = models.DateTimeField(default=timezone.now, verbose_name='更新時間')
    is_viewable = models.BooleanField(default=True, verbose_name='可檢視')
    is_apply = models.BooleanField(default=True, verbose_name='可申請')

    class Meta:
        verbose_name = "分寶群"
        verbose_name_plural = "分寶群"

    def __str__(self):
        return self.title


class ShareMember(models.Model):
    share_group = models.ForeignKey(ShareGroup, on_delete=models.CASCADE, verbose_name='分寶群')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='使用者')
    nick_name = models.CharField(default='', max_length=20, verbose_name='暱稱')
    introduce = models.CharField(default='', max_length=60, verbose_name='自我介紹')
    member_type = models.IntegerField(choices=MemberRole.choices(), default=MemberRole.AUDIT, verbose_name='成員類別')

    class Meta:
        verbose_name = "分寶群成員"
        verbose_name_plural = "分寶群成員"
    def __str__(self):
        return "{} | {}".format(self.share_group, self.nick_name)


class ShareGroupDetail(models.Model):
    share_group = models.ForeignKey(ShareGroup, on_delete=models.CASCADE, verbose_name='分寶群')
    item = models.CharField(max_length=20, verbose_name='項目')
    set_member = models.ForeignKey(ShareMember, on_delete=models.CASCADE, verbose_name='填表人', related_name='set_member')
    get_member = models.ForeignKey(ShareMember, on_delete=models.CASCADE, verbose_name='得寶人', related_name='get_member')
    share_members = models.ManyToManyField(ShareMember, verbose_name='分寶人', related_name='share_members')
    original_price = models.IntegerField(default=0, verbose_name='原始金額')
    share_price = models.IntegerField(default=0, verbose_name='平分金額')
    create_time = models.DateTimeField(default=timezone.now, verbose_name='建立時間')
    getting_time = models.DateTimeField(default=timezone.now, verbose_name='取得時間')
    update_time = models.DateTimeField(default=timezone.now, verbose_name='更新時間')
    extra = CustomJSONField(default=dict, blank=True, null=True, verbose_name='額外')

    class Meta:
        verbose_name = "分寶群明細表"
        verbose_name_plural = "分寶群明細表"
    def __str__(self):
        return "{} | {}".format(self.share_group, self.item)

class ShareGroupHistory(models.Model):
    share_group_detail = models.ForeignKey(ShareGroup, on_delete=models.CASCADE, verbose_name='分寶群明細表')
    item = models.CharField(max_length=20, verbose_name='項目')
    set_member = models.ForeignKey(ShareMember, on_delete=models.CASCADE, verbose_name='填表人', related_name='+')
    get_member = models.ForeignKey(ShareMember, on_delete=models.CASCADE, verbose_name='得寶人', related_name='+')
    share_members = models.ManyToManyField(ShareMember, verbose_name='分寶人', related_name='+')
    original_price = models.IntegerField(default=0, verbose_name='原始金額')
    share_price = models.IntegerField(default=0, verbose_name='平分金額')
    getting_time = models.DateTimeField(default=timezone.now, verbose_name='取得時間')
    create_time = models.DateTimeField(default=timezone.now, verbose_name='建立時間')

    class Meta:
        verbose_name = "分寶群紀錄表"
        verbose_name_plural = "分寶群紀錄表"

    def __str__(self):
        return "{}".format(self.item)

class UserDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='使用者')
    item = models.CharField(max_length=20, verbose_name='項目')
    price = models.IntegerField(default=0, verbose_name='金額')
    share_group_detail = models.ForeignKey(ShareGroup, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='分寶群明細表')
    remark = models.CharField(max_length=20, verbose_name='備註')
    getting_time = models.DateTimeField(default=timezone.now, verbose_name='取得時間')
    create_time = models.DateTimeField(default=timezone.now, verbose_name='建立時間')

    class Meta:
        verbose_name = "使用者明細表"
        verbose_name_plural = "使用者明細表"

    def __str__(self):
        return "{}".format(self.item)

class ShareStats(models.Model):
    share_group_detail = models.ForeignKey(ShareGroup, on_delete=models.CASCADE, verbose_name='分寶群明細表')
    out_member = models.ForeignKey(ShareMember, on_delete=models.CASCADE, verbose_name='待出帳者', related_name='out_member')
    in_member = models.ForeignKey(ShareMember, on_delete=models.CASCADE, verbose_name='待入帳者', related_name='in_member')
    price = models.IntegerField(default=0, verbose_name='金額')
    class Meta:
        verbose_name = "分寶統計表"
        verbose_name_plural = "分寶統計表"

    def __str__(self):
        return "{}".format(self.price)



from django.db import models
import uuid
from django.utils import timezone
from django.contrib.auth.models import User
from share.enums import MemberType

# Create your models here.

class ShareGroup(models.Model):
    title = models.CharField(max_length=20, verbose_name='標題')
    token = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name='授權碼')
    create_time = models.DateTimeField(default=timezone.now, verbose_name='建立時間')
    update_time = models.DateTimeField(default=timezone.now, verbose_name='更新時間')
    is_viewable = models.BooleanField(default=True, verbose_name='可檢視')
    class Meta:
        verbose_name = "分寶群"
        verbose_name_plural = "分寶群"

    def __str__(self):
        return self.title


class ShareMember(models.Model):
    share_group = models.ForeignKey(ShareGroup, on_delete=models.CASCADE, verbose_name='分寶群')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='使用者')
    nick_name = models.CharField(max_length=20, verbose_name='暱稱')
    member_type = models.IntegerField(choices=MemberType.choices(), default=MemberType.AUDIT, verbose_name='成員類別')

    class Meta:
        verbose_name = "分寶群成員"
        verbose_name_plural = "分寶群成員"
    def __str__(self):
        return "{} | {}".format(self.share_group, self.nick_name)


class ShareGroupDetail(models.Model):
    share_group = models.ForeignKey(ShareGroup, on_delete=models.CASCADE, verbose_name='分寶群')
    item = models.CharField(max_length=20, verbose_name='項目')
    set_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='填表人', related_name='set_user')
    get_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='得寶人', related_name='get_user')
    share_user = models.ManyToManyField(User, verbose_name='分寶人', related_name='share_user')
    original_price = models.IntegerField(default=0, verbose_name='原始金額')
    share_price = models.IntegerField(default=0, verbose_name='平分金額')
    create_time = models.DateTimeField(default=timezone.now, verbose_name='建立時間')
    update_time = models.DateTimeField(default=timezone.now, verbose_name='更新時間')

    class Meta:
        verbose_name = "分寶群明細表"
        verbose_name_plural = "分寶群明細表"
    def __str__(self):
        return "{} | {}".format(self.share_group, self.item)

class ShareGroupHistory(models.Model):
    share_group_detail = models.ForeignKey(ShareGroup, on_delete=models.CASCADE, verbose_name='分寶群明細表')
    item = models.CharField(max_length=20, verbose_name='項目')
    set_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='填表人', related_name='+')
    get_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='得寶人', related_name='+')
    share_user = models.ManyToManyField(User, verbose_name='分寶人', related_name='+')
    original_price = models.IntegerField(default=0, verbose_name='原始金額')
    share_price = models.IntegerField(default=0, verbose_name='平分金額')
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
    share_group_detail = models.ForeignKey(ShareGroup, on_delete=models.CASCADE, verbose_name='分寶群明細表')
    remark = models.CharField(max_length=20, verbose_name='備註')
    create_time = models.DateTimeField(default=timezone.now, verbose_name='建立時間')

    class Meta:
        verbose_name = "使用者明細表"
        verbose_name_plural = "使用者明細表"

    def __str__(self):
        return "{}".format(self.item)

class ShareStats(models.Model):
    out_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='待出帳者', related_name='out_user')
    in_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='待入帳者', related_name='in_user')
    price = models.IntegerField(default=0, verbose_name='金額')
    class Meta:
        verbose_name = "分寶統計表"
        verbose_name_plural = "分寶統計表"

    def __str__(self):
        return "{}".format(self.price)



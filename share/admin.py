from django.contrib import admin
from share import models
# Register your models here.

@admin.register(models.ShareGroup)
class ShareGroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'token', 'create_time', 'update_time', 'is_viewable')
    search_fields = ['is_viewable']  # 搜尋條件

@admin.register(models.ShareMember)
class ShareMemberAdmin(admin.ModelAdmin):
    list_display = ('share_group', 'user', 'nick_name', 'member_type')
    search_fields = ['share_group', 'member_type']  # 搜尋條件

@admin.register(models.ShareGroupDetail)
class ShareGroupDetailAdmin(admin.ModelAdmin):
    list_display = ('share_group', 'item', 'set_user', 'get_user', 'create_time', 'update_time')
    search_fields = ['share_group', 'item']  # 搜尋條件

@admin.register(models.ShareGroupHistory)
class ShareGroupHistoryAdmin(admin.ModelAdmin):
    list_display = ('share_group_detail', 'item', 'set_user', 'get_user', 'create_time')
    search_fields = ['share_group', 'item']  # 搜尋條件

@admin.register(models.UserDetail)
class UserDetailAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'price', 'remark')
    search_fields = ['user', 'item']  # 搜尋條件

@admin.register(models.ShareStats)
class ShareStatsAdmin(admin.ModelAdmin):
    list_display = ('out_user', 'in_user', 'price')
    search_fields = ['out_user']  # 搜尋條件


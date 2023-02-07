from django.contrib import admin
from share import models
# Register your models here.

@admin.register(models.ShareGroup)
class ShareGroupAdmin(admin.ModelAdmin):
    list_display = ('token', 'title', 'create_time', 'update_time', 'is_viewable', 'is_apply')
    search_fields = ['is_viewable']  # 搜尋條件
    list_editable = ('title', )

@admin.register(models.ShareMember)
class ShareMemberAdmin(admin.ModelAdmin):
    list_display = ('share_group', 'user', 'nick_name', 'member_type')
    search_fields = ['share_group', 'member_type']  # 搜尋條件
    raw_id_fields = ('user', 'share_group')

@admin.register(models.ShareGroupDetail)
class ShareGroupDetailAdmin(admin.ModelAdmin):
    list_display = ('share_group', 'item', 'set_user', 'get_user', 'getting_time', 'create_time', 'update_time')
    search_fields = ['share_group', 'item']  # 搜尋條件
    raw_id_fields = ('share_group', 'set_user', 'get_user')
    filter_horizontal = ('share_user', )

@admin.register(models.ShareGroupHistory)
class ShareGroupHistoryAdmin(admin.ModelAdmin):
    list_display = ('share_group_detail', 'item', 'set_user', 'get_user', 'getting_time', 'create_time')
    search_fields = ['share_group', 'item']  # 搜尋條件
    raw_id_fields = ('set_user', 'get_user',)
    filter_horizontal = ('share_user', )

@admin.register(models.UserDetail)
class UserDetailAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'price', 'share_group_detail', 'remark', 'getting_time')
    search_fields = ['user', 'item']  # 搜尋條件
    raw_id_fields = ('user',)

@admin.register(models.ShareStats)
class ShareStatsAdmin(admin.ModelAdmin):
    list_display = ('out_user', 'in_user', 'price')
    search_fields = ['out_user']  # 搜尋條件
    raw_id_fields = ('out_user', 'in_user',)


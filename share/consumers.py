import json
import zoneinfo

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.conf import settings

from share.models import ShareGroup, ShareGroupDetail, ShareMember, UserDetail, ShareStats
import uuid
paris_tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)


class ShareConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_name = self.scope['url_route']['kwargs']['group'] # = group token
        self.room_group_name = f"{self.room_name}"
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        json_data = json.loads(text_data)
        if json_data.get('is_group', False):
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': json_data['type'],
                    'message': json_data
                })
        else:
            await self.channel_layer.send(self.channel_name,
                {
                    'type': json_data['type'],
                    'message': json_data
                })

    async def members(self, json_data):
        data = await self.get_members(json_data)
        await self.send(text_data=json.dumps({'type': 'members', 'data': data}, ensure_ascii=False))

    @sync_to_async
    def get_members(self, json_data):
        share_group = ShareGroup.objects.get(token=self.room_name)
        data = {}
        for sharemember in share_group.sharemember_set.all():
            user_data = {
                'nick_name': sharemember.nick_name,
                'introduce': sharemember.introduce
            }

            if sharemember.user.userprofile.avatar:
                user_data['avatar'] = sharemember.user.userprofile.avatar.url
            else:
                user_data['avatar'] = f'https://secure.gravatar.com/avatar/{sharemember.user.userprofile.user_token.hex}?s=30&d=identicon'

            data[sharemember.id] = user_data
        return data

    async def table(self, json_data):
        data = await self.get_table(json_data)
        await self.send(text_data=json.dumps({'type': 'table', 'data': data}, ensure_ascii=False))

    @sync_to_async
    def get_table(self, json_data):
        share_group = ShareGroup.objects.get(token=self.room_name)
        group_detail = share_group.sharegroupdetail_set.all()

        result = []
        for groupDetail in group_detail[:1000]:
            groupDetail:ShareGroupDetail
            receipt_data = {
                'id': groupDetail.id,
                'get_member': groupDetail.get_member.nick_name,
                'set_member': groupDetail.set_member.nick_name,
                'item': groupDetail.item,
                'share_members': list(groupDetail.share_members.values_list("id", flat=True)),
                "original_price": groupDetail.original_price,
                "share_price": groupDetail.share_price,
                'getting_time': groupDetail.getting_time.astimezone(tz=paris_tz).strftime('%Y/%m/%d %H:%M'),
                'update_time': groupDetail.update_time.astimezone(tz=paris_tz).strftime('%Y/%m/%d'),
                'create_time': groupDetail.create_time.astimezone(tz=paris_tz).strftime('%Y/%m/%d'),
            }
            result.append(receipt_data)
        return result

    async def price_of_member(self, json_data):
        data = await self.get_price_of_member(json_data)
        await self.send(text_data=json.dumps({'type': 'price_of_member', 'data': data}, ensure_ascii=False))

    @sync_to_async
    def get_price_of_member(self, json_data):
        share_stats = ShareStats.objects.filter(share_group_detail__token=uuid.UUID(self.room_name))
        result = []
        for share_stat in share_stats:
            share_stat:ShareStats
            result.append({
                'out_member': share_stat.out_member.id,
                'in_member': share_stat.in_member.id,
                'price': share_stat.price,
                'id': share_stat.id
            })
        return result

    async def update_group_table(self, json_data):
        await self.send(text_data=json.dumps(json_data, ensure_ascii=False))

import uuid
import zoneinfo

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template import RequestContext
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.generic import TemplateView, View

from share.enums import MemberRole
from share.forms import GroupCreateForm, csrfForm
from share.models import (ShareGroup, ShareGroupDetail, ShareGroupHistory,
                          ShareMember, ShareStats, UserDetail)

paris_tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)
# Create your views here.

class Share(TemplateView):
    def get(self, request):
        if request.user.is_anonymous:
            return HttpResponseRedirect(f'/accounts/login/?next={request.path}')
        share_options = ShareMember.objects.filter(user=request.user, member_type__lt=40)
        return render(request, 'share_base.html', {'share_options': share_options})


class Information(TemplateView):
    def get(self, request):
        if request.user.is_anonymous:
            return HttpResponseRedirect(f'/accounts/login/?next={request.path}')
        share_options = ShareMember.objects.filter(user=request.user, member_type__lt=40)
        return render(request, 'information.html', {'share_options': share_options})

    def post(self, request):
        userDetails = UserDetail.objects.filter(user=request.user)
        result = []
        for userDetail in userDetails:
            userDetail:UserDetail
            receipt_data = {
                'id': userDetail.id,
                'item': userDetail.item,
                "price": format(userDetail.price, ','),
                'share_group': userDetail.share_group_detail.title if userDetail.share_group_detail else '',
                'remark': userDetail.remark,
                'getting_time': userDetail.getting_time.astimezone(tz=paris_tz).strftime('%Y/%m/%d %H:%M'),
                'create_time': userDetail.create_time.astimezone(tz=paris_tz).strftime('%Y/%m/%d %H:%M:%S'),
            }
            result.append(receipt_data)
        return JsonResponse({'result': result})

class ModalAddItam(TemplateView):
    def get(self, request, detail_id):
        form = csrfForm()
        if detail_id == 'new':
            return render(request, 'modal_add_item.html', {'form': form, 'title': '新增項目'})
        try:
            userDetail = UserDetail.objects.get(id=int(detail_id), user=request.user)
        except:
            return render(request, 'modal_group_error.html', {'message': '參數錯誤'})
        return render(request, 'modal_add_item.html', {'form': form, 'userDetail': userDetail, 'title': '修改項目'})

    def post(self, request, detail_id):
        form = csrfForm(request.POST)
        if form.is_valid() == False:
            return JsonResponse({'message': '表單已失效，請重新整理。'})

        post_data:dict = request.POST.dict()

        create_date = post_data.get('create_date', '')
        create_time = post_data.get('create_time', '')

        getting_time = parse_datetime(f"{create_date} {create_time}")
        getting_time = getting_time.replace(tzinfo=paris_tz)

        if detail_id == 'new':
            userDetail = UserDetail.objects.create(
                user=request.user, 
                item=post_data.get('item', ''),
                price=int(post_data.get('price', 0) if post_data.get('price', '') != '' else 0),
                remark=post_data.get('remark', ''),
                getting_time=getting_time,
                )

            receipt_data = {
                'id': userDetail.id,
                'item': userDetail.item,
                "price": format(userDetail.price, ','),
                'share_group': userDetail.share_group_detail.title if userDetail.share_group_detail else '',
                'remark': userDetail.remark,
                'getting_time': userDetail.getting_time.astimezone(tz=paris_tz).strftime('%Y/%m/%d %H:%M'),
                'create_time': userDetail.create_time.astimezone(tz=paris_tz).strftime('%Y/%m/%d %H:%M:%S'),
            }

            return JsonResponse({'message': '新增成功', 'receipt_data': receipt_data})

        try:
            userDetail = UserDetail.objects.get(id=int(detail_id), user=request.user)
            if 'del' in request.POST:
                userDetail.delete()
                receipt_data = {'id': int(detail_id),}
                return JsonResponse({'message': '刪除成功', 'receipt_data': receipt_data})

            userDetail.item = post_data.get('item', '')
            userDetail.price = int(post_data.get('price', 0) if post_data.get('price', '') != '' else 0)
            userDetail.remark = post_data.get('remark', '')
            userDetail.getting_time = getting_time
            userDetail.save()

            receipt_data = {
                'id': userDetail.id,
                'item': userDetail.item,
                "price": format(userDetail.price, ','),
                'share_group': userDetail.share_group_detail.title if userDetail.share_group_detail else '',
                'remark': userDetail.remark,
                'getting_time': userDetail.getting_time.astimezone(tz=paris_tz).strftime('%Y/%m/%d %H:%M'),
                'create_time': userDetail.create_time.astimezone(tz=paris_tz).strftime('%Y/%m/%d %H:%M:%S'),
            }

            return JsonResponse({'message': '更新成功', 'receipt_data': receipt_data})

        except:
            return JsonResponse({'message': '參數錯誤'})


class GroupCreate(TemplateView):
    def get(self, request):
        if request.user.is_anonymous:
            return HttpResponseRedirect(f'/accounts/login/?next={request.path}')

        form = GroupCreateForm()
        share_options = ShareMember.objects.filter(user=request.user, member_type__lt=40)
        context = {
            'form': form,
            'share_options': share_options
        }
        return render(request, 'group_create.html', context)

    def post(self, request):
        form = GroupCreateForm(request.POST)
        if form.is_valid():
            share_group = form.save()
            ShareMember.objects.create(share_group=share_group, user=request.user, nick_name=request.user.username, member_type=MemberRole.OWNER)
            return HttpResponseRedirect(f'/share/group/{share_group.token.hex}/')

        share_options = ShareMember.objects.filter(user=request.user, member_type__lt=40)
        return render(request, 'group_create.html', {'form': form, 'share_options': share_options})

class Group(TemplateView):
    def get(self, request, token):
        if request.user.is_anonymous:
            return HttpResponseRedirect(f'/accounts/login/?next={request.path}')

        share_options = ShareMember.objects.filter(user=request.user, member_type__lt=40)
        context = {
            'share_options': share_options
        }
        if len(token) != 32:
            return render(request, 'group.html', context)

        share_group = ShareGroup.objects.filter(token=token)
        if share_group.exists() == False:
            context['message'] = '連結已失效或分寶群未公開'
            return render(request, 'group_error.html', context)

        context['share_group'] = share_group[0]
        share_self = share_options.filter(share_group=share_group[0])
        is_edit = False
        if share_self.exists():
            if share_self[0].member_type in [MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MEMBER]:
                is_edit = True
            elif share_self[0].member_type == MemberRole.AUDIT and share_group[0].is_viewable == False:
                context['message'] = '管理者審核中'
                return render(request, 'group_error.html', context)

        elif share_group[0].is_viewable == False:
            context['message'] = '連結已失效或分寶群未公開'
            return render(request, 'group_error.html', context)
        if share_self:
            context['share_self'] = share_self[0]
        context['is_edit'] = is_edit
        # 要分 參觀模式跟 編輯模式
        return render(request, 'group.html', context)

class ModalGroupMembers(TemplateView):
    def get(self, request, member_id):
        shareMembers = ShareMember.objects.filter(id=int(member_id))
        if shareMembers.exists() == False:
            return render(request, 'modal_group_error.html', {'message': '參數錯誤'})
        shareMember = shareMembers[0]

        if shareMember.member_type in [MemberRole.ADMIN, MemberRole.OWNER]:
            is_edit = True
        elif shareMember.member_type == MemberRole.MEMBER:
            is_edit = False
        else:
            return render(request, 'modal_group_error.html', {'message': '無權限'})

        group_members = shareMember.share_group.sharemember_set.all()

        form = csrfForm()

        # aa = modelformset_factory(ShareMember, fields=('nick_name', 'member_type'))
        # bb = aa(queryset=group_members)
        # return render(request, 'modal_group_members.html', {
        #     'formset': bb})

        return render(request, 'modal_group_members.html', {
            'share_self': shareMember,
            'share_group': shareMember.share_group,
            'group_members': group_members, 
            'is_edit': is_edit, 
            'form': form, 
            'memberRole_choices': MemberRole.choices()})

    def post(self, request, member_id):
        form = csrfForm(request.POST)
        if form.is_valid() == False:
            return JsonResponse({'message': '表單已失效，請重新整理。'})

        shareMembers = ShareMember.objects.filter(id=int(member_id))
        shareMember = shareMembers[0]
        if shareMember.member_type not in [MemberRole.ADMIN, MemberRole.OWNER]:
            return JsonResponse({'message': '不要亂搞喔'})

        group_members = shareMember.share_group.sharemember_set.all()

        group_member_dict = {}

        for group_member in group_members:
            group_member_dict[group_member.id] = group_member

        for key, value in request.POST.dict().items():
            key:str
            key_det = key.split('-')
            if len(key_det) != 3:
                continue
            group_member:ShareMember = group_member_dict.get(int(key_det[1]), None)
            if group_member == None:
                print('找不到使用者')
                continue
            elif group_member.member_type == MemberRole.OWNER and shareMember.member_type == MemberRole.ADMIN:
                print('嘗試賦值所有者')
                continue

            if key_det[2] == 'nick_name':
                group_member.nick_name = value
            if key_det[2] == 'member_type':
                if '21' == value or shareMember.member_type == MemberRole.ADMIN and '22' == value:
                    # 嘗試賦值管理權
                    continue
                group_member.member_type = value

        ShareMember.objects.bulk_update(group_member_dict.values(), fields=['nick_name', 'member_type'])
        return JsonResponse({'message': '變更成功'})

class ModalGroupJoin(TemplateView):
    def get(self, request, token):
        form = csrfForm()
        share_groups = ShareGroup.objects.filter(token=token)
        if share_groups.exists() == False:
            return render(request, 'modal_group_error.html', {'message': '參數錯誤'})

        share_group = share_groups[0]
        data = {'share_group': share_group,
                'form': form}

        share_members = share_group.sharemember_set.filter(user=request.user)
        if share_members.exists():
            share_member = share_members[0]
            if share_member.member_type == MemberRole.BLOCKADE:
                return render(request, 'modal_group_error.html', {'message': '參數錯誤'})
            else:
                data['share_member'] = share_member
        return render(request, 'modal_group_join.html', data)

    def post(self, request, token):
        form = csrfForm(request.POST)
        if form.is_valid() == False:
            return JsonResponse({'message': '表單已失效，請重新整理。'})

        nick_name = request.POST.get('nick_name', request.user.username)
        introduce = request.POST.get('introduce', '')
        share_groups = ShareGroup.objects.filter(token=token)
        if share_groups.exists() == False:
            return JsonResponse({'message': '申請失敗'})
        share_group:ShareGroup = share_groups[0]

        if share_group.is_viewable and share_group.is_apply:
            share_members = share_group.sharemember_set.filter(user=request.user)
            if share_members.exists() == False:
                ShareMember.objects.create(share_group=share_group, user=request.user, nick_name=nick_name)
                return JsonResponse({'message': '申請成功'})

            share_member:ShareMember = share_members[0]
            if share_member.member_type == MemberRole.BLOCKADE:
                return JsonResponse({'message': '申請失敗'})

            if 'del' in request.POST:
                share_member.delete()
                return JsonResponse({'message': '取消成功'})

            share_member.nick_name = nick_name
            share_member.introduce = introduce
            share_member.save()
            return JsonResponse({'message': '更改成功'})
        return JsonResponse({'message': '申請失敗'})

class ModalGroupAdmin(TemplateView):
    def get(self, request, member_id):
        form = csrfForm()

        shareMembers = ShareMember.objects.filter(id=int(member_id))
        if shareMembers.exists() == False:
            return render(request, 'modal_group_error.html', {'message': '參數錯誤'})
        shareMember = shareMembers[0]

        if shareMember.member_type not in [MemberRole.ADMIN, MemberRole.OWNER]:
            return render(request, 'modal_group_error.html', {'message': '無權限'})

        return render(request, 'modal_group_admin.html', {
            'share_group': shareMember.share_group,
            'form': form})

    def post(self, request, member_id):
        form = csrfForm(request.POST)
        if form.is_valid() == False:
            return JsonResponse({'message': '表單已失效，請重新整理。'})

        shareMembers = ShareMember.objects.filter(id=int(member_id))
        if shareMembers.exists() == False:
            return JsonResponse({'message': '參數錯誤'})

        shareMember = shareMembers[0]
        if shareMember.member_type not in [MemberRole.ADMIN, MemberRole.OWNER]:
            return JsonResponse({'message': '不要亂搞喔'})

        share_group = shareMember.share_group
        post_data = request.POST.dict()

        share_group.title = post_data.get('title', '')

        if 'is_viewable' in post_data:
            share_group.is_viewable = True
        else:
            share_group.is_viewable = False

        if 'is_apply' in post_data:
            share_group.is_apply = True
        else:
            share_group.is_apply = False

        data = {'message': '更新成功'}
        if 'change_token' in post_data:
            share_group.token = uuid.uuid4()
            data['url'] = f'/share/group/{share_group.token.hex}/'

        share_group.update_time = timezone.now()
        share_group.save()

        return JsonResponse(data)


class ModalGroupAddItam(TemplateView):
    def get(self, request, group_id, detail_id):
        form = csrfForm()
        data = {'form': form,}
        try:
            share_self = ShareMember.objects.get(share_group__id=int(group_id), user=request.user)
            if share_self.member_type not in [MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MEMBER]:
                return render(request, 'modal_group_error.html', {'message': '參數錯誤'})
            data['share_self'] = share_self

            if detail_id == 'new':
                groupDetail = ShareGroupDetail.objects.filter(share_group__id=int(group_id)).last()
                share_members = list(groupDetail.share_members.values_list("id", flat=True)) if groupDetail else []
                data['title'] = '新增項目'
                data['share_members'] = share_members # 取最後一筆的紀錄
                return render(request, 'modal_group_add_item.html', data)

            groupDetail = ShareGroupDetail.objects.get(share_group__id=int(group_id), id=int(detail_id))
            share_members = list(groupDetail.share_members.values_list("id", flat=True))
            data['title'] = '修改項目'
            data['groupDetail'] = groupDetail
            data['share_members'] = share_members
        except:
            return render(request, 'modal_group_error.html', {'message': '參數錯誤'})
        return render(request, 'modal_group_add_item.html', data)

    def post(self, request, group_id, detail_id):
        form = csrfForm(request.POST)
        if form.is_valid() == False:
            return JsonResponse({'message': '表單已失效，請重新整理。'})

        share_self = ShareMember.objects.get(share_group__id=int(group_id), user=request.user)
        if share_self.member_type not in [MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MEMBER]:
            return JsonResponse({'message': '參數錯誤'})

        post_data:dict = request.POST.dict()
        share_members_list = list(map(int, dict(request.POST).get('share_members', [])))

        price_options = post_data.get('price_options', '')

        share_group=ShareGroup.objects.get(id=int(group_id))
        set_member = share_group.sharemember_set.get(user=request.user)
        
        share_members = share_group.sharemember_set.filter(id__in=share_members_list)

        original_price=int(post_data.get('original_price', 0) if post_data.get('original_price', '') != '' else 0)
        share_members_num = len(share_members)
        share_price = 0
        if original_price:
            if price_options == '1':
                share_price = int(original_price/share_members_num)
            else:
                price = int(original_price/0.95)
                fee = int(price*0.01 if price*0.01 <= 100000 else 100000)
                share_price = int((original_price-fee)*0.98/share_members_num)

        channel_layer = get_channel_layer()
        if detail_id == 'new':
            create_date = post_data.get('create_date', '')
            create_time = post_data.get('create_time', '')
            getting_time = parse_datetime(f"{create_date} {create_time}")
            getting_time = getting_time.replace(tzinfo=paris_tz)
            get_member = share_group.sharemember_set.get(id=int(post_data.get('get_member')))

            groupDetail = ShareGroupDetail.objects.create(
                share_group=ShareGroup.objects.get(id=int(group_id)),
                item=post_data.get('item', ''),
                set_member=set_member,
                get_member=get_member,
                original_price=original_price,
                share_price=share_price,
                getting_time=getting_time,
                extra={'price_options': price_options}
            )
            groupDetail.share_members.set(share_members)

            distribute_money(
                item=groupDetail.item,
                share_group_detail=groupDetail.share_group, 
                getting_time=groupDetail.getting_time,
                get_member=get_member,
                before_members=ShareMember.objects.none(), 
                after_members=share_members, 
                before_price=0,
                after_price=groupDetail.share_price
                )

            async_to_sync(channel_layer.group_send)(share_group.token.hex, {
                "type": "update_group_table", 
                "data": {
                    "type": 'append',
                    "data": get_output_json(groupDetail)},})

            async_to_sync(channel_layer.group_send)(share_group.token.hex, {
                "type": "price_of_member", "is_group": True})

            return JsonResponse({'message': '新增成功'})
        try:
            groupDetail = ShareGroupDetail.objects.get(share_group__id=int(group_id), id=int(detail_id))
            if 'del' in request.POST:
                del_id = groupDetail.id

                distribute_money(
                    item=groupDetail.item,
                    share_group_detail=groupDetail.share_group, 
                    getting_time=groupDetail.getting_time,
                    get_member=groupDetail.get_member,
                    before_members=groupDetail.share_members.all(), 
                    after_members=ShareMember.objects.none(), 
                    before_price=groupDetail.share_price,
                    after_price=0
                    )
                groupDetail.delete()

                async_to_sync(channel_layer.group_send)(share_group.token.hex, {
                    "type": "update_group_table", 
                    "data": {
                        "type": 'delete',
                        "data": {'id': del_id}}})

                async_to_sync(channel_layer.group_send)(share_group.token.hex, {
                    "type": "price_of_member", "is_group": True})
                return JsonResponse({'message': '刪除成功'})

            distribute_money(
                item=post_data.get('item', ''), 
                share_group_detail=groupDetail.share_group, 
                getting_time=groupDetail.getting_time,
                get_member=groupDetail.get_member,
                before_members=groupDetail.share_members.all(), 
                after_members=share_members, 
                before_price=groupDetail.share_price, 
                after_price=share_price)

            groupDetail.item=post_data.get('item', '')
            groupDetail.set_member=set_member
            groupDetail.original_price=original_price
            groupDetail.share_price=share_price
            groupDetail.extra={'price_options': price_options}
            groupDetail.share_members.set(share_members)
            groupDetail.save()

            async_to_sync(channel_layer.group_send)(share_group.token.hex, {
                "type": "update_group_table", 
                "data": {
                    "type": 'update',
                    "data": get_output_json(groupDetail)},})
            async_to_sync(channel_layer.group_send)(share_group.token.hex, {
                "type": "price_of_member", "is_group": True})
            return JsonResponse({'message': '更新成功'})

        except:
            return JsonResponse({'message': '參數錯誤'})

def get_output_json(groupDetail:ShareGroupDetail):
    return {
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
        'extra': groupDetail.extra
        }

def distribute_money(item, 
                    share_group_detail, 
                    getting_time, 
                    get_member, 
                    before_members, 
                    after_members, 
                    before_price:int, 
                    after_price:int):
    detail_data = []

    share_stats = ShareStats.objects.filter(share_group_detail=share_group_detail)
    share_stat_dict = {}
    for share_stat in share_stats:
        share_stat_dict[(share_stat.out_member.id, share_stat.in_member.id)] = share_stat

    # 之前有 之後沒有的
    diff_before = before_members.exclude(pk__in=after_members)
    if before_price:
        for member in diff_before:
            member:ShareMember
            detail_data.append(UserDetail(
                user=member.user,
                item=item,
                price=before_price*-1,
                share_group_detail=share_group_detail,
                remark=f'移除項目',
                getting_time=getting_time,
            ))
            set_money(share_group_detail, share_stat_dict, get_member, member, before_price*-1)
            set_money(share_group_detail, share_stat_dict, member, get_member, before_price)


    # 之前沒有 之後有的
    diff_after = after_members.exclude(pk__in=before_members)
    if after_price:
        for member in diff_after:
            member:ShareMember
            detail_data.append(UserDetail(
                user=member.user,
                item=item,
                price=after_price,
                share_group_detail=share_group_detail,
                getting_time=getting_time,
            ))
            set_money(share_group_detail, share_stat_dict, get_member, member, after_price)
            set_money(share_group_detail, share_stat_dict, member, get_member, after_price*-1)


    # 之前和之後都有的
    intersection = before_members & after_members
    if intersection:
        remark = ''
        if (before_price == 0 and after_price > 0) == False:
            remark='修改項目'

        for member in intersection:
            member:ShareMember
            detail_data.append(UserDetail(
                user=member.user,
                item=item,
                price=after_price-before_price,
                share_group_detail=share_group_detail,
                remark=remark,
                getting_time=getting_time,
            ))
            set_money(share_group_detail, share_stat_dict, get_member, member, after_price-before_price)
            set_money(share_group_detail, share_stat_dict, member, get_member, (after_price-before_price)*-1)

    ShareStats.objects.bulk_update(share_stat_dict.values(), fields=['out_member', 'in_member', 'price'])
    UserDetail.objects.bulk_create(detail_data)

def set_money(share_group_detail, share_stat_dict, out_member, in_member, maney):
    if out_member.id == in_member.id:
        return
    elif share_stat_dict not in (out_member.id, in_member.id):
        hare_stat, _  = ShareStats.objects.get_or_create(share_group_detail=share_group_detail, out_member=out_member, in_member=in_member)
        share_stat_dict[(hare_stat.out_member.id, hare_stat.in_member.id)] = hare_stat
    share_stat_dict[(out_member.id, in_member.id)].price += maney


class ModalGroupSendPrice(TemplateView):
    def get(self, request, group_id, share_stats_id):
        form = csrfForm()
        data = {'form': form,}

        try:
            share_self = ShareMember.objects.get(share_group__id=int(group_id), user=request.user)
            if share_self.member_type not in [MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MEMBER]:
                return render(request, 'modal_group_error.html', {'message': '參數錯誤'})
            
            share_stat = ShareStats.objects.get(share_group_detail__id=int(group_id), id=int(share_stats_id))
            data['share_stat'] = share_stat
        except:
            return render(request, 'modal_group_error.html', {'message': '參數錯誤'})

        # return render(request, 'modal_group_error.html', {'message': '參數錯誤'})
        return render(request, 'modal_group_send_price.html', data)

    def post(self, request, group_id, share_stats_id):
        form = csrfForm(request.POST)
        if form.is_valid() == False:
            return JsonResponse({'message': '表單已失效，請重新整理。'})

        share_self = ShareMember.objects.get(share_group__id=int(group_id), user=request.user)
        if share_self.member_type not in [MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MEMBER]:
            return JsonResponse({'message': '參數錯誤'})
        
        share_group = share_self.share_group
        post_data:dict = request.POST.dict()
        price = int(post_data.get('price', ''))
        share_stat = ShareStats.objects.get(share_group_detail__id=int(group_id), id=int(share_stats_id))

        groupDetail = ShareGroupDetail.objects.create(
            share_group=share_group,
            item="銷帳",
            set_member=share_self,
            get_member=share_stat.in_member,
            original_price=price,
            share_price=price,
            extra={'price_options': 1}
        )
        groupDetail.share_members.add(share_stat.out_member)

        distribute_money(
            item=groupDetail.item,
            share_group_detail=groupDetail.share_group, 
            getting_time=groupDetail.getting_time,
            get_member=groupDetail.get_member,
            before_members=ShareMember.objects.none(), 
            after_members=groupDetail.share_members.all(), 
            before_price=0,
            after_price=groupDetail.share_price
            )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(share_group.token.hex, {
            "type": "update_group_table", 
            "data": {
                "type": 'append',
                "data": get_output_json(groupDetail)},})

        async_to_sync(channel_layer.group_send)(share_group.token.hex, {
            "type": "price_of_member", "is_group": True})
        return JsonResponse({'message': '新增成功'})



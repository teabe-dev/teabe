import uuid
import zoneinfo

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
from share.models import ShareGroup, ShareMember, UserDetail, ShareGroupDetail, ShareGroupHistory
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

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
                'create_time': userDetail.create_time.astimezone(tz=paris_tz).strftime('%Y/%m/%d %H:%M'),
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
                'create_time': userDetail.create_time.astimezone(tz=paris_tz).strftime('%Y/%m/%d %H:%M'),
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
                'create_time': userDetail.create_time.astimezone(tz=paris_tz).strftime('%Y/%m/%d %H:%M'),
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
        try:
            share_self = ShareMember.objects.get(share_group__id=int(group_id), user=request.user)
            if share_self.member_type not in [MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MEMBER]:
                return render(request, 'modal_group_error.html', {'message': '參數錯誤'})

            if detail_id == 'new':
                groupDetail = ShareGroupDetail.objects.filter(share_group__id=int(group_id)).last()
                share_members = list(groupDetail.share_members.values_list("id", flat=True)) if groupDetail else []
                return render(request, 'modal_group_add_item.html', {
                    'title': '新增項目', 
                    'form': form, 
                    'share_self': share_self,
                    'share_members': share_members,
                    })

            groupDetail = ShareGroupDetail.objects.get(share_group__id=int(group_id), id=int(detail_id))
            share_members = list(groupDetail.share_members.values_list("id", flat=True))
        except:
            return render(request, 'modal_group_error.html', {'message': '參數錯誤'})
        return render(request, 'modal_group_add_item.html', {
            'title': '修改項目', 
            'form': form, 
            'share_self': share_self,
            'groupDetail': groupDetail, 
            'share_members': share_members, 
            })

    def post(self, request, group_id, detail_id):
        form = csrfForm(request.POST)
        if form.is_valid() == False:
            return JsonResponse({'message': '表單已失效，請重新整理。'})

        share_self = ShareMember.objects.get(share_group__id=int(group_id), user=request.user)
        if share_self.member_type not in [MemberRole.OWNER, MemberRole.ADMIN, MemberRole.MEMBER]:
            return render(request, 'modal_group_error.html', {'message': '參數錯誤'})

        post_data:dict = request.POST.dict()
        share_members_list = list(map(int, dict(request.POST).get('share_members', [])))

        create_date = post_data.get('create_date', '')
        create_time = post_data.get('create_time', '')

        getting_time = parse_datetime(f"{create_date} {create_time}")
        getting_time = getting_time.replace(tzinfo=paris_tz)

        share_group=ShareGroup.objects.get(id=int(group_id))
        set_member = share_group.sharemember_set.get(user=request.user)
        get_member = share_group.sharemember_set.get(id=int(post_data.get('get_member')))
        share_members = share_group.sharemember_set.filter(id__in=share_members_list)

        original_price=int(post_data.get('original_price', 0) if post_data.get('original_price', '') != '' else 0)

        channel_layer = get_channel_layer()
        if detail_id == 'new':
            groupDetail = ShareGroupDetail.objects.create(
                share_group=ShareGroup.objects.get(id=int(group_id)),
                item=post_data.get('item', ''),
                set_member=set_member,
                get_member=get_member,
                original_price=original_price,
                share_price=int(original_price/len(share_members)),
                getting_time=getting_time,
            )
            groupDetail.share_members.set(share_members)

            async_to_sync(channel_layer.group_send)(share_group.token.hex, {
                "type": "update_group_table", 
                "data": {
                    "type": 'append',
                    "data": {
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
                }},})

            return JsonResponse({'message': '新增成功'})
        try:
            groupDetail = ShareGroupDetail.objects.get(share_group__id=int(group_id), id=int(detail_id))
            if 'del' in request.POST:
                del_id = groupDetail.id
                groupDetail.delete()
                async_to_sync(channel_layer.group_send)(share_group.token.hex, {
                    "type": "update_group_table", 
                    "data": {
                        "type": 'delete',
                        "data": {
                        'id': del_id,}},})
                return JsonResponse({'message': '刪除成功'})
            groupDetail.item=post_data.get('item', '')
            groupDetail.set_member=set_member
            groupDetail.get_member=get_member
            groupDetail.original_price=original_price
            groupDetail.share_price=int(original_price/len(share_members))
            groupDetail.getting_time=getting_time
            groupDetail.save()

            async_to_sync(channel_layer.group_send)(share_group.token.hex, {
                "type": "update_group_table", 
                "data": {
                    "type": 'update',
                    "data": {
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
                }},})
            return JsonResponse({'message': '更新成功'})

        except:
            return render(request, 'modal_group_error.html', {'message': '參數錯誤'})
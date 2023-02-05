import uuid

from django.forms import formset_factory, modelformset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template import RequestContext
from django.views.generic import TemplateView, View

from share.enums import MemberRole
from share.forms import GroupCreateForm, csrfForm
from share.models import ShareGroup, ShareMember
from django.utils import timezone
# Create your views here.

class Share(TemplateView):
    def get(self, request):
        if request.user.is_anonymous:
            return HttpResponseRedirect('/accounts/login/')
        share_options = ShareMember.objects.filter(user=request.user, member_type__lt=40)
        return render(request, 'share_base.html', {'share_options': share_options})


class Information(TemplateView):
    def get(self, request):
        share_options = ShareMember.objects.filter(user=request.user, member_type__lt=40)
        return render(request, 'information.html', {'share_options': share_options})


class GroupCreate(TemplateView):
    def get(self, request):
        if request.user.is_anonymous:
            return HttpResponseRedirect('/accounts/login/')

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

        # TODO 可在前端顯示成員列表並可編輯
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
            if share_member.member_type == MemberRole.AUDIT:
                data['share_member'] = share_member
            else:
                return render(request, 'modal_group_error.html', {'message': '權限已變更，請重新整理頁面'})
        return render(request, 'modal_group_join.html', data)

    def post(self, request, token):
        form = csrfForm(request.POST)
        if form.is_valid() == False:
            return JsonResponse({'message': '表單已失效，請重新整理。'})

        nick_name = request.POST.get('nick_name', request.user.username)
        share_groups = ShareGroup.objects.filter(token=token)
        if share_groups.exists() == False:
            return JsonResponse({'message': '申請失敗'})
        share_group:ShareGroup = share_groups[0]

        if share_group.is_viewable and share_group.is_apply:
            share_members = share_group.sharemember_set.filter(user=request.user)
            if share_members.exists():
                share_member:ShareMember = share_members[0]
                if share_member.member_type == MemberRole.AUDIT:
                    if 'del' in request.POST:
                        share_member.delete()
                        return JsonResponse({'message': '取消成功'})

                    share_member.nick_name = nick_name
                    share_member.save()
                    return JsonResponse({'message': '更改成功'})
                else:
                    return JsonResponse({'message': '已申請'})

            ShareMember.objects.create(share_group=share_group, user=request.user, nick_name=nick_name)
            return JsonResponse({'message': '申請成功'})
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

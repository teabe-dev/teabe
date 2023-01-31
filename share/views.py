from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView, View

from share.enums import MemberRole
from share.forms import NewGroupForm
from share.models import ShareGroup, ShareMember

# Create your views here.

class Share(TemplateView):
    def get(self, request):
        if request.user.is_anonymous:
            return HttpResponseRedirect('/accounts/login/')
        share_data = ShareMember.objects.filter(user=request.user)
        return render(request, 'share_base.html', {'share_data': share_data})


class Information(TemplateView):
    def get(self, request):
        share_data = ShareMember.objects.filter(user=request.user)
        return render(request, 'information.html', {'share_data': share_data})


class NewGroup(TemplateView):
    def get(self, request):
        if request.user.is_anonymous:
            return HttpResponseRedirect('/accounts/login/')

        form = NewGroupForm()
        share_data = ShareMember.objects.filter(user=request.user)
        context = {
            'form': form,
            'share_data': share_data
        }
        return render(request, 'new_group.html', context)

    def post(self, request):
        form = NewGroupForm(request.POST)
        if form.is_valid():
            share_group = form.save()
            ShareMember.objects.create(share_group=share_group, user=request.user, nick_name=request.user.username, member_type=MemberRole.OWNER)
            # 轉跳

        share_data = ShareMember.objects.filter(user=request.user)
        return render(request, 'new_group.html', {'form': form, 'share_data': share_data})

class Group(TemplateView):
    def get(self, request, token):
        share_data = ShareMember.objects.filter(user=request.user)
        # TODO 顯示分寶資訊
        return render(request, 'information.html', {'share_data': share_data})
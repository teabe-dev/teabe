from django.shortcuts import render
from django.views.generic import View, TemplateView
from django.http import HttpResponseRedirect
from share.forms import NewGroupForm
from share.models import ShareMember
from share.enums import MemberType
# Create your views here.

class Share(TemplateView):
    def get(self, request):
        if request.user.is_anonymous:
            return HttpResponseRedirect('/accounts/login/')
        return render(request, 'share_base.html')


class NewGroup(TemplateView):
    def get(self, request):
        if request.user.is_anonymous:
            return HttpResponseRedirect('/accounts/login/')

        form = NewGroupForm()
        context = {
            'form': form
        }
        return render(request, 'new_group.html', context)

    def post(self, request):
        form = NewGroupForm(request.POST)
        if form.is_valid():
            share_group = form.save()
            ShareMember.objects.create(share_group=share_group, user=request.user, member_type=MemberType.OWNER)
        return render(request, 'new_group.html', {'form': form})

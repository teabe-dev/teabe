from django.shortcuts import render
from django.views.generic import View, TemplateView
from django.http import HttpResponseRedirect
# Create your views here.

class Share(TemplateView):
    def get(self, request):
        if request.user.is_anonymous:
            return HttpResponseRedirect('/accounts/login/')
        return render(request, 'share_base.html')
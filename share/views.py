from django.shortcuts import render
from django.views.generic import View, TemplateView
# Create your views here.

class Group(TemplateView):
    def get(self, request):
        # if request.user.is_anonymous:
        #     return HttpResponseRedirect('/accounts/login/')
        return render(request, 'group.html')
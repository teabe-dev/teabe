from django import forms
from share import models

class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = models.ShareGroup
        fields = ('title', 'is_viewable', 'is_apply')

class csrfForm(forms.Form):
    pass
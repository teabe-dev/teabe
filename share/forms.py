from django import forms
from share import models

class NewGroupForm(forms.ModelForm):
    class Meta:
        model = models.ShareGroup
        fields = ('title', 'is_viewable')







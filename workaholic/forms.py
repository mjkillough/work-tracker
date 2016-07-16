#!/usr/bin/env python
# encoding: utf-8

from django import forms
from django.contrib import auth


class SignupForm(auth.forms.UserCreationForm):

    class Meta:
        model = auth.models.User
        fields = ("username", "email", "password1", "password2")

    email = forms.EmailField(required=True)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

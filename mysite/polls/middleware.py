import re
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from polls import models


def is_profile_complete(user):
    site = user.profile.site
    form = models.ProfileForm.objects.get(site=site)
    form_fields = form.form_fields['fields']

    required_fields = []
    required_choices = {}
    for field in form_fields:
        if field['required']:
            if field.get('choices'):
                required_choices[field['id']] = field['choices']
                required_fields.append(field['id'])
            else:
                required_choices[field['id']] = 'no-choice'
                required_fields.append(field['id'])

    fields_validations = []
    if user.profile.dynamic_fields:
        for user_field, value in user.profile.dynamic_fields.items():
            if user_field in required_fields and (value in str(required_choices[user_field]) or required_choices[user_field] == 'no-choice') and value:
                fields_validations.append(True)
            else:
                fields_validations.append(False)

        is_complete = all([*fields_validations, *[field in user.profile.dynamic_fields for field in required_fields]])
        return is_complete
    else:
        return False

class ProfileRedirectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        current_user = request.user
        skip_urls = [
            '/polls/myprofile',
            '/accounts/logout/',
        ]

        if (
            current_user.is_authenticated
            and request.path not in skip_urls
            and not is_profile_complete(current_user)
        ):
            return HttpResponseRedirect(reverse_lazy("my_profile"))

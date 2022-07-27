import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from polls import models
from polls.forms.user import ProfileForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@login_required
def index(request):
    """It renders the Polls"""
    answers = models.Answer.objects.select_related('poll')
    polls_count = len(set([answer.poll.pk for answer in answers]))
    context = {
        'polls': [{
            'title': '',
            'id': '',
            'answers': []
        } for _ in range(polls_count)]
    }
    for answer in answers:
        context['polls'][answer.poll.pk-1]['title'] = answer.poll.title
        context['polls'][answer.poll.pk-1]['id'] = answer.poll.id
        context['polls'][answer.poll.pk-1]['answers'].append({
                "value": answer.value,
                "user_first_name": answer.user.first_name,
                "user_last_name": answer.user.last_name,
                "id": answer.pk,
            })
    return render(request, 'polls/index.html', context)


@login_required
def my_profile(request):
    current_user_profile = request.user.profile
    user_form = models.ProfileForm.objects.get(site=current_user_profile.site)
    fields = user_form.form_fields['fields']
    data = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
    }
    data.update(current_user_profile.dynamic_fields)
    form = ProfileForm(fields=fields, initial=data)
    return render(request, 'polls/current_user.html', {'form': form})


@login_required
@csrf_exempt
def edit_answer(request, poll_id, answer_id):
    payload = json.loads(request.body)
    answer = models.Answer.objects.get(pk=answer_id)
    answer.value = payload.get('value')
    answer.save()
    return JsonResponse({"value": answer.value})

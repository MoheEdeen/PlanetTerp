from django.views import View
from django.http import JsonResponse
from django.template.context_processors import csrf

from crispy_forms.utils import render_crispy_form

from home.forms.professor_forms import ProfessorFormAdd
from home.models import Professor, Review, Course
from home.utils import send_updates_webhook

class AddProfessor(View):
    def post(self, request):
        user = request.user

        form = ProfessorFormAdd(user, data=request.POST)
        ctx = {}
        ctx.update(csrf(request))

        if form.is_valid():
            cleaned_data = form.cleaned_data

            new_professor = Professor(
                name=cleaned_data['name'],
                slug=None,
                type=cleaned_data['type_']
            )
            new_professor.save()

            course = Course.objects.filter(name=cleaned_data['course']).first()

            new_review = Review(
                professor=new_professor,
                course=course,
                user=user if user.is_authenticated else None,
                content=cleaned_data['content'],
                rating=cleaned_data['rating'],
                grade=cleaned_data['grade'],
                anonymous=cleaned_data['anonymous']
            )
            new_review.save()

            send_updates_webhook(request)

            form = ProfessorFormAdd(user)
            form_html = render_crispy_form(form, form.helper, context=ctx)

            context = {
                "success": True,
                "form": form_html
            }
        else:
            form_html = render_crispy_form(form, form.helper, context=ctx)

            context = {
                "success": False,
                "form": form_html
            }

        return JsonResponse(context)

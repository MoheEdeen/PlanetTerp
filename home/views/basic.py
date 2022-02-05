from django.template.context_processors import csrf
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView, RedirectView, ListView
from django.http import HttpResponse, Http404
from django.contrib.auth.mixins import UserPassesTestMixin

from crispy_forms.utils import render_crispy_form

from home.models import Organization, Professor, Course, Review, Grade, User
from home.tables.reviews_table import VerifiedReviewsTable, ProfileReviewsTable
from home.forms.basic import (HistoricCourseGradeForm,
    HistoricProfessorGradeForm, ProfileForm)
from home.views.data_sources import GradeData
from home.utils import recompute_ttl_cache

class About(View):
    def get(self, request):
        organizations = Organization.objects.all()

        context = {
            "organizations": organizations
        }
        return render(request, "about.html", context)

class Contact(RedirectView):
    permanent = True
    pattern_name = "about"

class PrivacyPolicy(TemplateView):
    template_name = "privacypolicy.html"

class TermsOfUse(TemplateView):
    template_name = "termsofuse.html"

class Courses(ListView):
    model = Course
    template_name = "course_list.html"

class Professors(ListView):
    queryset = Professor.verified.all()
    template_name = "professor_list.html"

class Documents(TemplateView):
    template_name = "documents.html"

class SetColorScheme(View):
    def post(self, request):
        request.session["color_scheme"] = request.POST["scheme"]
        return HttpResponse()

class Robots(TemplateView):
    content_type = "text/plain"
    template_name = "robots.html"

class Grades(View):
    template_name = "grades.html"

    def get(self, request):
        context = {
            "course_form": HistoricCourseGradeForm(),
            "professor_form": HistoricProfessorGradeForm()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        course = request.POST.get('course', None)
        semester = request.POST.get('semester', None)
        semester = semester if semester != '' else None
        pf_semesters = request.POST.get("pf_semesters", False) == "true"

        course_form = HistoricCourseGradeForm(course, semester, data=request.POST)
        professor_form = HistoricProfessorGradeForm(data=request.POST)

        ctx = {}
        ctx.update(csrf(request))
        context = {
            "course_search_success": False,
            "professor_search_success": False
        }

        if course is None and professor_form.is_valid():
            context["professor_search_success"] = True
            data = professor_form.cleaned_data
            professor = data.get("professor", None)
            context['professor_data'] = GradeData.compose_course_grade_data(professor, pf_semesters)

        if course is not None and course_form.is_valid():
            context["course_search_success"] = True
            data = course_form.cleaned_data
            professor = data.get("professor", None)
            course = data.get("course", None)
            semester = data.get("semester", None)
            section = data.get("section", None)
            context['course_data'] = GradeData.compose_grade_data(professor, course, semester, section, pf_semesters)

        context["professor_form"] = render_crispy_form(professor_form, professor_form.helper, context=ctx)
        context["course_form"] = render_crispy_form(course_form, course_form.helper, context=ctx)
        return JsonResponse(context)

class CourseReviews(View):
    def get(self, request, name):
        if name != name.upper():
            return redirect("course-reviews", name=name.upper())
        course = Course.unfiltered.filter(name=name).first()

        if course is None:
            raise Http404()

        reviews = course.review_set(manager="verified").order_by("-created_at")

        context = {
            "course": course,
            "num_reviews": reviews.count(),
            "reviews_table": VerifiedReviewsTable(reviews, request)
        }
        return render(request, "course_reviews.html", context)

class Index(View):
    def get(self, request):
        num_courses = Course.unfiltered.count()
        num_professors = Professor.verified.count()
        num_reviews = Review.verified.count()
        num_course_grades = Grade.unfiltered.count()

        recent_reviews = (
            Review
            .verified
            .filter(professor__status=Professor.Status.VERIFIED)
            .order_by("-pk")[:3]
        )
        random_organization = Organization.objects.order_by("?")
        random_organization = random_organization and random_organization[0]

        context = {
            "num_courses": num_courses,
            "num_professors": num_professors,
            "num_reviews": num_reviews,
            "num_course_grades": num_course_grades,
            "recent_reviews": recent_reviews,
            "random_organization": random_organization
        }
        return render(request, "index.html", context)

class SortReviewsTable(View):
    def post(self, request):
        data = request.POST
        obj_id = int(data["obj_id"])
        data_type = data["type"]
        dir_ = data["direction"]
        key =  "-rating" if dir_ == "desc" else ("rating" if dir_ == "asc" else "-created_at")
        if data_type == "professor":
            reviews = Review.verified.filter(professor__id=obj_id)
        elif data_type == "course":
            reviews = Review.verified.filter(course__id=obj_id)
        else:
            raise ValueError(f"Unknown type: {data_type}")

        reviews = reviews.order_by(key)

        context = {
            "reviews_table": VerifiedReviewsTable(reviews, request).as_html(request)
        }

        return JsonResponse(context)

class RecomputeTTLCache(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def post(self, _request):
        recompute_ttl_cache()
        return HttpResponse()

class UserProfile(UserPassesTestMixin, View):
    # as all accounts have the option to still leave anonymous reviews, only
    # allow admins to view individual user profiles for now.
    # We may want to allow people to view a subset of other user's profiles,
    # containing only their public reviews.
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, user_id):
        user = User.objects.filter(pk=user_id).first()
        if not user:
            raise Http404()

        reviews = user.review_set.order_by("created_at")

        context = {
            "reviews_table": ProfileReviewsTable(reviews, request),
            "form": ProfileForm(instance=user, allow_edits=False)
        }

        return render(request, "profile.html", context)

from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

login = LoginView.as_view(
    template_name="partials/form.html",
    extra_context={
        "form_name": "로그인",
        "sumbit_label": "로그인",
    }
)

logout = LogoutView.as_view(
    next_page="accounts:login",
)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"

profile = ProfileView.as_view()
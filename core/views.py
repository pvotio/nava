from django.shortcuts import render
from django.views.generic import View


class ReportStatusTemplateView(View):
    def get(self, request, hash_id):
        return render(request, "core/waiting_page.html", {"hash_id": hash_id})

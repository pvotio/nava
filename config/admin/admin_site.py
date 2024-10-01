from django.contrib.admin.sites import AdminSite

from config.admin.admin_forms import AdminAuthWithCaptcha


class AdminSiteWithCaptcha(AdminSite):
    login_form = AdminAuthWithCaptcha
    site_title = "Nava"
    site_header = "Nava"
    index_title = "Administration"

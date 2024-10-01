from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html
from guardian.admin import GuardedModelAdminMixin
from guardian.shortcuts import get_objects_for_user
from simple_history.admin import SimpleHistoryAdmin

from config.admin.admin_site import AdminSiteWithCaptcha
from core.admin_views import download_html_view, generate_report_view
from core.forms import ReportModelForm, TemplateModelForm
from core.models import Argument, Database, Report, Template

custom_admin = AdminSiteWithCaptcha(name="custom_admin")


class UserAdmin(BaseUserAdmin):
    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

    def delete_model(self, request, obj):
        if obj.is_superuser and not request.user.is_superuser:
            raise PermissionDenied

        super().delete_model(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            return readonly_fields + ("is_superuser",)

        return readonly_fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs

        return qs.exclude(is_superuser=True)


class DatabaseAdmin(admin.ModelAdmin):
    model = Database
    ordering = ["-created_at"]
    search_fields = ["name", "backend"]
    list_display = ["name", "backend", "created_at", "updated_at"]
    list_filter = ["name", "backend", "created_at", "updated_at"]
    readonly_fields = [
        "id",
        "updated_at",
        "created_at",
    ]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["_connection_string"].widget.attrs.update(
            {
                "placeholder": (
                    "host=[db_host];user=[db_user];password="
                    "[db_password];database=[db_name];port=[db_port]"
                )
            }
        )
        return form


class ArgumentsAdmin(admin.TabularInline):
    model = Argument
    extra = 0


class TemplateAdmin(GuardedModelAdminMixin, SimpleHistoryAdmin):
    form = TemplateModelForm
    change_form_template = "admin/core_template_change_form.html"
    ordering = ["-created_at"]
    list_display = ["title", "id", "is_active", "user", "updated_at", "created_at"]
    list_filter = ["user", "is_active", "created_at", "updated_at"]
    list_per_page = 10
    history_list_display = ["changed_fields"]
    readonly_fields = ["id", "updated_at", "created_at"]
    inlines = [ArgumentsAdmin]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:template_id>/generate/",
                self.admin_site.admin_view(
                    lambda request, template_id: generate_report_view(
                        request, template_id, self.admin_site
                    )
                ),
                name="generate_report",
            )
        ]
        return custom_urls + urls

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if "user" in form.base_fields:
            form.base_fields["user"].initial = request.user
            form.base_fields["user"].disabled = True
        return form

    @staticmethod
    def is_user_admin(user):
        return user.groups.filter(name__iexact="admin").exists()

    def has_module_permission(self, request):
        if super().has_module_permission(request):
            return True
        return self.get_model_objects(request).exists()

    def get_queryset(self, request):
        if (
            request.user.is_superuser
            or request.user.groups.filter(name__iexact="admin").exists()
        ):
            return super().get_queryset(request)
        data = self.get_model_objects(request)
        return data

    def get_model_objects(self, request, action=None, klass=None):
        opts = self.opts
        actions = [action] if action else ["view", "edit", "delete"]
        klass = klass if klass else opts.model
        model_name = klass._meta.model_name
        return get_objects_for_user(
            user=request.user,
            perms=[f"{perm}_{model_name}" for perm in actions],
            klass=klass,
            any_perm=True,
        )

    def has_permission(self, request, obj, action):
        opts = self.opts
        code_name = f"{action}_{opts.model_name}"
        if obj:
            return request.user.has_perm(f"{opts.app_label}.{code_name}", obj)
        else:
            return self.get_model_objects(request).exists()

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser or self.is_user_admin(request.user):
            return True

        return self.has_permission(request, obj, "view")

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or self.is_user_admin(request.user):
            return True

        return self.has_permission(request, obj, "change")

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or self.is_user_admin(request.user):
            return True

        return self.has_permission(request, obj, "delete")

    def obj_perms_manage_view(self, request, object_pk):
        if not request.user.has_perm(
            "guardian.change_userobjectpermission"
        ) or not request.user.has_perm("guardian.change_groupobjectpermission"):
            post_url = reverse("admin:index", current_app=self.admin_site.name)
            return redirect(post_url)

        return super().obj_perms_manage_view(request, object_pk)

    def changed_fields(self, obj):
        if obj.prev_record:
            delta = obj.diff_against(obj.prev_record)
            return ", ".join([change.field for change in delta.changes])
        return None

    changed_fields.short_description = "Changed fields"


class ReportAdmin(admin.ModelAdmin):
    form = ReportModelForm
    ordering = ["-created_at"]
    list_display = [
        "hash_id",
        "output_file",
        "get_template_title",
        "user",
        "status",
        "created_at",
    ]
    search_fields = ["output_file", "hash_id"]
    list_filter = ["user", "template__title", "status", "created_at", "updated_at"]
    exclude = ["output_file"]
    readonly_fields = [
        "input_args",
        "download_pdf_button",
        "output_content_button",
        "updated_at",
        "created_at",
        "hash_id",
        "id",
    ]

    @admin.display(description="Template", ordering="template__title")
    def get_template_title(self, obj):
        return obj.template.title

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if "user" in form.base_fields:
            form.base_fields["user"].initial = request.user
            form.base_fields["user"].disabled = True
        return form

    def download_pdf_button(self, obj):
        if obj.status == "G":
            path = f"/files/{obj.output_file}.pdf"
            return format_html(
                '<a href="{}" target="_blank" class="button" style="background-color: '
                "#0A74DA; color: #FFF; padding: 5px 10px; border-radius: 3px; "
                'text-decoration: none;">Download</a>',
                path,
            )
        else:
            return "Not Available"

    download_pdf_button.short_description = "PDF"

    def output_content_button(self, obj):
        if obj.pk:
            return format_html(
                '<a href="{}" target="_blank" class="button" style="background-color: '
                "#0A74DA; color: #FFF; padding: 5px 10px; border-radius: 3px; "
                'text-decoration: none;">Download</a>',
                reverse("admin:download_html_view", args=[obj.pk]),
            )
        else:
            return "Not Available"

    output_content_button.short_description = "HTML"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:report_id>/download/",
                self.admin_site.admin_view(download_html_view),
                name="download_html_view",
            )
        ]
        return custom_urls + urls


custom_admin.register(Report, ReportAdmin)
custom_admin.register(User, UserAdmin)
custom_admin.register(Group, GroupAdmin)
custom_admin.register(Template, TemplateAdmin)
custom_admin.register(Database, DatabaseAdmin)

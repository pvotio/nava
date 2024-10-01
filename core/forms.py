from django import forms
from django_ace import AceWidget

from core.models import Argument, Template


class TemplateModelForm(forms.ModelForm):
    html_template = forms.CharField(
        widget=AceWidget(
            mode="html",
            theme="nord_dark",
            wordwrap=True,
            showprintmargin=True,
            width="800px",
            height="300px",
        )
    )
    python_script = forms.CharField(
        widget=AceWidget(
            mode="python",
            theme="nord_dark",
            wordwrap=True,
            showprintmargin=True,
            width="800px",
            height="300px",
        )
    )
    python_validation_script = forms.CharField(
        widget=AceWidget(
            mode="python",
            theme="nord_dark",
            wordwrap=True,
            showprintmargin=True,
            width="800px",
            height="300px",
        )
    )

    class Meta:
        model = Template
        fields = "__all__"


class ReportModelForm(forms.ModelForm):
    output_content = forms.CharField(
        widget=AceWidget(
            mode="html",
            theme="nord_dark",
            wordwrap=True,
            showprintmargin=True,
            width="800px",
            height="300px",
            readonly=True,
        )
    )

    class Meta:
        model = Template
        fields = "__all__"


class ReportGenerationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        template_id = kwargs.pop("template_id", None)
        super().__init__(*args, **kwargs)

        if template_id:
            template = Template.objects.get(pk=template_id)
            arguments = Argument.objects.filter(report=template)
            for arg in arguments:
                self.fields[arg.name] = forms.CharField(required=True, label=arg.name)

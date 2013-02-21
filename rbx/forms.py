from django import forms
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, HTML

from rbx.models import UserProfile, Project, Invitation, Box, \
    OperatingSystem, EXECUTOR_SOURCE_TYPE

PROJECT_VISIBILITY = (
    ('public', mark_safe('<i class="icon-unlock icon-large"></i> Anyone can \
                        see the project. You can choose who can modify it.')),
    ('private', mark_safe('<i class="icon-lock icon-large"></i> You can \
                        choose who can see and modify the project.')),
)


class HomeSignupForm(forms.Form):
    name = forms.CharField(max_length=100, label='',
        widget=forms.TextInput(attrs={'placeholder': 'Pick a username'}))
    email = forms.EmailField(label='',
        widget=forms.TextInput(attrs={'placeholder': 'Your email address'}))
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={
        'placeholder': 'Create a password'}))


class RequestInviteForm(forms.ModelForm):

    class Meta:
        model = Invitation

    email = forms.EmailField(label='',
        widget=forms.TextInput(attrs={'class': 'input-block-level',
                                      'required': 'required',
                                      'placeholder': 'Your email address'}))


class NewProjectForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(NewProjectForm, self).__init__(*args, **kwargs)
        self.fields = {
            'name': forms.CharField(),
            'owner': forms.ModelChoiceField(
                        # TODO: Add user's teams
                        UserProfile.objects.filter(pk=user.pk),
                        empty_label=None),
            'visibility': forms.ChoiceField(choices=PROJECT_VISIBILITY,
                                            widget=forms.RadioSelect,
                                            initial='public',
            ),
        }

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.form_action = reverse('new_project')
        self.helper.html5_required = True
        self.helper.layout = Layout(
            Field('name', css_class='input-xlarge'),
            'owner',
            'visibility',
            Div(
                Div(
                    Submit('create_project', 'Create project',
                            css_class="btn-primary"),
                    css_class='controls',
                ),
                css_class='controls-group',
            ),
        )

    def clean_name(self):
        slug = slugify(self.cleaned_data['name'])
        user = self.cleaned_data['owner']
        if len(Project.objects.filter(slug=slug, owner=user)):
            raise forms.ValidationError(
                'Similar name already exists on this account')
        return self.cleaned_data['name']


class EditProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ('name', 'description', 'public')

    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'input-block-level',
                   'required': 'required'}))
    description = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'class': 'input-block-level',
            'placeholder': 'Add project description...'}))
    public = forms.BooleanField(required=False)


class BoxForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')
        action = kwargs.pop('action')
        form_class = 'form_class' in kwargs and kwargs.pop('form_class') or ''
        super(BoxForm, self).__init__(*args, **kwargs)

        self.fields['project'] = forms.ModelChoiceField(Project.objects,
                                    widget=forms.HiddenInput(),
                                    initial=project)
        self.fields['repository_type'] = forms.ChoiceField(
                                            choices=EXECUTOR_SOURCE_TYPE)
        self.fields['os'] = forms.ModelChoiceField(OperatingSystem.objects,
                                                   empty_label=None,
                                                   label='Operating System')
        self.fields['lifetime'] = forms.DecimalField(min_value=1,
                                    max_value=120,
                                    initial=3,
                                    help_text='minute(s)',
                                    label='Max run time')
        self.fields['reload-location'] = forms.CharField(max_length=120, required=False,
                                                        widget=forms.HiddenInput())

        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal ' + form_class
        self.helper.form_action = action
        self.helper.html5_required = True
        self.helper.help_text_inline = True
        self.helper.layout = Layout(
            'project',
            Field('name', css_class='input-block-level'),
            Field('description', css_class='input-block-level'),
            Field('lifetime', css_class='input-mini'),
            Div(
                'repository_type',
                'source_repository',
                css_class='input-append input-xlarge'
            ),
            Field('os', css_class='input-block-level'),
            Field('before_run', css_class='input-block-level'),
            Field('run_command', css_class='input-block-level'),
            Field('after_run', css_class='input-block-level'),
            'disabled',
            Div(
                Div(
                    Submit('save_box', 'Save box and add parameters',
                            css_class="btn-primary"),
                    css_class='controls unfragmented',
                ),
                css_class='controls-group',
            ),
            Field('reload-location', data_reload_populate='name'),
        )

    class Meta:
        model = Box

class RunForm(forms.Form):

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.html5_required = True
    helper.help_text_inline = True
    helper.layout = Layout(
        HTML('<p><small>No parameters available.</small></p>'),
        Submit('run_project', 'Run project', css_class='btn-primary')
    )

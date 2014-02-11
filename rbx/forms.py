import re
from json import loads
from django import forms
from django.db.models import Max
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div, HTML, Button
from crispy_forms.bootstrap import PrependedText

from settings import EDIT_RIGHT
from rbx.models import UserProfile, Project, Invitation, Box, BoxParam, System

PROJECT_VISIBILITY = (
    ('public', mark_safe('<i class="icon-unlock icon-large"></i> Anyone can \
                        see the project. You can choose who can modify it.')),
    ('private', mark_safe('<i class="icon-lock icon-large"></i> You can \
                        choose who can see and modify the project.')),
)

PARAM_TEXT_SUBTYPE = (
    ('CharField', 'Plain text'),
    #('TextField', 'Paragraph text'),
    #('DateField', 'Date'),
    #('TimeField', 'Time'),
    #('DateTimeField', 'Date and time'),
    ('EmailField', 'Email address'),
    #('IPAddressField', 'IP address'),
    ('SlugField', 'Slug'),
    ('URLField', 'URL'),
)

PARAM_NUMBER_SUBTYPE = (
    ('IntegerField', 'Integer'),
    ('DecimalField', 'Decimal'),
    ('FloatField', 'Float'),
)


class HomeSignupForm(forms.Form):
    name = forms.CharField(max_length=100, label='',
                           widget=forms.TextInput(attrs={'placeholder':
                                                         'Pick a username'}))
    email = forms.EmailField(label='',
                             widget=forms.TextInput(attrs={'placeholder':
                                                           'Your email address'}))
    password = forms.CharField(label='',
                               widget=forms.PasswordInput(attrs={'placeholder':
                                                                 'Create a password'}))


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

    name = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'input-block-level',
                   'required': 'required'}))
    description = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'class': 'input-block-level',
            'placeholder': 'Add project description...'}))
    public = forms.BooleanField(required=False)

    class Meta:
        model = Project
        fields = ('name', 'description', 'public')


class BoxForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')
        action = kwargs.pop('action')
        form_class = 'form_class' in kwargs and kwargs.pop('form_class') or ''
        super(BoxForm, self).__init__(*args, **kwargs)

        self.fields['project'] = forms.ModelChoiceField(Project.objects,
                                                        widget=forms.HiddenInput(),
                                                        initial=project)
        self.fields['system'] = forms.ModelChoiceField(System.objects,
                                                       empty_label=None)
        self.fields['lifetime'] = forms.DecimalField(min_value=1,
                                                     max_value=120,
                                                     initial=5,
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
                'source_type',
                'source_location',
                css_class='input-append'
            ),
            Field('system', css_class='input-block-level'),
            Div(
                HTML('<label class="control-label">Install software</label>'),
                HTML('<div id="system_software" class="controls">'
                        + 'Please select a system</div>'),
                css_class='control-group',
            ),
            HTML('{% include "box_command.html" with box_form=box_form %}'),
            Div(
                Field('command', css_class='input-block-level'),
                id='command-group',
                css_class='hide',
            ),
            'allow_runs',
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

    def __init__(self, *args, **kwargs):
        box = kwargs.pop('box')
        user = kwargs.pop('user')
        super(RunForm, self).__init__(*args, **kwargs)
        params = BoxParam.objects.filter(box=box).order_by('order')
        can_edit = box.project.is_allowed(user, EDIT_RIGHT)
        layout = []
        controls = []
        self.fields['lifetime'] = forms.DecimalField(min_value=1,
                                                     max_value=box.lifetime,
                                                     initial=box.lifetime,
                                                     help_text='minute(s)',
                                                     label='Max run time')
        layout.append(Field('lifetime', css_class='input-mini'))
        for param in params:
            prop = self.build_help(param)
            if can_edit:
                prop['help_text'] += ('<i class="icon-wrench space-left edit-param"' +
                                      ' data-toggle="tooltip"' +
                                      ' title="Edit"></i>')
            self.fields[param.name] = getattr(forms, param.subtype)(**prop)
            layout.append(Div(Field(param.name, css_class=param.css_class),
                              css_class="parameter", data_param="%d" % param.pk))
        layout.append(Div(id='new_param'))
        if can_edit:
            controls.append(HTML('<a href="{{ box.link }}/param/text" ' +
                                 'id="add_param" data-title="%s" class="btn space-right">%s</a>'
                                 % ('Parameter type', 'Add parameter')))
        if box.allow_runs:
            if user.is_authenticated():
                controls.append(Submit('run_project', 'Run project', css_class='btn btn-primary'))
            else:
                controls.append(HTML('<a href="%s" ' % reverse('login') +
                                   'class="btn btn-primary">Sign in to launch run</a>'))
        else:
            layout.append(HTML('<p><small>New runs are disabled.</small></p>'))
        if len(controls):
            layout.append(Div(Div(*controls, css_class='controls'), css_class='controls-group'))
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal require'
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.layout = Layout(*layout)

    def camelcase2separator(self, name, separator=' '):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1%s\2' % separator, name)
        return re.sub('([a-z0-9])([A-Z])', r'\1%s\2' % separator, s1).lower()

    def build_help(self, param):
        ''' Add details on field constraints and type
        '''
        help_text = [self.camelcase2separator(param.subtype)]
        constraints = loads(param.constraints)
        for name, value in constraints.items():
            if (name not in ('help_text', 'subtype', 'required', 'initial')
                    and value is not None and value != ''):
                help_text.append('%s: %s' % (name.replace('_', ' '), str(value)))
        constraints['help_text'] = ('<i class="icon-info-sign param-info" data-toggle="tooltip"' +
                                    ' title="%s"></i> %s' % (', '.join(help_text),
                                                             constraints.get('help_text', '')))
        return constraints

class ParamForm(forms.Form):

    def __init__(self, *args, **kwargs):
        box = kwargs.pop('box')
        action = kwargs.pop('action')
        param = 'param' in kwargs and kwargs.pop('param') or None
        new = 'new' in kwargs and kwargs.pop('new') or None
        super(ParamForm, self).__init__(*args, **kwargs)
        self.layout = []
        self.helper = FormHelper()
        self.helper.form_class = 'well form-horizontal'
        self.helper.html5_required = True
        self.helper.help_text_inline = True
        self.helper.form_action = action
        self.helper.form_id = 'fragment'
        self.helper.form_method = 'post'

        self.fields['box'] = forms.ModelChoiceField(Box.objects,
                                          widget=forms.HiddenInput(),
                                          initial=box)
        order = BoxParam.objects.filter(box=box).aggregate(Max('order')).get('order__max')
        order = order and order + 10 or 0
        self.fields['order'] = forms.IntegerField(initial=(param and param.order or order),
                                                  widget=forms.HiddenInput())
        self.fields['type'] = forms.CharField(initial=(param and param.field_type or new),
                                              widget=forms.HiddenInput())
        self.layout.append('order')
        self.layout.append('type')
        self.layout.append('box')
        self.layout.append('subtype')
        self.layout.append('parameter_name')
        self.layout.append(Field('initial', css_class='input-block-level',
                                 placeholder='Default value (optional)'))
        self.layout.append(Field('help_text', css_class='input-block-level',
                                 placeholder='Parameter meaning (optional)'))
        if param:
            self.render_existing(param)
        else:
            self.render_new(new)
        self.layout.append('required')
        self.layout.append(Div(Div(Button('delete_param', 'Delete parameter',
                                          css_class="delete_param confirm-action",
                                          data_confirm="Yes delete parameter!"),
                                   Submit('save_param', 'Save parameter',
                                          css_class="save_param"),
                                   css_class='controls'),
                               css_class='controls-group'))
        self.helper.layout = Layout(*self.layout)

    def render_existing(self, param):
        const = loads(param.constraints)
        self.fields['pk'] = forms.IntegerField(initial=param.pk, widget=forms.HiddenInput())
        self.fields['parameter_name'] = forms.SlugField(initial=param.name)
        self.fields['initial'] = forms.CharField(required=False,
                                       initial=const.get('initial'))
        self.fields['required'] = forms.BooleanField(initial=const.get('required', True),
                                                     required=False)
        self.fields['help_text'] = forms.CharField(required=False,
                                              initial=const.get('help_text', ''),
                                              widget=forms.Textarea())
        self.layout.append('pk')
        getattr(self, 'render_%s' % param.field_type)(const)

    def render_new(self, param_type):
        self.fields['parameter_name'] = forms.SlugField()
        self.fields['initial'] = forms.CharField(required=False)
        self.fields['required'] = forms.BooleanField(initial=True, required=False)
        self.fields['help_text'] = forms.CharField(required=False,
                                              widget=forms.Textarea())
        getattr(self, 'render_%s' % param_type)()

    def render_text(self, constraints=None):
        if not constraints:
            constraints = {}
        self.fields['subtype'] = forms.ChoiceField(choices=PARAM_TEXT_SUBTYPE)
        self.fields['min_length'] = forms.IntegerField(required=False,
                                                       initial=constraints.get('min_length'))
        self.fields['max_length'] = forms.IntegerField(required=False,
                                                       initial=constraints.get('max_length'))
        self.layout.append(Field('min_length', css_class='input-small',
                                 placeholder='Optional'))
        self.layout.append(Field('max_length', css_class='input-small',
                                 placeholder='Optional'))

    def render_number(self, constraints=None):
        if not constraints:
            constraints = {}
        self.fields['subtype'] = forms.ChoiceField(choices=PARAM_NUMBER_SUBTYPE)
        self.fields['min_value'] = forms.IntegerField(required=False,
                                             initial=constraints.get('min_value'))
        self.fields['max_value'] = forms.IntegerField(required=False,
                                             initial=constraints.get('max_value'))
        self.layout.append(Field('min_value', css_class='input-small',
                                 placeholder='Optional'))
        self.layout.append(Field('max_value', css_class='input-small',
                                 placeholder='Optional'))


class ProfileForm(forms.Form):

    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('profile')
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.layout = []
        fields = (('full_name', profile.user.first_name, 'user'),
                  ('company', profile.company, 'briefcase', None, '(or School)'),
                  ('website', profile.website, 'globe', forms.URLField),
                  ('location', profile.location, 'map-marker'),
                  ('gravatar_email', profile.gravatar_email, 'picture', forms.EmailField, '(private)'))
        for field in fields:
            self.build_field(*field)
        self.helper = FormHelper()
        self.helper.html5_required = True
        self.helper.help_text_inline = True
        self.helper.form_action = reverse('settings_profile')
        self.layout.append(Submit('update_profile', 'Update profile'))
        self.helper.layout = Layout(*self.layout)

    def build_field(self, name, initial, icon=None, field_class=None, help_text=''):
        if not field_class:
            field_class = forms.CharField
        placeholder = name.replace('_', ' ').capitalize()
        self.fields[name] = field_class(initial=initial, required=False, label='')
        if icon:
            self.layout.append(PrependedText(name, self.icon(icon),
                                             placeholder='%s %s' % (placeholder, help_text),
                                             css_class='input-xlarge'))
        else:
            self.layout.append(Field(name, placeholder='%s %s' % (placeholder, help_text)))

    def icon(self, name):
        return '<i class="icon-%s"></i> ' % name


class PasswordForm(forms.Form):

    current_password = forms.CharField(widget=forms.PasswordInput())
    new_password = forms.CharField(widget=forms.PasswordInput())
    repeat_new_password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username')
        super(PasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.html5_required = True
        self.helper.help_text_inline = True
        self.helper.form_action = reverse('settings_profile')
        self.helper.layout = Layout('current_password', 'new_password', 'repeat_new_password',
                                    Div(Div(Submit('update_password', 'Update password'),
                                            css_class='controls'),
                                        css_class='controls-group'))

    def clean_current_password(self):
        user = User.objects.get(username=self.username)
        if not user.check_password(self.cleaned_data['current_password']):
            raise forms.ValidationError('Current password mismatch')
        return self.cleaned_data['current_password']

    def clean(self):
        # TODO; use cracklib to check strength
        if self.cleaned_data['new_password'] != self.cleaned_data['repeat_new_password']:
            raise forms.ValidationError('New passwords mismatch')
        return self.cleaned_data

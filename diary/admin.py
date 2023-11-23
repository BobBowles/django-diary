from django.contrib import admin
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.admin import UserAdmin
from datetimewidget.widgets import DateWidget


# Register your models here.

from .models import Customer, Treatment, Resource, Entry

# crispy forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML, Fieldset



DATE_WIDGET_OPTIONS = {
    'minView': 2,
    'maxView': 4,
    'startView': 4,
}
CUSTOMER_HELP_TEXTS = {
    'email': 'Make sure you use a valid email.',
    'opt_out_entry_reminder_email':
        'Leave unchecked to receive diary reminder emails.',
    'opt_out_entry_change_email':
        'Leave unchecked to receive diary change emails.',
}



class CustomerBaseForm(forms.ModelForm):
    """
    Base form for displaying and altering Customer information.
    """


    class Meta:
        abstract = True

        model = Customer
        fields = (
            'username',
            'gender',
            'title',
            'first_name',
            'last_name',
            'phone',
            'email',
            'opt_out_entry_reminder_email',
            'opt_out_entry_change_email',
            'date_of_birth',
            'notes',
        )
        widgets = {
            'date_of_birth': DateWidget(
                bootstrap_version=3,
                options=DATE_WIDGET_OPTIONS,
            ),
        }
        exclude = (
            'staff_status',
            'superuser_status',
        )
        help_texts = CUSTOMER_HELP_TEXTS


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()


    def initialise_crispy(self, display_password=False):
        """
        Perform the initialisation to enable crispy forms. This emulates the
        admin Customer form layouts. Invoke from subclass __init__() method.

        display_password enables subclasses to toggle display of password
        fields.
        """
        self.helper.layout = Layout(
            Fieldset('',
                'username',
                Row(
                    Column('first_name', css_class='form-group col-md-6 mb-0'),
                    Column('last_name', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row',
                ),
                Row(
                    Column('password1', css_class='form-group col-md-6 mb-0'),
                    Column('password2', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row',
                ) if display_password else None,
                Row(
                    Column('gender', css_class='form-group col-md-6 mb-0'),
                    Column('title', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row',
                ),
            ),
            Fieldset('Contact Info',
                'phone',
                'email',
                Row(
                    Column(
                        'opt_out_entry_reminder_email',
                        css_class='form-group col-md-6 mb-0',
                    ),
                    Column(
                        'opt_out_entry_change_email',
                        css_class='form-group col-md-6 mb-0',
                    ),
                    css_class='form-row',
                ),
            ),
            Fieldset('Personal Info',
                'date_of_birth',
                'notes',
            ),
            Row(
                Column(
                    HTML(''),
                    css_class='form-group col-md-11 mb-0',
                ),
                Column(
                    Submit(
                        'save',
                        'Save',
                        css_class='save btn btn-default diarybutton'
                    ),
                    css_class='form-group col-md-1 mb-0',
                ),
                css_class='form-row',
            )
        )



class CustomerCreationForm(CustomerBaseForm):
    """
    A form for creating new Customers. Includes all the required
    fields, plus a repeated password.
    """
    password1 = forms.CharField(
        label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)


    class Meta(CustomerBaseForm.Meta):
        abstract = False


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initialise_crispy(display_password=True)


    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2


    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(CustomerCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user



class CustomerChangeForm(CustomerBaseForm):
    """
    A form for updating Customers.

    Customers can change their non-security-related information using this form.

    Excludes security-sensitive information like password and privileges, which
    are changed by other means (needs staff privilege except for self password
    change).
    """


    class Meta(CustomerBaseForm.Meta):
        abstract = False
        exclude = (
            'password',
            'staff_status',
            'superuser_status',
            'is_active',
        )


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initialise_crispy(display_password=False)


class CustomerAdmin(UserAdmin):
    # The forms to add and change user instances
    form = CustomerChangeForm
    add_form = CustomerCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username', 'first_name', 'last_name', )
#    list_filter = ('is_admin',)
    list_filter = ()
    fieldsets = (
        (None, {
            'fields': (
                'username',
                ('first_name', 'last_name'),
                ('title', 'gender'),
                #'password', # excluded from change form so excluded here too
                )
            }
        ),
        ('Contact Info', {
            'fields': (
                'phone',
                'email',
                ('opt_out_entry_reminder_email', 'opt_out_entry_change_email'),
                )
            }
        ),
        ('Personal Info', {
            'fields': (
                'date_of_birth',
                'notes',
                )
            }
        ),
#        ('Permissions', {'fields': ('is_admin',)}),
    )
#    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
#    # overrides get_fieldsets to use this attribute when creating a user.
#    add_fieldsets = (
#        (None, {
#            'classes': ('wide',),
#            'fields': ('username', 'password1', 'password2')}
#        ),
#    )
    search_fields = ('username', 'first_name', 'last_name')
    ordering = ('first_name', 'last_name', )
    filter_horizontal = ()


admin.site.register(Customer, CustomerAdmin)


@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'min_duration', 'resource_required',]
    list_editable = ['min_duration', 'resource_required',]
    list_display_links = ['name',]
    ordering = ['name', 'min_duration',]


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'fg_color', 'bg_color', 'enabled',]
    list_editable = ['description', 'fg_color', 'bg_color', 'enabled',]
    list_display_links = ['name',]
    ordering = ['name',]


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = [
        'creator',
        'date',
        'time',
        'customer',
    ]
    list_filter = [
        'creator',
        'customer',
        'date',
    ]
    fieldsets = (
        (None, {
            'fields': (
                'creator',
                'date',
                'time',
                'customer',
             )
       }),
       ('Details', {
            'fields': (
                'treatment',
                'resource',
                'duration',
                'notes',
            )
       }),
       ('Administration', {
            'fields': (
                'cancelled',
                'no_show',
            )
       }),
    )
    ordering = ('date', 'time', )

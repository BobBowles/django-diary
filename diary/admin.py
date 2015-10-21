from django.contrib import admin
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.admin import UserAdmin
from datetimewidget.widgets import DateWidget


# Register your models here.

from .models import Customer, Treatment, Resource, Entry



DATE_WIDGET_OPTIONS = {
    'minView': 2,
    'maxView': 4,
    'startView': 4,
}


CUSTOMER_HELP_TEXTS = {
    'email': 'Make sure you use a valid email.',
}



class CustomerCreationForm(forms.ModelForm):
    """
    A form for creating new Customers. Includes all the required
    fields, plus a repeated password.
    """
    password1 = forms.CharField(
        label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)


    class Meta:
        model = Customer
        fields = (
            'username',
            'title',
            'first_name',
            'last_name',
            'email',
            'phone',
            'date_of_birth',
            'gender',
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



class CustomerChangeForm(forms.ModelForm):
    """
    A form for updating Customers. 
    
    Customers can change their non-security-related information using this form.
    
    Excludes security-sensitive information like password and privileges, which 
    are changed by other means (needs staff privilege except for self password 
    change).
    """


    class Meta:
        model = Customer
        fields = (
            'username',
            'title',
            'first_name',
            'last_name',
            'email', 
            'phone',
            'date_of_birth', 
            'gender',
            'notes',
        )
        widgets = {
            'date_of_birth': DateWidget(
                bootstrap_version=3,
                options=DATE_WIDGET_OPTIONS,
            ),
        }
        exclude = (
            'password',
            'staff_status',
            'superuser_status',
            'is_active',
        )
        help_texts = CUSTOMER_HELP_TEXTS



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
                'first_name',
                'last_name',
                #'password', # excluded from change form so excluded here too
            )
        }),
        ('Contact info', {
            'fields': (
                'email',
                'phone',
            )
        }),
        ('Personal info', {
            'fields': (
                'title',
                'date_of_birth',
                'gender',
                'notes',
            )
        }),
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
    search_fields = ('username',)
    ordering = ('first_name', 'last_name', )
    filter_horizontal = ()


admin.site.register(Customer, CustomerAdmin)


admin.site.register(Treatment)
admin.site.register(Resource)


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


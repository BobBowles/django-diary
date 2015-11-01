from django import forms
from .models import Entry, Customer
from datetimewidget.widgets import (
    TimeWidget,
    DateWidget,
)
from . import settings
from .widgets import RelatedFieldWidgetCanAdd



TIME_FORMATS = ['%H:%M', '%I:%M%p', '%I:%M %p',]
DURATION_FORMATS = ['%H:%M',]
DATE_WIDGET_OPTIONS = {
    # NB convert between conventions for numbering days (widget uses Sunday=0)
    'weekStart': ((settings.DIARY_FIRST_DAY_OF_WEEK + 1) % 7),
    'minView': 2,
    'maxView': 3,
}
TIME_WIDGET_OPTIONS = {
    'format': 'HH:ii P' if settings.DIARY_SHOW_MERIDIAN else 'hh:ii',
    'showMeridian': settings.DIARY_SHOW_MERIDIAN,
    'minuteStep': 15,
}
DURATION_WIDGET_OPTIONS = {
    'format': 'hh:ii',
    'minuteStep': 15,
}



class EntryForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        """
        Override constructor to allow customer field to be configurably visible.
        """
        exclude_customer = kwargs.pop('exclude_customer', False)
        super(EntryForm, self).__init__(*args, **kwargs)
        if exclude_customer:
            del self.fields['customer']
        else:
            # make sure the customer selection popup has some sort of sane order
            self.fields['customer'].queryset = Customer.objects.all().order_by(
                'first_name', 
                'last_name',
            )



    class Meta:
        model = Entry
        fields = (
            'customer',
            'date',
            'time',
            'treatment',
            'duration',
            'resource',
            'notes',
        )
        widgets = {
            # override customer widget attributes AFTER creating the form
            'customer': RelatedFieldWidgetCanAdd(Customer),
            'date': DateWidget(
                bootstrap_version=3,
                options=DATE_WIDGET_OPTIONS,
            ),
            'time': TimeWidget(
                bootstrap_version=3,
                options=TIME_WIDGET_OPTIONS,
            ),
            'duration': TimeWidget(
                bootstrap_version=3,
                options=DURATION_WIDGET_OPTIONS,
            ),
        }
        input_formats = {
            'time': TIME_FORMATS,
            'duration': DURATION_FORMATS,
        }


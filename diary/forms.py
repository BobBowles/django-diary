from django import forms
from .models import Entry, Customer
from datetimewidget.widgets import (
    TimeWidget,
    DateWidget,
)
from .widgets import RelatedFieldWidgetCanAdd



TIME_FORMATS = ['%H:%M', '%I:%M%p', '%I:%M %p',]
DURATION_FORMATS = ['%H:%M',]
DATE_WIDGET_OPTIONS = {
#    'todayBtn': True,
    'minView': 2,
    'maxView': 3,
}
TIME_WIDGET_OPTIONS = {
    'format': 'HH:ii P',
    'showMeridian': True,
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


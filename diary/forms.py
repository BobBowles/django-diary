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
        else:           # add real widget attributes AFTER it is instantiated
            self.fields['customer'].widget.related_url = (
                'diary:customer_add' if self.instance
                else "diary:customer_add_no_entry"
            )
            self.fields['customer'].widget.related_kwargs = (
                {'entry_pk': self.instance.pk} if self.instance
                else None
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
            'customer': RelatedFieldWidgetCanAdd(Customer), # use defaults here
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


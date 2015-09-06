from django import forms
from .models import Entry
from datetimewidget.widgets import (
    TimeWidget,
    DateWidget,
)


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

    class Meta:
        model = Entry
        fields = (
            'date',
            'time',
            'duration',
            'title',
            'snippet',
            'body',
            'remind',
        )
        widgets = {
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


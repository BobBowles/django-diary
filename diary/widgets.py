from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.forms import widgets
from django.conf import settings
from django.utils.translation import ugettext as _




class RelatedFieldWidgetCanAdd(widgets.Select):
    """
    Supplements the standard Select widget behaviour by adding an 'add' button.
    
    Added related_kwargs for targeted redirection.
    
    Adapted from:
    http://stackoverflow.com/questions/28068168/django-adding-an-add-new-button-for-a-foreignkey-in-a-modelform
    """


    def __init__(
        self, 
        related_model, 
        related_url=None, 
        related_kwargs=None, *args, **kwargs
    ):

        super(RelatedFieldWidgetCanAdd, self).__init__(*args, **kwargs)

        if not related_url:         # construct a url for the default admin site
            rel_to = related_model
            info = (rel_to._meta.app_label, rel_to._meta.object_name.lower())
            related_url = 'admin:%s_%s_add' % info
            related_kwargs = {}

        # Be careful that here "reverse" is not allowed
        self.related_url = related_url
        self.related_kwargs = related_kwargs


    def render(self, name, value, *args, **kwargs):
        self.related_url = reverse(
            self.related_url, 
            kwargs=self.related_kwargs,
        )
        output = [
            super(RelatedFieldWidgetCanAdd, self).render(
                name, 
                value, 
                *args, 
                **kwargs
            )
        ]
        output.append('<a href="%s" class="add-another" id="add_id_%s" onclick="return showAddAnotherPopup(this);"> ' % \
            (self.related_url, name))
        output.append('<img src="%sadmin/img/icon_addlink.gif" width="10" height="10" alt="%s"/></a>' % (settings.STATIC_URL, _('Add Another')))                                                                                                                               
        return mark_safe(''.join(output))


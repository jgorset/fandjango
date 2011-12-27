from django import template
from django.conf import settings
register = template.Library()

@register.tag
def facebook_init(parser, token):
    nodelist = parser.parse(('endfacebook',))
    parser.delete_first_token()
    return FacebookNode(nodelist)

class FacebookNode(template.Node):
    """Allow code to be added inside the facebook asynchronous closure. """
    def __init__(self, nodelist):
        try:
            app_id = settings.FACEBOOK_APPLICATION_ID
        except AttributeError:
            raise template.TemplateSyntaxError, "%r tag requires FACEBOOK_APP_ID to be configured." \
                % token.contents.split()[0]
        self.app_id   = app_id
        self.nodelist = nodelist

    def render(self, context):
        t = template.loader.get_template('fandjango/facebook_init.html')
        code = self.nodelist.render(context)
        custom_context = context
        custom_context['code'] = code
        custom_context['app_id'] = self.app_id
        return t.render(context)

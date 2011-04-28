from utils import redirect_to_facebook_authorization
from settings import FACEBOOK_APPLICATION_URL

def authorize_application(request):
    return redirect_to_facebook_authorization(
        redirect_uri = request.GET['redirect_uri'] if request.GET.has_key('redirect_uri') else FACEBOOK_APPLICATION_URL
    )

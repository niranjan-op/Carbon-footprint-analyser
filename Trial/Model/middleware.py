from django.contrib import messages
from django.conf import settings
from django.shortcuts import redirect
from django.urls import resolve

class LoginRequiredMiddleware:
    """
    Middleware to enhance the login_required decorator by adding a message
    when redirecting to login page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code executed before the view
        response = self.get_response(request)
        
        # Code executed after the view
        # If we're about to redirect to login and it's not a direct login/logout request
        if (not request.user.is_authenticated and 
            response.status_code == 302 and 
            response.url.startswith(settings.LOGIN_URL) and
            not request.path.startswith(settings.LOGIN_URL) and
            not request.path.startswith('/logout')):
            
            # Get the current view's name to provide context in the message
            try:
                current_url = resolve(request.path)
                view_name = current_url.url_name
                
                if view_name:
                    # Create a user-friendly name
                    friendly_name = view_name.replace('_', ' ').title()
                    messages.info(request, f"Please log in to access the {friendly_name} page.")
                else:
                    messages.info(request, "Please log in to continue.")
            except:
                messages.info(request, "Please log in to continue.")
        
        return response

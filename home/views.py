from django.shortcuts import render, render_to_response

# Create your views here.


def home(request):
    """
    A noddy home page for testing/development purposes.
    """
    return render_to_response('diary/home.html', {'user': request.user})


from django.shortcuts import render

# Create your views here.


def home(request):
    """
    A noddy home page for testing/development purposes.
    """
    return render(request, 'diary/home.html', {'user': request.user})

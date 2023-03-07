from django.shortcuts import render


def handle_not_found(request, exception):
    return render(request, 'errors/404.html')


def handle_permission_denied(request, exception):
    return render(request, 'errors/403.html')


def handle_server_error(request):
    return render(request, 'errors/500.html')

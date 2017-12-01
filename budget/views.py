from django.shortcuts import render


def home_page(request):
    return render(request, 'home.html')


def budget_page(request):
    if request.user.is_authenticated:
        return render(request, 'budget.html')
    else:
        return home_page(request)

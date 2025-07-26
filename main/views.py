from django.shortcuts import render
from main.forms import ContactForms
from django.shortcuts import render, redirect

# Create your views here.
def index(request):
    return render(request, 'index.html')

def contact(request):
    form = ContactForms()
    if request.method == 'POST':
        form = ContactForms(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    return render(request, 'contact.html', {'form': form})


def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

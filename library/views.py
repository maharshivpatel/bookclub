from django.http import HttpResponse
from django.shortcuts import redirect, render
from library.models import Library, Librarian
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


def guest_view(request):

    if Library.objects.count() == 0 and Librarian.objects.count() == 0:
        messages.add_message(request, messages.SUCCESS, 'Start setup for your Library')
        return redirect('usercreate')

    if request.user.is_anonymous:
        return redirect('userlogin')

    if request.user.is_authenticated and not request.user.library:
        messages.add_message(request, messages.INFO, 'Please create Library to continue')
        return redirect('librarycreate')
    
    if request.user.is_authenticated and request.user.library:
        messages.add_message(request, messages.INFO, f'Welcome to {request.user.library}')
        return redirect('books')

    return HttpResponse('<h1>Woah, Our Developer made a mistake you should never see this message.</h1>')


def usercreate_view(request):

    guest = {
      'p_btn_txt': 'Create',
      's_btn_txt': 'login',
      's_url_name': 'userlogin'
    }

    if request.user.is_authenticated:
        messages.add_message(request, messages.INFO, 'You are already logged in as user.')
        return redirect('books')

    messages.add_message(request, messages.INFO, 'Please Enter Details to create Librarian')
    return render(request, 'library/guest_flow.html',  {'guest': guest})


def userlogin_view(request):

    guest = {
      'p_btn_txt': 'Login',
      's_btn_txt': 'create user',
      's_url_name': 'usercreate'
    }

    if request.user.is_authenticated:
        messages.add_message(request, messages.INFO, 'You are already logged in as user.')
        return redirect('books')

    messages.add_message(request, messages.INFO, 'Please Login to continue')
    return render(request, 'library/guest_flow.html', {'guest': guest})


def librarycreate_view(request):

    guest = {
      'p_btn_txt': 'Create',
      's_btn_txt': 'select library',
      's_url_name': 'libraryselect'
    }

    if request.user.library:
        messages.add_message(request, messages.INFO, f'You are already a librarian at {request.user.library}.')
        return redirect('books')

    messages.add_message(request, messages.INFO, 'Please enter details to create Librarian')
    return render(request, 'library/guest_flow.html',  {'guest': guest})


def libraryselect_view(request):

    guest = {
      'p_btn_txt': 'Select',
      's_btn_txt': 'create library',
      's_url_name': 'librarycreate'
    }

    if request.user.library:
        messages.add_message(request, messages.INFO, f'You are already a librarian at {request.user.library}.')
        return redirect('books')

    messages.add_message(request, messages.INFO, 'Please Select Library to continue')
    return render(request, 'library/guest_flow.html', {'guest': guest})

@login_required
def profile_view(request):
    page = {
        'title': 'Profile',
        'button': {
            'btn_text':'Back',
            'button_action': "redirect",
            'url_name': 'transactions',
            'css_btn_type': 'light',
        }
    }

    return render(request, 'library/page_edit.html', {'page': page})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Please have been logged out successfully.')
    return redirect('userlogin')
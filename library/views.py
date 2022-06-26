from django.http import HttpResponse
from django.shortcuts import redirect, render
from library.models import Library, Librarian
from bookclub.utils import load_json
from library.forms import LibrarianCreationForm, LibrarianLoginForm, LibraryForm, LibrarySelectForm, LibrarianUpdateForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def guest_view(request):

    if Library.objects.count() == 0 and Librarian.objects.count() == 0:
        return redirect('usercreate')

    if request.user.is_anonymous:
        return redirect('userlogin')

    if request.user.is_authenticated and not request.user.library:
        return redirect('librarycreate')
    
    if request.user.is_authenticated and request.user.library:
        messages.add_message(request, messages.INFO, f'Welcome to {request.user.library}')
        return redirect('books')

    return HttpResponse('<h1>Woah, Our Developer made a mistake you should never see this message.</h1>')


def usercreate_view(request):

    pagedata = load_json(folder='library',file='usercreate')

    if request.user.is_authenticated:
        messages.add_message(request, messages.INFO, 'You are already logged in as user.')
        return redirect('books')

    if request.method == 'POST':
        form = LibrarianCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('librarycreate')
    else:
        form = LibrarianCreationForm()

    messages.add_message(request, messages.INFO, 'Please create user to continue')
    return render(request, 'library/guest_flow.html',  {**pagedata, 'form': form})


def userlogin_view(request):

    pagedata = load_json(folder='library',file='userlogin')

    if request.user.is_authenticated:
        messages.add_message(request, messages.INFO, 'You are already logged in as user.')
        return redirect('books')

    if request.method == 'POST':

        form = LibrarianLoginForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=raw_password)

            if user is not None:
                login(request, user)

                if not user.library:
                    return redirect('librarycreate')

                messages.add_message(request, messages.INFO, f'Welcome to {request.user.library}')
                return redirect('books')

        messages.add_message(request, messages.ERROR, 'Username or Password is Incorrect.')

        return render(request, 'library/guest_flow.html', {**pagedata, 'form': form})

    else:
        messages.add_message(request, messages.INFO, 'Please Login to continue')
        form = LibrarianLoginForm()

    return render(request, 'library/guest_flow.html', {**pagedata, 'form': form})


def librarycreate_view(request):

    pagedata = load_json(folder='library',file='librarycreate')

    if request.user.library:
        messages.add_message(request, messages.INFO, f'You are already a librarian at {request.user.library}.')
        return redirect('books')

    if request.method == 'POST':
        
        form = LibraryForm(request.POST)
        
        if form.is_valid():
            
            formobj = form.save()
            request.user.library = formobj
            request.user.save()
            
            return redirect('books')

        return render(request, 'library/guest_flow.html', {**pagedata, 'form': form})

    else:
        form = LibraryForm()

    messages.add_message(request, messages.INFO, 'Please enter details to create Library')

    return render(request, 'library/guest_flow.html',  {**pagedata, 'form': form} )


def libraryselect_view(request):

    pagedata = load_json(folder='library', file='libraryselect')

    if request.user.library:
        messages.add_message(request, messages.INFO, f'You are already a librarian at {request.user.library}.')
        return redirect('books')

    if request.method == 'POST':
        form = LibrarySelectForm(request.POST)

        if form.is_valid():

            if form.cleaned_data.get('library'):
            
                request.user.library = form.cleaned_data.get('library')
                request.user.save()
            
                messages.add_message(request, messages.INFO, f'You have selected {request.user.library} Library.')
            
                return redirect('books')
        
        messages.add_message(request, messages.WARNING, 'Please Select your Library.')
        
        return render(request, 'library/guest_flow.html', {**pagedata, 'form': form} )

    else:
        form = LibrarySelectForm()
        messages.add_message(request, messages.SUCCESS, 'Please Select your Library.')

    return render(request, 'library/guest_flow.html', {**pagedata, 'form': form} )


@login_required
def profile_view(request):
    
    pagedata = load_json(folder='library',file='profile')

    librarian = Librarian.objects.get(id = request.user.id)

    form = LibrarianUpdateForm(request.POST or None, request.FILES or None, instance=librarian)
    
    if form.is_valid():
        form.save()
        messages.add_message(request, messages.SUCCESS, 'Information Saved.')
    
        return redirect('books')

    return render(request, 'library/page_edit.html', {**pagedata, 'form': form})


@login_required
def library_view(request):

    pagedata = load_json(folder='library',file='library')

    library = Library.objects.get(id = request.user.library.id)

    form = LibraryForm(request.POST or None, request.FILES or None, instance=library)
    
    if form.is_valid():
        form.save()
        messages.add_message(request, messages.SUCCESS, 'Information Saved.')
    
        return redirect('books')

    return render(request, 'library/page_edit.html', {**pagedata, 'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.add_message(request, messages.SUCCESS, 'Please have been logged out successfully.')
    return redirect('userlogin')
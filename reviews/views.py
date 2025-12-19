from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout

class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        # Tell Django to use this Model to save data
        model = get_user_model()
        # And show this fields
        fields = ('username',)

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # stick session cookie to user to have his information
            login(request, user)
            return redirect('main')
    else:
        form = SignupForm()

    return render(request, 'reviews/signup.html', {'form': form})

def main(request):
    return render(request, 'reviews/main.html')

def log_out(request):
    logout(request)
    return redirect('login')
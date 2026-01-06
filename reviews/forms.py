from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Ticket, Review

class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username',)

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['headline', 'rating', 'body']
        labels = {
            'headline': 'Titre',
            'rating': 'Note (0 à 5)',
            'body': 'Commentaire',
        }
        widgets = {
            'rating': forms.RadioSelect(
                choices=[(i, str(i)) for i in range(6)]
            ),
        }

class FollowUserForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=150)
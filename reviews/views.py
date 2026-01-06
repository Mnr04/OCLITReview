from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout
from django import forms
from .models import Ticket, Review, UserFollows, User

from itertools import chain
from django.db.models import CharField, Value


""" Forms """
class SignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        # Tell Django to use this Model to save data
        model = get_user_model()
        # And show this fields
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

class FollowUserForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=150)

""" Authentification """
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
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'reviews/main.html')

def log_out(request):
    logout(request)
    return redirect('login')

""" Ticket """
def create_ticket(request):

    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('main')
    else:
        form = TicketForm()

    return render(request, 'reviews/create_ticket.html', {'form': form})

def edit_ticket(request, ticket_id):

    if not request.user.is_authenticated:
        return redirect('login')

    ticket = get_object_or_404(Ticket, id=ticket_id)

    if ticket.user != request.user:
        return redirect('main')

    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('main')
    else:
        form = TicketForm(instance=ticket)

    return render(request, 'reviews/edit_ticket.html', {
        'form': form,
        'ticket': ticket}
        )

def delete_ticket(request, ticket_id):

    if not request.user.is_authenticated:
        return redirect('login')

    ticket = get_object_or_404(Ticket, id=ticket_id)

    if ticket.user == request.user:
        if request.method == 'POST':
            ticket.delete()
            return redirect('main')

    return redirect('main')

""" Review """
def create_review(request, ticket_id):

    if not request.user.is_authenticated:
        return redirect('login')

    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()
            return redirect('main')
    else:
        form = ReviewForm()

    return render(request, 'reviews/create_review.html', {'form': form, 'ticket': ticket})

def create_ticket_and_review(request):

    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES)
        review_form = ReviewForm(request.POST)

        if ticket_form.is_valid() and review_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()

            review = review_form.save(commit=False)
            review.ticket = ticket
            review.user = request.user
            review.save()

            return redirect('main')

    else:
        ticket_form = TicketForm()
        review_form = ReviewForm()

    context = {
        'ticket_form': ticket_form,
        'review_form': review_form,
    }
    return render(request, 'reviews/create_ticket_and_review.html', context)

def edit_review(request, review_id):

    if not request.user.is_authenticated:
        return redirect('login')


    review = get_object_or_404(Review, id=review_id)

    if review.user != request.user:
        return redirect('main')

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            return redirect('main')
    else:
        form = ReviewForm(instance=review)

    return render(request, 'reviews/edit_review.html', {
        'form': form,
        'review': review,
        'ticket': review.ticket}
        )

def delete_review(request, review_id):

    if not request.user.is_authenticated:
        return redirect('login')

    review = get_object_or_404(Review, id=review_id)

    if review.user == request.user:
        review.delete()
        return redirect('main')

    return redirect('main')

""" User Folow """
def follow_users(request):

    if not request.user.is_authenticated:
        return redirect('login')

    form = FollowUserForm()
    message = ""

    if request.method == 'POST':
        form = FollowUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user_to_follow = User.objects.get(username=username)

                if user_to_follow == request.user:
                    message = "Vous ne pouvez pas vous suivre vous-même."
                elif UserFollows.objects.filter(user=request.user, followed_user=user_to_follow).exists():
                    message = "Vous suivez déjà cet utilisateur."
                else:
                    UserFollows.objects.create(user=request.user, followed_user=user_to_follow)
                    return redirect('follow_users')

            except User.DoesNotExist:
                message = "Cet utilisateur n'existe pas."

    following = UserFollows.objects.filter(user=request.user)
    followers = UserFollows.objects.filter(followed_user=request.user)

    return render(request, 'reviews/follow_users.html', {
        'form': form,
        'following': following,
        'followers': followers,
        'message': message
    })

def unfollow_user(request, user_id):
    if not request.user.is_authenticated:
        return redirect('login')

    user_to_unfollow = get_object_or_404(User, id=user_id)
    UserFollows.objects.filter(user=request.user, followed_user=user_to_unfollow).delete()

    return redirect('follow_users')

""" MAIN VIEW """
def main(request):

    if not request.user.is_authenticated:
        return redirect('login')

    follows = UserFollows.objects.filter(user=request.user)
    followed_users_ids = []
    for follow in follows:
        followed_users_ids.append(follow.followed_user.id)

    tickets_me = Ticket.objects.filter(user=request.user)
    tickets_followed = Ticket.objects.filter(user__in=followed_users_ids)
    tickets = tickets_me | tickets_followed
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    reviews_me = Review.objects.filter(user=request.user)
    reviews_followed = Review.objects.filter(user__in=followed_users_ids)
    reviews_answers = Review.objects.filter(ticket__in=tickets_me)
    reviews = reviews_me | reviews_followed | reviews_answers
    reviews = reviews.distinct()
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))


    posts = sorted(
        chain(tickets, reviews),
        key=lambda post: post.time_created,
        reverse=True
    )

    return render(request, 'reviews/main.html', {'posts': posts})

""" My Post """

def posts(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # My tickets
    tickets = Ticket.objects.filter(user=request.user)
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    # My reviews
    reviews = Review.objects.filter(user=request.user)
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    posts = sorted(
        chain(tickets, reviews),
        key=lambda post: post.time_created,
        reverse=True
    )

    return render(request, 'reviews/posts.html', {'posts': posts})
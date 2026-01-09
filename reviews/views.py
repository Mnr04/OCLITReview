from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Ticket, Review, UserFollows, User, BlockedUser
from .forms import SignupForm, TicketForm, ReviewForm, FollowUserForm
from itertools import chain
from django.db.models import CharField, Value
from django.db import transaction


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main')
    else:
        form = SignupForm()
    return render(request, 'reviews/signup.html', {'form': form})


def log_out(request):
    logout(request)
    return redirect('login')


@login_required
def main(request):
    """
    Displays the news feed for the logged-in user.

    This view combines tickets and reviews from:
    - The user.
    - The users they follow.
    - Responses to the user's own tickets.

    Posts are sorted by creation date and marked to distinguish
    between tickets and reviews.

    Returns:
        HttpResponse: The 'feed.html' page with the list of posts.
    """
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

    my_reviewed_tickets = []
    for review in reviews_me:
        my_reviewed_tickets.append(review.ticket.id)

    posts = sorted(
        chain(tickets, reviews),
        key=lambda post: post.time_created,
        reverse=True
    )

    context = {
        'posts': posts,
        'my_reviewed_tickets': my_reviewed_tickets
    }

    return render(request, 'reviews/main.html', context)


@login_required
def posts(request):
    """
    Displays only the posts created by the current user.

    This view retrieves:
    - Tickets created by the user.
    - Reviews created by the user.

    The items are combined into a single list and sorted by date.
    """
    tickets = Ticket.objects.filter(user=request.user)
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    reviews = Review.objects.filter(user=request.user)
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    posts = sorted(
        chain(tickets, reviews),
        key=lambda post: post.time_created,
        reverse=True
    )
    return render(request, 'reviews/posts.html', {'posts': posts})


@login_required
def create_ticket(request):
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


@login_required
def create_ticket_and_review(request):
    """
    Allows the user to create a ticket and a review at the same time.

    This view handles two forms:
    - TicketForm: For the book/article details.
    - ReviewForm: For the review content.

    If both forms are valid, the ticket is saved first, and then the review
    is linked to it.
    """
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES)
        review_form = ReviewForm(request.POST)
        if ticket_form.is_valid() and review_form.is_valid():
            with transaction.atomic():
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

    context = {'ticket_form': ticket_form, 'review_form': review_form}
    return render(request, 'reviews/create_ticket_and_review.html', context)


@login_required
def create_review(request, ticket_id):
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
    return render(
        request, 'reviews/create_review.html', {'form': form, 'ticket': ticket}
        )


@login_required
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if ticket.user != request.user:
        return redirect('main')

    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('posts')
    else:
        form = TicketForm(instance=ticket)

    return render(
        request, 'reviews/edit_ticket.html', {'form': form, 'ticket': ticket}
        )


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if review.user != request.user:
        return redirect('main')

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            return redirect('posts')
    else:
        form = ReviewForm(instance=review)

    return render(request, 'reviews/edit_review.html', {
        'form': form,
        'review': review,
        'ticket': review.ticket
    })


@login_required
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request == 'POST':
        if ticket.user == request.user:
            ticket.delete()
    return redirect('posts')


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if review.user == request.user:
        review.delete()
    return redirect('posts')


@login_required
def follow_users(request):
    """
    Manages the subscription system.

    Allows the user to follow other users based on specific rules:
    - Users cannot follow themselves.
    - Users cannot follow someone they have blocked.
    - Users cannot follow someone who blocked them.

    """
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

                elif BlockedUser.objects.filter(
                    user=request.user, blocked_user=user_to_follow
                ).exists():
                    message = (
                        "Vous avez bloqué cet utilisateur. "
                        "Débloquez-le d'abord."
                    )

                elif BlockedUser.objects.filter(
                    user=user_to_follow, blocked_user=request.user
                ).exists():
                    message = "Vous ne pouvez pas suivre cet utilisateur."

                elif UserFollows.objects.filter(
                    user=request.user, followed_user=user_to_follow
                ).exists():
                    message = "Vous suivez déjà cet utilisateur."

                else:
                    UserFollows.objects.create(
                        user=request.user, followed_user=user_to_follow
                    )
                    return redirect('follow_users')

            except User.DoesNotExist:
                message = "Cet utilisateur n'existe pas."

    following = UserFollows.objects.filter(user=request.user)
    followers = UserFollows.objects.filter(followed_user=request.user)

    blocked_users = BlockedUser.objects.filter(user=request.user)

    context = {
        'form': form,
        'following': following,
        'followers': followers,
        'blocked_users': blocked_users,
        'message': message
    }
    return render(request, 'reviews/follow_users.html', context)


@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    UserFollows.objects.filter(
        user=request.user, followed_user=user_to_unfollow
    ).delete()
    return redirect('follow_users')


@login_required
def block_user(request, user_id):
    user_to_block = get_object_or_404(User, id=user_id)

    if user_to_block != request.user:
        BlockedUser.objects.get_or_create(
            user=request.user, blocked_user=user_to_block
        )

        UserFollows.objects.filter(
            user=request.user, followed_user=user_to_block
        ).delete()
        UserFollows.objects.filter(
            user=user_to_block, followed_user=request.user
        ).delete()

    return redirect('follow_users')


@login_required
def unblock_user(request, user_id):
    BlockedUser.objects.filter(
        user=request.user, blocked_user_id=user_id
    ).delete()
    return redirect('follow_users')

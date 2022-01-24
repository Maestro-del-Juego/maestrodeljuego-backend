from telnetlib import STATUS
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUser(AbstractUser):
    avatar = models.URLField(blank=True, default='')

    def __repr__(self):
        return f"<User username:{self.username}>"
    
    def __str__(self):
        return f"{self.username}"


class GameNight(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'date', 'rid'], name='unique-gamenight')
        ]

    STATUS_CHOICES = [
        ('Voting', 'Voting'),
        ('Finalized', 'Finalized'),
        ('Cancelled', 'Cancelled')
    ]

    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='gamenights')
    date = models.DateField()
    rid = models.CharField(max_length=15, null=True)
    status = models.CharField(max_length=9, choices=STATUS_CHOICES, default='Voting')
    invitees = models.ManyToManyField('Contact', related_name='invited')
    attendees = models.ManyToManyField('Contact', related_name='attended')
    games = models.ManyToManyField('Game', related_name='gamenights', blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField(null=True)
    location = models.CharField(max_length=300)
    options = models.ManyToManyField('Game', related_name='options', blank=True)

    def __repr__(self):
        return f"<GameNight rid:{self.rid}>"

    def __str__(self):
        return f"{self.rid}"

    def update_attendees(self, contact_pk):
        attendees_list = self.attendees
        contact = Contact.objects.get(pk=contact_pk)
        if contact in self.invitees.all():
            if contact in attendees_list.all():
                attendees_list.remove(contact)
            else:
                attendees_list.add(contact)

    def update_invitees(self, contact_pk):
        invitees_list = self.invitees
        contact = Contact.objects.get(pk=contact_pk)
        if contact in invitees_list.all():
            invitees_list.remove(contact)
            if contact in self.attendees.all():
                self.attendees.remove(contact)
        else:
            invitees_list.add(contact)

    def update_options(self, game_pk):
        options_list = self.options
        game = Game.objects.get(pk=game_pk)
        if game in options_list.all():
            options_list.remove(game)
            if game in self.games.all():
                self.games.remove(game)
        else:
            options_list.add(game)

    def update_games(self, game_pk):
        games_list = self.games
        game = Game.objects.get(pk=game_pk)
        if game in self.options.all():
            if game in games_list.all():
                games_list.remove(game)
            else:
                games_list.add(game)


class Tag(models.Model):
    name = models.CharField(max_length=150)
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='tags', null=True)

    def __repr__(self):
        return f"<Tag name:{self.name}>"

    def __str__(self):
        return f"{self.name}"

class Category(models.Model):

    name = models.CharField(max_length=150)

    def __repr__(self):
        return f"<Category name: {self.name}>"

    def __str__(self):
        return f"{self.name}"


class GeneralFeedback(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['gamenight', 'attendee'], name='unique-feedback')
        ]

    gamenight = models.ForeignKey('GameNight', on_delete=models.CASCADE, related_name='generalfeedback')
    attendee = models.ForeignKey('Contact', on_delete=models.CASCADE, related_name='generalfeedback')
    overall_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    people_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True)
    location_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True)

    def __repr__(self):
        return f"<GeneralFeedback contact:{self.attendee.first_name} {self.attendee.last_name}>"

    def __str__(self):
        return f"GeneralFeedback from {self.attendee.first_name} {self.attendee.last_name}"


class Contact(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'first_name', 'last_name', 'email'], name='unique-contact')
        ]

    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='contacts', null=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254)
    
    def __repr__(self):
        return f"<Contact {self.first_name} {self.last_name}>"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Voting(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['gamenight', 'invitee', 'game'], name='unique-vote')
        ]

    gamenight = models.ForeignKey('GameNight', on_delete=models.CASCADE, related_name='voting')
    invitee = models.ForeignKey('Contact', on_delete=models.CASCADE, related_name='voting')
    game = models.ForeignKey('Game', on_delete=models.CASCADE, related_name='voting')
    vote = models.IntegerField(validators=[MinValueValidator(-1), MaxValueValidator(1)], default=0)

    def __repr__(self) -> str:
        return f"<Vote game: {self.game.title} name: {self.invitee.first_name} {self.invitee.last_name}>"
        
    def __str__(self):
        return f"Vote from {self.invitee.first_name} {self.invitee.last_name}"

class GameFeedback(models.Model):
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['gamenight', 'attendee', 'game'], name='unique-game-feedback')
        ]
    gamenight = models.ForeignKey('GameNight', on_delete=models.CASCADE, related_name='gamefeedback', null=True)
    attendee = models.ForeignKey('Contact', on_delete=models.CASCADE, related_name='gamefeedback', null=True)
    game = models.ForeignKey('Game', on_delete=models.CASCADE, related_name='gamefeedback')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True)

    def __repr__(self):
        return f"<GameFeedback {self.game.title} by {self.feedback.attendee.first_name} {self.feedback.attendee.last_name}>"


class Game(models.Model):
    title = models.CharField(max_length=250)
    bgg = models.IntegerField()
    pub_year = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    min_players = models.IntegerField(null=True, blank=True)
    max_players = models.IntegerField(null=True, blank=True)
    image = models.URLField(null=True, blank=True)
    playtime = models.IntegerField(null=True, blank=True)
    player_age = models.IntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    owners = models.ManyToManyField('CustomUser', related_name='games', blank=True)
    wishlisted = models.ManyToManyField('CustomUser', related_name='wishlist', blank=True)
    tags = models.ManyToManyField('Tag', related_name='games', blank=True)
    categories = models.ManyToManyField('Category', related_name='games', blank=True)

    def __repr__(self):
        return f"<Game title:{self.title}>"

    def __str__(self):
        return f"{self.title}"

    def update_owners(self, user):
        '''
        Adds or removes user from the owners M2M field.
        '''

        owner_list = self.owners
        if user in owner_list.all():
            owner_list.remove(user)
        else:
            owner_list.add(user)
            self.wishlisted.remove(user)

    def update_wishlisted(self, user):
        '''
        Adds or removes user from the wishlisted M2M field.
        '''

        wishlist_users = self.wishlisted
        if user in wishlist_users.all():
            wishlist_users.remove(user)
        else:
            wishlist_users.add(user)
            self.owners.remove(user)

    def tally_votes(self, gamenight):
        ballots = Voting.objects.filter(game=self, gamenight=gamenight)
        votes = 0
        for ballot in ballots:
            votes += ballot.vote

        return votes

    def calc_feedback(self, gamenight):
        ballots = GameFeedback.objects.filter(game=self, gamenight=gamenight)
        total = 0
        for ballot in ballots:
            total += ballot.rating
        average = total/len(ballots)
        return round(average, 2)


class RSVP(models.Model):
    gamenight = models.ForeignKey('GameNight', on_delete=models.CASCADE, related_name='rsvps')
    invitee = models.ForeignKey('Contact', on_delete=models.CASCADE, related_name='rsvps')
    attending = models.BooleanField()
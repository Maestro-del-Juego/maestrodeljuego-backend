from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUser(AbstractUser):
    avatar = models.URLField(blank=True, default='')

    def __repr__(self):
        return f"<User username:{self.username}>"
    
    def __str__(self):
        return f"{self.username}"


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


class GameNight(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='gamenights')
    date = models.DateField()
    invitees = models.ManyToManyField('Contact', related_name='invited')
    attendees = models.ManyToManyField('Contact', related_name='attended')
    games = models.ManyToManyField('Game', related_name='gamenights')
    player_num = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True)
    location = models.CharField(max_length=300)
    option1 = models.ForeignKey('Game', on_delete=models.DO_NOTHING, related_name='option1')
    option2 = models.ForeignKey('Game', on_delete=models.DO_NOTHING, related_name='option2', blank=True)
    option3 = models.ForeignKey('Game', on_delete=models.DO_NOTHING, related_name='option3', blank=True)
    option4 = models.ForeignKey('Game', on_delete=models.DO_NOTHING, related_name='option4', blank=True)
    option5 = models.ForeignKey('Game', on_delete=models.DO_NOTHING, related_name='option5', blank=True)
    option6 = models.ForeignKey('Game', on_delete=models.DO_NOTHING, related_name='option6', blank=True)
    option7 = models.ForeignKey('Game', on_delete=models.DO_NOTHING, related_name='option7', blank=True)
    option8 = models.ForeignKey('Game', on_delete=models.DO_NOTHING, related_name='option8', blank=True)
    option9 = models.ForeignKey('Game', on_delete=models.DO_NOTHING, related_name='option9', blank=True)
    option10 = models.ForeignKey('Game', on_delete=models.DO_NOTHING, related_name='option10', blank=True)

    def __repr__(self):
        return f"<GameNight date:{self.date}>"

    def __str__(self):
        return f"{self.date}"


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


class Feedback(models.Model):
    gamenight = models.ForeignKey('GameNight', on_delete=models.CASCADE, related_name='feedback')
    attendee = models.ForeignKey('Contact', on_delete=models.CASCADE, related_name='feedback')
    overall_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    people_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True)
    location_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True)
    game1_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True)
    game2_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True)
    game3_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True)
    game4_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True)
    game5_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True)

    def __repr__(self):
        return f"<Feedback contact:{self.attendee.first_name} {self.attendee.last_name}>"

    def __str__(self):
        return f"Feedback from {self.attendee.first_name} {self.attendee.last_name}"


class Contact(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254)
    
    def __repr__(self):
        return f"<Contact name:{self.first_name} {self.last_name}>"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Voting(models.Model):
    gamenight = models.ForeignKey('GameNight', on_delete=models.CASCADE, related_name='voting')
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE, related_name='voting')
    option1 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)], blank=True)
    option2 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)], blank=True)
    option3 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)], blank=True)
    option4 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)], blank=True)
    option5 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)], blank=True)
    option6 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)], blank=True)
    option7 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)], blank=True)
    option8 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)], blank=True)
    option9 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)], blank=True)
    option10 = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(3)], blank=True)
    
    def __repr__(self) -> str:
        return f"<Voting name:{self.contact.first_name} {self.contact.last_name}>"
        
    def __str__(self):
        return f"Vote from {self.contact.first_name} {self.contact.last_name}"

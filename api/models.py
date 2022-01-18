from django.db import models
from django.contrib.auth.models import AbstractUser


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
    date = models.DateField()
    game = models.ForeignKey('Game', on_delete=models.CASCADE, related_name='gamenights')
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='gamenights')
    player_num = models.IntegerField()
    round_num = models.IntegerField()
    playtime = models.IntegerField(blank=True)

    def __repr__(self):
        return f"<GameNight date:{self.date} game:{self.game}>"

    def __str__(self):
        return f"{self.date}, {self.game}"


class Tag(models.Model):
    name = models.CharField(max_length=150)
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='tags', null=True)

    def __repr__(self):
        return f"<Tag name:{self.name}>"

    def __str__(self):
        return f"{self.name}"

from django.db import models


class User(models.Model):
    def __repr__(self):
        return f"<User username:{self.username}>"
    
    def __str__(self):
        return f"{self.username}"


class Game(models.Model):
    title = models.CharField(max_length=250)
    bgg_id = models.IntegerField()
    pub_year = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    min_players = models.IntegerField(null=True, blank=True)
    max_players = models.IntegerField(null=True, blank=True)
    image = models.URLField(null=True, blank=True)
    playtime = models.IntegerField(null=True, blank=True)
    player_age = models.IntegerField(null=True, blank=True)
    owners = models.ManyToManyField('User', related_name='games', blank=True)
    wishlisted = models.ManyToManyField('User', related_name='wishlist', blank=True)
    tags = models.ManyToManyField('Tag', related_name='games', blank=True)

    def __repr__(self):
        return f"<Game title:{self.title}>"

    def __str__(self):
        return f"{self.title}"


class GameNight(models.Model):
    date = models.DateField()
    game = models.ForeignKey('Game', on_delete=models.CASCADE, related_name='gamenights')
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='gamenights')
    player_num = models.IntegerField()
    round_num = models.IntegerField()
    playtime = models.IntegerField(blank=True)

    def __repr__(self):
        return f"<GameNight date:{self.date} game:{self.game}>"

    def __str__(self):
        return f"{self.date}, {self.game}"


class Tag(models.Model):
    name = models.CharField(max_length=150)

    def __repr__(self):
        return f"<Tag name:{self.name}>"

    def __str__(self):
        return f"{self.name}"

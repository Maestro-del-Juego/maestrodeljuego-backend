from rest_framework import serializers
from .models import Game, CustomUser, Tag, GameNight, Contact, Voting, GeneralFeedback, GameFeedback, RSVP, Category
from djoser.serializers import UserCreatePasswordRetypeSerializer
from drf_writable_nested import WritableNestedModelSerializer
from django.db.models.query import QuerySet
from calendar import day_name
from datetime import date
import random


class GameListSerializer(serializers.ModelSerializer):
    categories = serializers.StringRelatedField(many=True)

    class Meta:
        model = Game
        fields = (
            'pk',
            'bgg',
            'title',
            'pub_year',
            'image',
            'playtime',
            'min_players',
            'max_players',
            'categories',
        )


class UserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'pk',
            'username',
            'avatar',
        )


class GameDetailSerializer(serializers.ModelSerializer):
    owned = serializers.SerializerMethodField()
    wishlisted = serializers.SerializerMethodField()
    categories = serializers.StringRelatedField(many=True)

    class Meta:
        model = Game
        fields = (
            'title',
            'bgg',
            'pub_year',
            'description',
            'min_players',
            'max_players',
            'image',
            'playtime',
            'player_age',
            'categories',
            'owned',
            'wishlisted'
        )

    def get_owned(self, obj):
        user = self.context['request'].user
        owners = obj.owners.all()
        if user in owners:
            return True
        return False

    def get_wishlisted(self, obj):
        user = self.context['request'].user
        wishers = obj.wishlisted.all()
        if user in wishers:
            return True
        return False


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = (
            'pk',
            'first_name',
            'last_name',
            'email'
        )


class RSVPSerializer(serializers.ModelSerializer):
    gamenight = serializers.StringRelatedField()
    invitee = ContactSerializer(read_only=True)
    class Meta:
        model = RSVP
        fields = (
            'pk',
            'gamenight',
            'invitee',
            'attending',
        )


class RSVPForGameNightSerializer(serializers.ModelSerializer):
    invitee = serializers.StringRelatedField()
    class Meta:
        model = RSVP
        fields = (
            'invitee',
            'attending'
        )


class GameForGameNightSerializer(serializers.ModelSerializer):
    categories = serializers.StringRelatedField(many=True)
    votes = serializers.SerializerMethodField()
    # feedback = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = (
            'pk',
            'bgg',
            'title',
            'pub_year',
            'image',
            'playtime',
            'min_players',
            'max_players',
            'categories',
            'votes',
            # 'feedback',
        )

    def get_votes(self, obj):
        serialized_instance = self.parent.parent.instance
        if isinstance(serialized_instance, QuerySet):
            return None
        gamenight = serialized_instance
        votes = obj.tally_votes(gamenight)
        return votes

    # def get_feedback(self, obj):
    #     serialized_instance = self.parent.parent.instance
    #     if isinstance(serialized_instance, QuerySet):
    #         return None
    #     gamenight = serialized_instance
    #     feedback = 
    #     rating = obj.calc_feedback(gamenight)
    #     return rating


class ContactForGameNightSerializer(serializers.ModelSerializer):
    favorite_games = serializers.SerializerMethodField()
    attendance_rate = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = (
            'pk',
            'first_name',
            'last_name',
            'email',
            'favorite_games',
            'attendance_rate',
        )

    def get_favorite_games(self, obj):
        votes = obj.voting.all()
        gamefbacks = obj.gamefeedback.all()
        voted_games_dict = {}
        fback_total_dict = {}
        fback_count_dict = {}
        fback_avg_dict = {}
        game_dict = {}
        for fback in gamefbacks:
            game = fback.game
            if game.title in fback_total_dict and game.title in fback_count_dict:
                fback_total_dict[game.title] += fback.rating
            else:
                fback_total_dict[game.title] = fback.rating
            if game.title in fback_count_dict:
                fback_count_dict[game.title] += 1
            else:
                fback_count_dict[game.title] = 1
            if game.title not in game_dict:
                game_dict[game.title] = game
        for game in fback_total_dict.keys():
            fback_avg_dict[game] = fback_total_dict[game]/fback_count_dict[game]
        for vote in votes:
            game = vote.game
            if game.title in voted_games_dict:
                voted_games_dict[game.title] += vote.vote
            else:
                voted_games_dict[game.title] = vote.vote
        fback_sort = sorted(fback_avg_dict, key=fback_avg_dict.__getitem__)
        final_list = []
        for game in reversed(fback_sort):
            game_obj = game_dict[game]
            final_list.append(
                {
                    'title': game,
                    'bgg': game_obj.bgg,
                    'pub_year': game_obj.pub_year,
                    'image': game_obj.image,
                    'avg_feedback': fback_avg_dict[game],
                    'accum_votes': voted_games_dict[game]
                }
            )
            if len(final_list) == 5:
                break
        return final_list

    def get_attendance_rate(self, obj):
        attended = len(obj.attended.all())
        invited = len(obj.invited.all())
        return round((attended/invited)*100, 2)


class GameNightSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer(read_only=True)
    invitees = serializers.SerializerMethodField()
    rsvps = RSVPForGameNightSerializer(many=True)
    attendees = ContactForGameNightSerializer(many=True)
    games = GameForGameNightSerializer(read_only=True, many=True)
    options = GameForGameNightSerializer(read_only=True, many=True)
    # feedback = serializers.SerializerMethodField()

    class Meta:
        model = GameNight
        fields = (
            'pk',
            'rid',
            'user',
            'date',
            'status',
            'invitees',
            'rsvps',
            'attendees',
            'games',
            'start_time',
            'end_time',
            'location',
            'options',
            # 'feedback',
        )

    # def get_feedback(self, obj):
    #     return obj.calc_feedback()

    def get_invitees(self, obj):
        invitees = obj.invitees.all()
        rsvps = obj.rsvps.all()
        rsvp_list = []
        inv_list = []
        for rsvp in rsvps:
            rsvp_list.append(rsvp.invitee)
        for contact in invitees:
            if contact in rsvp_list:
                continue
            inv_list.append(
                {
                    'pk': contact.pk,
                    'first_name': contact.first_name,
                    'last_name': contact.last_name,
                    'email': contact.email
                }
            )
        return inv_list


class GameNightCreateSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer(read_only=True)

    class Meta:
        model = GameNight
        fields = (
            'pk',
            'rid',
            'user',
            'date',
            'status',
            'invitees',
            'games',
            'start_time',
            'end_time',
            'location',
            'options'
        )


class DjoserUserSerializer(serializers.ModelSerializer):
    games = GameListSerializer(many=True, read_only=True)
    wishlist = GameListSerializer(many=True, read_only=True)
    contacts = ContactSerializer(many=True, read_only=True)
    gamenights = GameNightSerializer(many=True, read_only=True)
    gamenights_finished = serializers.SerializerMethodField()
    weekday_stats = serializers.SerializerMethodField()
    most_common_players = serializers.SerializerMethodField()
    most_played_games = serializers.SerializerMethodField()
    least_played_games = serializers.SerializerMethodField()
    games_not_played = serializers.SerializerMethodField()
    highest_rated_games = serializers.SerializerMethodField()
    most_played_categories = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = (
            'pk',
            'username',
            'email',
            'avatar',
            'games',
            'wishlist',
            'contacts',
            'gamenights',
            'gamenights_finished',
            'weekday_stats',
            'most_common_players',
            'most_played_games',
            'least_played_games',
            'games_not_played',
            'highest_rated_games',
            'most_played_categories',
        )

    def get_gamenights_finished(self, obj):
        return len(obj.gamenights.filter(status="Finalized"))

    # methods for weekday_stats field
    def get_weekday_stats(self, obj):
        user = obj
        gamenight_dict = self.build_week_dict(user)
        days = gamenight_dict.keys()
        stats_dict = {
            'avg_overall_feedback': {},
            'avg_attend_ratio': {},
            'avg_session_len': {},
            'avg_game_num': {},
            'avg_player_num': {},
            'sessions_num': {}
        }
        for day in days:
            gamenights = gamenight_dict[day]
            stats_dict['avg_overall_feedback'][day] = self.days_avg_overall(gamenights)
            stats_dict['avg_attend_ratio'][day] = self.days_avg_attend(gamenights)
            stats_dict['avg_session_len'][day] = self.days_avg_session_len(gamenights)
            stats_dict['avg_game_num'][day] = self.days_avg_game_num(gamenights)
            stats_dict['avg_player_num'][day] = self.days_avg_player_num(gamenights)
            stats_dict['sessions_num'][day] = len(gamenights)
        return stats_dict

    def build_week_dict(self, user):
        '''
        Builds a dictionary where the keys are the names for the days of the
        week and the values are the GameNights that occurred on that day.
        '''
        gamenights = user.gamenights.filter(status="Finalized")
        game_days = {}
        days = list(day_name)
        for day in days:
            game_days[day] = []
        for night in gamenights:
            day = night.date.weekday()
            game_days[days[day]].append(night)
        return game_days

    def days_avg_overall(self, gamenights):
        '''
        Takes a list of GameNight objects and returns the average overall
        rating among them.
        '''
        gamenight_num = len(gamenights)
        total = 0
        for gamenight in gamenights:
            overall = gamenight.calc_avg_overall()
            if overall == None:
                gamenight_num -= 1
                continue
            total += overall
        if gamenight_num == 0:
            average = None
        else:
            average = round(total/gamenight_num, 2)
        return average

    def days_avg_attend(self, gamenights):
        '''
        Takes a list of GameNight objects and returns the average attendance
        ratio among them as a percentage.
        '''
        gamenight_num = len(gamenights)
        total = 0
        for gamenight in gamenights:
            attendees_num = len(gamenight.attendees.all())
            invitees_num = len(gamenight.invitees.all())
            if invitees_num == None:
                gamenight_num -= 1
                continue
            attendance = round(attendees_num/invitees_num, 2)
            total += attendance
        if gamenight_num == 0:
            return None
        else:
            average = round((total/gamenight_num)*100, 2)
        return average

    def days_avg_session_len(self, gamenights):
        '''
        Takes a list of GameNight objects and returns the average session
        length (in minutes) among them.
        '''
        gamenight_num = len(gamenights)
        total = 0
        for gamenight in gamenights:
            session_len = gamenight.calc_session_len()
            if session_len == None:
                gamenight_num -= 1
                continue
            total += session_len
        if gamenight_num == 0:
            average = None
        else:
            average = round(total/gamenight_num, 2)
        return average

    def days_avg_game_num(self, gamenights):
        '''
        Takes a list of GameNight objects and returns the average number of
        unique games played among them.
        '''
        gamenight_num = len(gamenights)
        total = 0
        for gamenight in gamenights:
            game_num = len(gamenight.games.all())
            if game_num == 0:
                gamenight_num -=1
                continue
            total += game_num
        if gamenight_num == 0:
            average = None
        else:
            average = round(total/gamenight_num, 2)
        return average

    def days_avg_player_num(self, gamenights):
        '''
        Takes a list of GameNight objects and returns the average number of
        players among them.
        '''
        gamenight_num = len(gamenights)
        total = 0
        for gamenight in gamenights:
            player_num = len(gamenight.attendees.all())
            if player_num ==0:
                gamenight_num -=1
                continue
            total += player_num
        if gamenight_num == 0:
            average = None
        else:
            average = round(total/gamenight_num, 2)
        return average

    def get_most_common_players(self, obj):
        contacts = obj.contacts.all()
        return_list = []
        name_pk_dict = {}
        freq_dict = {}
        for contact in contacts:
            gamenights = len(contact.attended.all())
            freq_dict[str(contact)] = gamenights
            name_pk_dict[str(contact)] = contact.pk
        contacts_sort = sorted(freq_dict, key=freq_dict.__getitem__)
        if len(contacts) < 5:
            index = -1
            max = -len(contacts) - 1
            while index > max:
                name = contacts_sort[index]
                if freq_dict[name] == 0:
                    index -= 1
                    if index == max:
                        break
                    continue
                pk = name_pk_dict[name]
                return_list.append(
                    {
                        'name': name,
                        'pk': pk,
                        'attended': freq_dict[name]
                    }
                )
                index -= 1
                if index == max:
                    break
        else:
            index = -1
            while index > -6:
                name = contacts_sort[index]
                if freq_dict[name] == 0:
                    index -= 1
                    if index == -6:
                        break
                    continue
                pk = name_pk_dict[name]
                return_list.append(
                    {
                        'name': name,
                        'pk': pk,
                        'attended': freq_dict[name]
                    }
                )
                index -= 1
                if index == -6:
                    break
        return return_list

    def get_most_played_games(self, obj):
        games = obj.games.all()
        freq_dict, other_data, games_sort = self.sort_games_by_play_num(games)
        played_dict = {k:v for k,v in freq_dict.items() if v != 0}
        for game in games_sort.copy():
            if game not in played_dict:
                games_sort.remove(game)
        total = sum(played_dict.values())
        perc_left = 100
        perc_added = 0
        final_list = []
        for game in reversed(games_sort):
            percentage = round((played_dict[game]/total)*100, 2)
            if len(final_list) > 8:
                if percentage < perc_left:
                    final_list.append(
                        {
                            'title': 'Other',
                            'percentage': round(perc_left, 2)
                        }
                    )
                    break
            perc_left -= percentage
            perc_added += percentage
            game_data = other_data[game]
            if perc_added > 100:
                percentage -= (perc_added - 100)
            final_list.append(
                {
                    'title': game,
                    'bgg': game_data['bgg'],
                    'pub_year': game_data['pub_year'],
                    'image': game_data['image'],
                    'played': played_dict[game],
                    'percentage': round(percentage, 2)
                }
            )
        return final_list

    def get_least_played_games(self, obj):
        return_list = []
        games = obj.games.all()
        freq_dict, other_data, games_sort = self.sort_games_by_play_num(games)
        if len(games) < 5:
            for game in games_sort:
                if freq_dict[game] == 0:
                    continue
                gamenights = games.filter(title=game)[0].gamenights.all()
                most_recent = gamenights[0].date
                for gamenight in gamenights:
                    if gamenight.date > most_recent:
                        most_recent = gamenight.date
                game_data = other_data[game]
                return_list.append(
                    {
                        'name': game,
                        'bgg': game_data['bgg'],
                        'pub_year': game_data['pub_year'],
                        'image': game_data['image'],
                        'last_played': str(most_recent),
                        'played': freq_dict[game]
                    }
                )
        else:
            index = 0
            while len(return_list) < 5:
                name = games_sort[index]
                if freq_dict[name] == 0:
                    index += 1
                    if index == len(games_sort):
                        break
                    continue
                gamenights = games.filter(title=name)[0].gamenights.all()
                most_recent = gamenights[0].date
                for gamenight in gamenights:
                    if gamenight.date > most_recent:
                        most_recent = gamenight.date
                game_data = other_data[name]
                return_list.append(
                    {
                        'name': name,
                        'bgg': game_data['bgg'],
                        'pub_year': game_data['pub_year'],
                        'image': game_data['image'],
                        'last_played': str(most_recent),
                        'played': freq_dict[name]
                    }
                )
                index += 1
                if index == len(games_sort):
                    break

        return return_list

    def get_games_not_played(self,obj):
        final_list = []
        games = obj.games.all()
        freq_dict, other_data, games_sort = self.sort_games_by_play_num(games)
        zeroes = [k for k,v in freq_dict.items() if v == 0]
        for game in zeroes:
            game_data = other_data[game]
            final_list.append(
                {
                    'name': game,
                    'bgg': game_data['bgg'],
                    'pub_year': game_data['pub_year'],
                    'image': game_data['image'],
                    'played': freq_dict[game]
                }
            )
        if len(final_list) < 6:
            return final_list
        return random.sample(final_list, 5)

    def sort_games_by_play_num(self, games):
        other_data_dict = {}
        freq_dict = {}
        for game in games:
            gamenights = len(game.gamenights.all())
            freq_dict[str(game)] = gamenights
            other_data_dict[str(game)] = {
                'bgg': game.bgg,
                'pub_year': game.pub_year,
                'image': game.image
            }
        games_sort = sorted(freq_dict, key=freq_dict.__getitem__)
        return freq_dict, other_data_dict, games_sort

    def get_highest_rated_games(self, obj):
        games = obj.games.all()
        other_data = {}
        rating_dict = {}
        final_list = []
        for game in games:
            all_gamenights = game.gamenights.all()
            gamenights = all_gamenights.filter(user=obj)
            total = 0
            for gamenight in gamenights:
                fback = game.calc_feedback(gamenight)
                if fback is None:
                    continue
                total += fback
            if total == 0:
                continue
            rating_dict[str(game)] = round(total/len(gamenights), 2)
            other_data[str(game)] = {
                'bgg': game.bgg,
                'pub_year': game.pub_year,
                'image': game.image
            }
        games_sort = sorted(rating_dict, key=rating_dict.__getitem__)
        if len(games) < 6:
            for game in reversed(games_sort):
                if game not in rating_dict:
                    continue
                game_data = other_data[game]
                final_list.append(
                    {
                        'name': game,
                        'bgg': game_data['bgg'],
                        'pub_year': game_data['pub_year'],
                        'image': game_data['image'],
                        'rating': rating_dict[game]
                    }
                )
        else:
            for game in reversed(games_sort):
                if game not in rating_dict:
                    continue
                game_data = other_data[game]
                final_list.append(
                    {
                        'name': game,
                        'bgg': game_data['bgg'],
                        'pub_year': game_data['pub_year'],
                        'image': game_data['image'],
                        'rating': rating_dict[game]
                    }
                )
        return final_list

    def get_most_played_categories(self, obj):
        categories = Category.objects.all()
        games = obj.games.all()
        freq_dict, other, g_sort = self.sort_games_by_play_num(games)
        count_dict = {}
        for category in categories:
            count_dict[category.name] = 0
        for game in games:
            game_cats = game.categories.all()
            for cat in game_cats:
                count_dict[cat.name] += freq_dict[str(game)]
        played_dict = {k:v for k,v in count_dict.items() if v != 0}
        total = sum(played_dict.values())
        sorted_cats = sorted(played_dict, key=played_dict.__getitem__)
        perc_left = 100
        perc_added = 0
        final_list = []
        for category in reversed(sorted_cats):
            percentage = round((played_dict[category]/total)*100, 2)
            if len(final_list) > 8:
                if percentage < perc_left:
                    final_list.append(
                        {
                            'name': 'Other',
                            'percentage': round(perc_left, 2)
                        }
                    )
                    break
            perc_left -= percentage
            perc_added += percentage
            if perc_added > 100:
                percentage -= (perc_added - 100)
            final_list.append(
                {
                    'name': category,
                    'games_played': played_dict[category],
                    'percentage': round(percentage, 2)
                }
            )
        return final_list


class DjoserRegistrationSerializer(UserCreatePasswordRetypeSerializer):
    class Meta(UserCreatePasswordRetypeSerializer.Meta):
        fields = (
            'username',
            'avatar',
            'email',
            'password',
        )


class TagListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'name',
            'user',
        )
        


class GameFeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model = GameFeedback
        fields = (
            'gamenight',
            'attendee',
            'game',
            'rating',
        )


class GeneralFeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model = GeneralFeedback
        fields = (
            'gamenight',
            'attendee',
            'overall_rating',
            'people_rating',
            'location_rating',
            'comments',
        )


class VotingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voting
        fields = (
            'gamenight',
            'invitee',
            'game',
            'vote'
        )

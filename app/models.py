from django.db import models

# Create your models here.

class Player(models.Model):
    name = models.CharField(max_length=100)
    sid = models.CharField(max_length=100)
    pp3 = models.FloatField(default=0)
    profile = models.CharField(default='',max_length=50,blank=True)
    letter = models.CharField(default='',max_length=50,blank=True)
    senobi = models.FloatField(default=0)
    sum = models.FloatField(default=0)
    abstein = models.BooleanField(default=False)
    hashurl = models.CharField(default='',max_length=64)
    rival_sid = models.CharField(default='',max_length=100,blank=True)
    league = models.CharField(default='',max_length=10)

    def __str__(self):
        return self.name

class Updatetime(models.Model):
    time = models.DateTimeField()

class Map(models.Model):
    league = models.CharField(default='',max_length=10)
    title = models.CharField(default='',max_length=100)
    author = models.CharField(default='',max_length=100)
    diff = models.CharField(default='',max_length=20)
    label = models.CharField(default='',max_length=20)
    notes = models.IntegerField(default=0)
    bsr = models.CharField(default='',max_length=10)
    hash = models.CharField(default='',max_length=100)

    def __str__(self):
        return f'({self.league}){self.title[:10]}'

class Score(models.Model):
    sid = models.CharField(max_length=20)
    diff = models.CharField(max_length=20)
    score = models.IntegerField(default=0)
    acc = models.FloatField(default=0)

    def __str__(self):
        name = Player.objects.get(sid = self.sid).name
        title = Map.objects.filter(diff = self.diff)[0].title   
        return name + ' > ' + title

class News(models.Model):
    time = models.DateTimeField()
    text = models.CharField(default='',max_length=100)

    def __str__(self):
        return str(self.time) + '_' + self.text

class LeagueInfo(models.Model):
    league = models.CharField(default='',max_length=20)
    fontcolor = models.CharField(default='',max_length=20)
    bgcolor = models.CharField(default='',max_length=20)

    def __str__(self):
        return self.league
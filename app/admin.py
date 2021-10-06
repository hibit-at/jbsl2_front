from django.contrib import admin
from .models import Player,Updatetime,Score,Map,LeagueInfo,News

# Register your models here.

admin.site.register(Player)
admin.site.register(Updatetime)
admin.site.register(Map)
admin.site.register(Score)
admin.site.register(LeagueInfo)
admin.site.register(News)
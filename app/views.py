from django.core.checks.messages import Error
from django.shortcuts import render, redirect
from django import forms
import requests
from .models import News, Player, Updatetime, Map, Score, LeagueInfo
from collections import defaultdict
import re
from datetime import date, datetime

# utils


def slope(n):
    if n == 1:
        return 0
    if n == 2:
        return -3
    return -(n+2)


def color(label):
    if label == 'Expert+':
        return 'magenta'
    if label == 'Expert':
        return 'red'
    if label == 'Hard':
        return 'orange'
    if label == 'Normal':
        return 'green'
    if label == 'Easy':
        return 'cyan'
    return 'black'


def name_from_sid(sid):
    if Player.objects.filter(sid=sid).exists():
        return Player.objects.get(sid=sid).name
    return Error


def object_from_sid(sid):
    if Player.objects.filter(sid=sid).exists():
        return Player.objects.get(sid=sid)
    return Error


def score_acc_map(score_txt, notes):
    score = int(score_txt.replace(',', ''))
    acc = score/(115*8*int(notes)-7245)*100
    acc = float(acc*100//1/100)
    return acc

# Create your views here.


def index(request):
    # 人間関係をグラフ化
    players = Player.objects.all()
    nodes = []
    edges = {}
    for p in players:
        rival_sid = p.rival_sid
        if rival_sid == '':
            continue
        rival_name = name_from_sid(rival_sid)
        edges[p.name] = rival_name

    # 両想い
    how_many_pair = 0
    for p in players:
        name = p.name
        if name in edges:
            love = edges[name]
            if love in edges:
                love_love = edges[love]
                if name == love_love:
                    how_many_pair += 1
    how_many_pair //= 2

    # 片想い
    kataomoi = {}
    for p in players:
        kataomoi[p.name] = 0
    for p in players:
        name = p.name
        if name in edges:
            love = edges[name]
            kataomoi[love] += 1
    sort_kataomoi = sorted(kataomoi.items(), key=lambda x: -x[1])
    kataomoi_num = sort_kataomoi[0][1]
    print(kataomoi_num)
    kataomowares = list(
        filter(lambda x: x[1] == kataomoi_num, kataomoi.items()))
    #

    players = Player.objects.all().order_by('pp3').exclude(league='staff').reverse()
    size = len(players)
    print('player size', size)
    border1_2 = max(8, size//3)
    border2_3 = max(16, (2*size)//3)
    j1 = players[:border1_2]
    for p in j1:
        p.league = "J1"
        p.save()
    j2 = players[border1_2:border2_3]
    for p in j2:
        p.league = "J2"
        p.save()
    j3 = players[border2_3:]
    for p in j3:
        p.league = "J3"
        p.save()
    print('border1_2', border1_2)
    print('border2_3', border2_3)
    leagues = LeagueInfo.objects.all()
    total_league = []
    for L in leagues:
        league = L.league
        L_players = Player.objects.filter(
            league=league).order_by('pp3').reverse()
        if league == 'staff':
            L_players = Player.objects.filter(league=league)
            print('staff roll')
            player_staffs = ['BigSlick','おかず','oRuGaM','おーばか']
            for ps in player_staffs:
                psobject = Player.objects.filter(name = ps)
                L_players = L_players.union(psobject)
            L_players = L_players.order_by('-pp3')
        append_data = {
            'leagueinfo': L,
            'players': L_players
        }
        total_league.append(append_data)
    utimes = Updatetime.objects.all()
    if len(utimes) > 0:
        utime = utimes[0]
    else:
        utime = None
    # Newsfeed
    news = News.objects.all().order_by('-time')[:7]
    params = {'total_league': total_league,
              'how_many_pair': how_many_pair,
              'kataomowares': kataomowares,
              'utime': utime,
              'news' : news}
    return render(request, 'index.html', params)


def user(request):
    # クエリからユーザーの特定
    hashurl = request.GET.get('hash')
    if not Player.objects.filter(hashurl=hashurl).exists():
        return render(request, 'error.html')
    player = Player.objects.get(hashurl=hashurl)
    print(f'{player.name} authenticated!')
    # POSTがあった場合にはプロフィールの変更
    post = request.POST
    if len(post) > 0:
        # プロフィールの変更
        print(post)
        player.profile = post['profile']
        # ライバルの変更
        if 'rival' in post:
            player.rival_sid = request.POST['rival']
            # 自分をライバルに設定した場合は、ライバルなし
            if player.sid == player.rival_sid:
                player.rival_sid = ''
        else:
            rival_sid = player.rival_sid
        player.save()

    # ライバルの名前の探索
    rival = ''
    if player.rival_sid != '':
        rival = Player.objects.get(sid=player.rival_sid).name
    #

    # フォーム作成
    rivals = Player.objects.all().filter(
        league=player.league).order_by('pp3').reverse()
    choice = []
    for r in rivals:
        choice.append((r.sid, r.name))

    class ProfileForm(forms.Form):
        profile = forms.CharField(
            label='ひとこと', widget=forms.Textarea, max_length=50, required=False)
        rival = forms.ChoiceField(
            label='ライバル', widget=forms.RadioSelect, choices=choice, required=False)


    init_form = {
        'profile': player.profile,
        'rival': player.rival_sid,
    }
    pform = ProfileForm(initial=init_form)

    params = {'player': player, 'pform': pform, 'rival': rival}
    return render(request, 'user.html', params)


def what(request):
    return render(request, 'what.html')


def leaderboard(request):
    league = request.GET.get('league')
    print(league, 'league')

    if not Player.objects.filter(league=league).exists():
        return render(request, 'error.html')

    # リーグ内プレイヤーの選定
    players = Player.objects.filter(league=league)
    size = len(players)
    base = size + 3
    # リーグ内マップの選定
    maps = Map.objects.filter(league=league)
    # マップごとのプレイヤーランキング
    LBs = []
    for m in maps:
        mapLB = []
        for p in players:
            # print(p.name, m.title)
            if Score.objects.filter(sid=p.sid, diff=m.diff).exists():
                score = Score.objects.get(sid=p.sid, diff=m.diff)
                mapLB.append((p.name, score.acc))
            else:
                mapLB.append((p.name, 0))
        mapLB = sorted(mapLB, key=lambda x: -x[1])
        scored_LB = []
        rank = 1
        for mL in mapLB:
            print(mL)
            name, acc = mL
            pos = base + slope(rank)
            if acc == 0:
                pos = 0
            player = Player.objects.get(name=name)
            if player.abstein:
                pos = 0
            append_data = {
                'rank': rank,
                'name': name,
                'acc': acc,
                'pos': pos,
                'abstein': player.abstein,
                'sid' : player.sid,
            }
            scored_LB.append(append_data)
            if not player.abstein:
                rank += 1
        append_data = {
            'map': m,
            'color': color(m.label),
            'players': scored_LB,
        }
        LBs.append(append_data)
    # 順位点をもとにランキングを決定

    def pos_acc():
        return {'pos': 0, 'acc': 0}

    total_rank = defaultdict(pos_acc)
    for LB in LBs:
        for p in LB['players']:
            # print(p)
            total_rank[p['name']]['pos'] += p['pos']
            total_rank[p['name']]['acc'] += p['acc']
    total_rank = sorted(total_rank.items(),
                        key=lambda x: (-x[1]['pos'], -x[1]['acc']))
    scored_rank = []
    rank = 1
    for t in total_rank:
        name = t[0]
        player = Player.objects.get(name=name)
        append_data = {
            'rank': rank,
            'player' : player,
            'pos': t[1]['pos'],
            'acc': t[1]['acc'],
        }
        scored_rank.append(append_data)
        if not player.abstein:
            rank += 1

    # リーグごとのカラー
    Linfo = LeagueInfo.objects.get(league=league)

    # 取得日時
    utimes = Updatetime.objects.all()
    if len(utimes) > 0:
        utime = utimes[0]
    else:
        utime = None

    params = {
        'scored_rank': scored_rank,
        'league': league,
        'LBs': LBs,
        'Linfo': Linfo,
        'utime': utime,
    }

    return render(request, 'leaderboard.html', params)


def mapboard(request):
    diff = request.GET.get('map')
    if not Map.objects.filter(diff=diff).exists():
        return render(request, 'error.html')
    map = Map.objects.filter(diff=diff)[0]
    scores = Score.objects.filter(diff=diff).order_by('-acc')
    players = []
    rank = 1
    for s in scores:
        player = Player.objects.get(sid=s.sid)
        name = player.name
        league = player.league
        append_data = {
            'rank': rank,
            'name': name,
            'league': league,
            'acc': s.acc,
        }
        players.append(append_data)
        rank += 1

    # 取得日時
    utimes = Updatetime.objects.all()
    if len(utimes) > 0:
        utime = utimes[0]
    else:
        utime = None

    params = {'map': map,
              'color': color(map.label),
              'scores': scores,
              'players': players,
              'utime': utime,
              }
    return render(request, 'mapboard.html', params)


def submission(request):

    class URLForm(forms.Form):
        url = forms.CharField(
            widget=forms.Textarea(attrs={'cols': '100', 'rows': '1'}),
            label='url', max_length=100,)

    form = URLForm()
    params = {'form': form}
    return render(request, 'submission.html', params)


def register(request):

    post = request.POST
    print(post)
    if len(post) == 0:
        return render(request, 'error.html')
    try:
        url = post['url']
        print(url)
        txt = requests.get(url).text
        txt = txt.replace('\n', '').replace('\t', '')
        ptn = r'https://scoresaber.com/leaderboard/(.*?)\?page=(.*?)'
        diff = re.findall(ptn, url)[0][0]
    except:
        return render(request, 'error.html')

    # map validation
    print(diff)
    if not Map.objects.filter(diff=diff).exists():
        print('not')
        params = {'message': ['このマップIDは本システムに登録されていません。']}
        return render(request, 'register.html', params)
    song = Map.objects.filter(diff=diff)[0]
    ptn = r'<a href="/u/(.*?)">'
    sids = re.findall(ptn, txt)
    ptn = r'<td class="score">(.*?)</td>'
    scores = re.findall(ptn, txt)
    logs = [f'{song.title} ({song.label}) のスコアを検索中...']
    cnt = 0
    for sid, score in zip(sids, scores):
        logs.append(f'プレイヤーID {sid} を検索 ')
        if not Player.objects.filter(sid=sid).exists():
            continue
        player = Player.objects.get(sid=sid)
        logs.append(f'{player.name} として登録されています。')
        acc = score_acc_map(score, song.notes)
        print(acc)
        if Score.objects.filter(diff=diff, sid=sid).exists():
            score = Score.objects.get(diff=diff, sid=sid)
            score.acc = acc
            score.save()
        else:
            Score.objects.create(
                diff=diff,
                sid=sid,
                acc=acc,
            )
        logs.append(f'精度を {acc} %に更新。')
        cnt += 1
    logs.append(f'更新を完了しました。')
    if cnt == 0:
        logs.append(f'対象譜面は合っているようですが、集計対象のプレイヤーが存在しません。')
        logs.append(f'ページ番号が間違っている可能性があります。リンク先に対象プレイヤーの名前があるか確認ください。')
    params = {'message': logs}
    return render(request, 'register.html', params)
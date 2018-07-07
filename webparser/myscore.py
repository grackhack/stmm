import re
from datetime import datetime
from time import sleep
import logging
import json

import sys

import telegram
from bs4 import BeautifulSoup
from telegram.ext import Updater

from tbot.cfg import TOKEN, ALEX, VOVEI
from tbot.cfg import BOT_FATHER
from tbot.cfg import DOCENT
from webparser import myscoresettings
from webparser.dbconnection import run_sql
from webparser.seleniumparser import WebParser
from webparser import sql

DEBUG = False
logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.DEBUG, filename=u'myscore.log')


class EventType(object):
    new_game = '0'
    goal = '1'
    card_red = '2'


class Odds(object):
    def __init__(self, pre_odds=None, live_odds=None, flash_facts=None):
        self.pre_p1 = pre_odds[0] if pre_odds else ''
        self.pre_x = pre_odds[1] if pre_odds else ''
        self.pre_p2 = pre_odds[2] if pre_odds else ''
        self.live_p1 = live_odds[0] if live_odds else ''
        self.live_x = live_odds[1] if live_odds else ''
        self.live_p2 = live_odds[2] if live_odds else ''
        self.flash_facts = flash_facts if flash_facts else ''
        self.dog = ''

    def get_pre_odds(self):
        return self.pre_p1, self.pre_x, self.pre_p2

    def get_live_odds(self):
        return self.live_p1, self.live_x, self.live_p2

    def get_odds(self):
        return self.pre_p1, self.pre_x, self.pre_p2, self.live_p1, self.live_x, self.live_p2, self.dog

    def update_dog(self):
        try:
            if float(self.pre_p1) < 1.91 and float(self.pre_p2) > 2:
                self.dog = '2'
            if float(self.pre_p2) < 1.91 and float(self.pre_p1) > 2:
                self.dog = '1'
        except Exception:
            print('BAD ODDS: {}'.format(self.pre_p1, self.pre_p2))


class Stats(object):
    def __init__(self):
        self.place = ''
        self.team = ''
        self.count_games = ''
        self.wins = ''
        self.draw = ''
        self.lose = ''
        self.goals = ''
        self.form = ''
        self.k_win = ''
        self.k_lose = ''

    def get_stat_json(self):
        return json.dumps({'team': self.team, 'place': self.place, 'cnt': self.count_games,
                           'w': self.wins, 'd': self.draw, 'l': self.lose, 'g': self.goals,
                           'f': self.form, 'kw': self.k_win, 'kl': self.k_lose
                           })


class Game(object):
    def __init__(self, game=None):
        self.time = game[0] if game else ''
        self.timer = game[1] if game else ''
        self.team_home = game[2] if game else ''
        self.rhcard = game[3] if game else ''
        self.score = game[4] if game else ''
        self.team_away = game[5] if game else ''
        self.racard = game[6] if game else ''
        self.part_top = game[7] if game else ''
        self.html_link = game[8] if game else ''
        self.odds = Odds()
        self.stat_home = ''
        self.stat_away = ''

    def get_score(self):
        cur_score = myscoresettings.MSC_SCORE_REGEX.search(self.score)
        return cur_score.groups() if cur_score else ('', '')

    def get_game_params(self):
        return self.time, self.timer, self.team_home, self.rhcard, self.score, self.team_away, self.racard, self.part_top, self.html_link

    @staticmethod
    def get_diff_game(game, new_game):
        event_type = ''
        new_score = myscoresettings.MSC_SCORE_REGEX.search(new_game.score)
        new_score = new_score.groups() if new_score else ('', '')
        game_score = myscoresettings.MSC_SCORE_REGEX.search(game.score)
        game_score = game_score.groups() if game_score else ('', '')

        exist_new_score = new_score[0].isdigit() and new_score[1].isdigit()
        exist_game_score = game_score[0].isdigit() and game_score[1].isdigit()

        timer = myscoresettings.MSC_TIMER_REGEX.search(new_game.timer)
        new_timer = timer.group() if timer else ''
        if (new_score[0] == new_score[1] == '0' or new_score[0] == new_score[1] == '') and new_game.rhcard == new_game.racard == ''\
                and new_timer:
            if int(new_timer) < myscoresettings.MSC_TIMER_NEW_EVENT:
                event_type = EventType.new_game

        if exist_new_score and exist_game_score and (new_score[0] != game_score[0] or new_score[1] != game_score[1]):
            event_type = EventType.goal

        if new_game.rhcard != game.rhcard or new_game.rhcard != game.rhcard:
            event_type = EventType.card_red

        return any([new_game.rhcard != game.rhcard, new_game.rhcard != game.rhcard,
                    new_score[0] != game_score[0], new_score[1] != game_score[1]]
                   ), event_type

    @staticmethod
    def _get_type_event(game, new_game):
        pass


class League(object):
    def __init__(self, header=None, game=None):
        self.header = ''
        self.game = {}
        self.count_game = 0
        if header:
            self.header = self.Header(header)
        if game:
            for item in game:
                self.game[self.count_game] = Game(item)
                self.count_game += 1

    def add_game(self, game):
        self.game[self.count_game] = game
        self.count_game += 1

    def add_header(self, header):
        self.header = self.Header(header)

    class Header(object):
        def __init__(self, header):
            self.html_link = header[0] if header else ''
            self.caption = header[1] if header else ''
            self.country = header[2] if header else ''


class MyScore(object):

    def __init__(self, html):
        self.log = logging
        self.html = html
        self.log.info('INIT BS')
        self.soup = BeautifulSoup(self.html, "html.parser")
        self.log.info('END INIT BS')

    def get_table(self, class_name):
        """
        Get table from html
        :return:
        """
        try:
            self.log.info('Get table: {}'.format(class_name))
            return self.soup.find_all('table', class_=class_name)
        except Exception:
            self.log.logging.exception("message")
            return ''

    def get_table_by_id(self, class_name):
        """
        Get table from html
        :return:
        """
        try:
            self.log.info('Get table: {}'.format(class_name))
            return self.soup.find_all('id', class_=class_name)
        except Exception:
            self.log.logging.exception("message")
            return ''

    def renew_html(self, html):
        """
        Update html for parsing BSoup
        :param html:
        :return:
        """
        self.html = html
        self.soup = BeautifulSoup(self.html, "html.parser")

    def parse_league_table(self, table):
        """
        Parse one table of league
        :param table:
        :return: Dict with data for league with games
        """
        curren_league = League()
        try:
            rows = table.find_all('tr')
            header_row = rows.pop(0)
            header_html_link = header_row.get('class')[1][4:]
            cols = header_row.find_all('td')
            caption = cols[1].findAll('span', {"tournament_part"})
            caption = caption[0].text if caption else ''
            flag = cols[1].findAll('span', 'flag')
            country = flag[0].get('title', '') if flag else ''
            curren_league.add_header((header_html_link, caption, country))
            cnt = 1
            for row in rows:
                html_link = row.get('id')[4:]
                cols = row.find_all('td')
                if cols:
                    time = cols[1].text.strip()
                    timer = cols[2].text.strip()
                    # team_home = cols[3].text.strip()
                    team_home = cols[3].findAll('span', {"class": "padr"})[0].text.strip()
                    rhcard = cols[3].findAll('span', {"class": "rhcard"})
                    rhcard = rhcard[0].get('class')[1][-1:] if rhcard else ''
                    score = ''.join(cols[4].text.strip().split())
                    # team_away = cols[5].text.strip()
                    team_away = cols[5].findAll('span', {"class": "padl"})[0].text.strip()
                    racard = cols[5].findAll('span', {"class": "racard"})
                    racard = racard[0].get('class')[1][-1:] if racard else ''
                    part_top = cols[6].text.strip()
                    curren_league.add_game(Game((time, timer, team_home, rhcard, score, team_away, racard, part_top, html_link)))

                cnt += 1
        except Exception as e:
            self.log.logging.exception("message")

        return curren_league

    def _parse_pre_odds(self, table_odds):
        odds = Odds()
        try:
            for tmp_table in table_odds:
                table_id = tmp_table.get('id')
                if table_id == myscoresettings.MSC_PRE_ODDS_TABLE:
                    rows = tmp_table.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if cols:
                            odds.pre_p1 = cols[1].text.strip().split()[1] if cols[1] else ''
                            odds.pre_x = cols[2].text.strip().split()[1] if cols[1] else ''
                            odds.pre_p2 = cols[3].text.strip().split()[1] if cols[1] else ''
                            odds.update_dog()
                if table_id == myscoresettings.MSC_LIVE_ODDS_TABLE:
                    rows = tmp_table.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if cols:
                            for c in cols:
                                self.log.info(c)
                            odds.live_p1 = cols[1].text.strip().split()[1] if cols[1] else ''
                            odds.live_x = cols[2].text.strip().split()[1] if cols[1] else ''
                            odds.live_p2 = cols[3].text.strip().split()[1] if cols[1] else ''
                if table_id == myscoresettings.MSC_FLASH_FACTS_TABLE:
                    rows = tmp_table.find_all('tr')
                    for row in rows:
                        odds.flash_facts += '\n' + row.text.strip()
        except:
            self.log.exception('Message')
        return odds

    def _parse_stat_table(self, stat_table):
        stat_table_list = []
        try:
            for tmp_table in stat_table:
                table_id = tmp_table.get('id')
                if table_id == myscoresettings.MSC_STAT_TYPE_1:
                    rows = tmp_table.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if cols:
                            total_teams = len(rows) - 1
                            stat = Stats()
                            stat.place = cols[0].text.strip().replace('.', '') + '/' + str(total_teams)
                            stat.team = cols[1].text.strip()
                            stat.count_games = cols[2].text.strip() + '/' + str((total_teams - 1) * 2)
                            stat.wins = cols[3].text.strip()
                            stat.draw = cols[4].text.strip()
                            stat.lose = cols[5].text.strip()
                            stat.goals = cols[6].text.strip()
                            if stat.goals:
                                try:
                                    tmp_g = stat.goals.split(':')
                                    if len(tmp_g) == 2:
                                        z = int(tmp_g[0])
                                        p = int(tmp_g[1])
                                        cnt = int(cols[2].text.strip())
                                        stat.k_win = str(round(z/cnt, 2))
                                        stat.k_lose = str(round(p/cnt, 2))
                                except Exception:
                                    self.log.exception('Message')
                            form = cols[8].findAll('a')
                            form_str = ''
                            for item in form:
                                tmp_list = item.attrs.get('class', '')
                                if len(tmp_list) > 1:
                                    if tmp_list[1] == 'form-w':
                                        form_str += 'B'
                                    if tmp_list[1] == 'form-d':
                                        form_str += 'H'
                                    if tmp_list[1] == 'form-l':
                                        form_str += 'П'
                            stat.form = form_str
                            stat_table_list.append(stat.get_stat_json())
        except:
            self.log.exception('Message')
        return stat_table_list

    def _update_game(self, game):
        """
        Renew record in soccer table
        :param game:
        :return:
        """
        update_sql = sql.UPDATE_ONE_GAME_BY_LINK.format(tbl=myscoresettings.MSC_SOCCER_TABLE,
                                                        link=game.html_link)
        params = (game.get_game_params())
        run_sql(update_sql, params=params)

    def _check_current_diff(self, exist_game, current_game):
        """
        Check differrence for onr game
        :param exist_game:
        :param current_game:
        :return: True if have difference
        """
        diff, event_type = Game.get_diff_game(exist_game, current_game)
        if diff:
            print("{} - {} event: {}".format(current_game.team_home, current_game.team_away, event_type))
            self._insert_event(current_game, event_type)
        self._update_game(current_game)
        return current_game, event_type

    def _insert_event(self, game, event_type):
        """
        Inser new event for game
        :param game:
        :return:
        """
        insert_sql = sql.INSERT_ONE_EVENT.format(tbl=myscoresettings.MSC_EVENT_TABLE)
        params = (*game.get_game_params(), event_type, datetime.now())
        run_sql(insert_sql, params)
        print('New event {}'.format(params))


    def _get_current_game(self, game):
        sql_get_game = sql.SELECT_GAME_BY_LINK.format(tbl=myscoresettings.MSC_SOCCER_TABLE,
                                                      link=game.html_link)
        result = run_sql(sql_get_game)
        return result

    def _insert_league(self, header):
        """
        Insert league in table league
        :param header:
        :return:
        """
        insert_sql = sql.INSERT_LEAGUE_IF_EXIST.format(tbl=myscoresettings.MSC_LEAGUE_TABLE,
                                                       link=header.html_link,
                                                       cap=header.caption,
                                                       country=header.country)
        run_sql(insert_sql)

    def _insert_game(self, header, game):
        """
        Insert new game in soccer table
        :param header:
        :param game:
        :return:
        """
        sql_leagie_id = sql.SELECT_LEAGUE_ID.format(tbl=myscoresettings.MSC_LEAGUE_TABLE, link=header.html_link)
        result = run_sql(sql_leagie_id)
        if result:
            id_league = result[0]
            insert_sql = sql.INSERT_ONE_GAME.format(tbl=myscoresettings.MSC_SOCCER_TABLE, league_id=id_league)
            params = (game.get_game_params())
            self.log.info(params)
            run_sql(insert_sql, params=params)

    def _get_current_game_odds(self, current_game):
        current_link = '{}/{}/{}/{}'.format(myscoresettings.MSC_BASE_LINK, myscoresettings.MSC_MATCH_LINK,
                                         current_game.html_link, myscoresettings.MSC_MATCH_SUMMARY_LINK)
        current_odds = Odds()
        with WebParser(current_link, True, myscoresettings.MSC_MATCH_SUMMARY_CLASS) as cu:
            msc_local = MyScore(cu.get_source_html())
            try:
                odds_table = msc_local.get_table(myscoresettings.MSC_ODDS)
                if odds_table:
                    current_odds = self._parse_pre_odds(odds_table)
            except Exception:
                myscore.log.exception("message")
        return current_odds

    def _get_current_game_table(self, current_game):
        current_link = '{}/{}/{}/{}'.format(myscoresettings.MSC_BASE_LINK, myscoresettings.MSC_MATCH_LINK,
                                         current_game.html_link, myscoresettings.MSC_MATCH_TABLE)
        current_stat = []
        with WebParser(current_link, True, myscoresettings.MSC_MATCH_SUMMARY_CLASS) as cu:
            msc_local = MyScore(cu.get_source_html())
            try:
                stat_table = msc_local.get_table(myscoresettings.MSC_STAT_TABLE)
                if stat_table:
                    current_stat = self._parse_stat_table(stat_table)
            except Exception:
                myscore.log.exception("message")
        return current_stat

    @staticmethod
    def _update_odds(current_game, odds):
        update_sql = sql.UPDATE_GAME_ODDS.format(tbl=myscoresettings.MSC_EVENT_TABLE, link=current_game.html_link)
        params = (odds.get_odds())
        run_sql(update_sql, params=params)

    @staticmethod
    def _update_stat(current_game, stat_list):
        update_sql = sql.UPDATE_GAME_STAT.format(tbl=myscoresettings.MSC_EVENT_TABLE, link=current_game.html_link)
        home_stat = ''
        away_stat = ''
        for item in stat_list:
            if item:
                tmp = json.loads(item)
                if current_game.team_home in tmp.get('team', ''):
                    home_stat = item
                if current_game.team_away in tmp.get('team', ''):
                    away_stat = item
        params = (home_stat, away_stat)
        run_sql(update_sql, params=params)

    @staticmethod
    def _get_event_odds(html_link):
        odds = Odds()
        select_sql = sql.SELECT_ODDS_BY_LINK.format(tbl=myscoresettings.MSC_EVENT_TABLE, link=html_link)
        result = run_sql(select_sql)
        if result:
            odds.live_p1 = result[0]
            odds.live_p2 = result[1]
            odds.live_x = result[2]
            odds.pre_p1 = result[3]
            odds.pre_p2 = result[4]
            odds.pre_x = result[5]
            odds.dog = result[6]
        return odds

    @staticmethod
    def _get_event_stat(html_link):
        stat = []
        select_sql = sql.SELECT_STAT_BY_LINK.format(tbl=myscoresettings.MSC_EVENT_TABLE, link=html_link)
        result = run_sql(select_sql)
        if result:
            stat.append(result[0])
            stat.append(result[1])
        else:
            stat = ['', '']
        return stat

    def calc_stat(self, html_link, dog):
        country_str = ''
        lg_str = ''
        try:
            sql_lg_id = sql.SELECT_LG_ID_AND_COUNTRY.format(link=html_link)
            res_lg_id = run_sql(sql_lg_id)
            if res_lg_id:
                lg = res_lg_id[0]
                country = res_lg_id[1]
            sql_0_1 = sql.SELECT_0_1_BY_COUNTRY.format(country=country, dog=dog)
            res_0_1 = run_sql(sql_0_1)
            res_0_1 = res_0_1[0] if res_0_1 else '0'
            sql_0_2 = sql.SELECT_0_2_BY_COUNTRY.format(country=country, dog=dog)
            res_0_2 = run_sql(sql_0_2)
            res_0_2 = res_0_2[0] if res_0_2 else '0'
            sql_1_1 = sql.SELECT_1_1_BY_COUNTRY.format(country=country, dog=dog)
            res_1_1 = run_sql(sql_1_1)
            res_1_1 = res_1_1[0] if res_1_1 else '0'
            sql_0_1_s = sql.SELECT_0_1_STAY_BY_COUNTRY.format(country=country, dog=dog)
            res_0_1_s = run_sql(sql_0_1_s)
            res_0_1_s = res_0_1_s[0] if res_0_1_s else '0'
            if res_0_1 != 0:
                kw = str(round(round(int(res_1_1) / int(res_0_1), 2) * 100)) + '%'
            else:
                kw = '-'
            if res_0_1 != 0:
                kp = str(round(round(int(res_0_2) / int(res_0_1), 2) * 100)) + '%'
            else:
                kp = '-'
            if res_0_1 != 0:
                ks = str(round(round(int(res_0_1_s) / int(res_0_1), 2) * 100)) + '%'
            else:
                ks = '-'
            country_str = 'Всего:{} В:{}({}) П:{}({}) П0:{}({})'.format(res_0_1, res_1_1, kw, res_0_2, kp, res_0_1_s, ks)

            sql_0_1 = sql.SELECT_0_1_BY_LG.format(lg=lg, dog=dog)
            res_0_1 = run_sql(sql_0_1)
            res_0_1 = res_0_1[0] if res_0_1 else '0'
            sql_0_2 = sql.SELECT_0_2_BY_LG.format(lg=lg, dog=dog)
            res_0_2 = run_sql(sql_0_2)
            res_0_2 = res_0_2[0] if res_0_2 else '0'
            sql_1_1 = sql.SELECT_1_1_BY_LG.format(lg=lg, dog=dog)
            res_1_1 = run_sql(sql_1_1)
            res_1_1 = res_1_1[0] if res_1_1 else '0'
            sql_0_1_s = sql.SELECT_0_1_STAY_BY_LG.format(lg=lg, dog=dog)
            res_0_1_s = run_sql(sql_0_1_s)
            res_0_1_s = res_0_1_s[0] if res_0_1_s else '0'
            if res_0_1 != 0:
                kw = str(round(round(int(res_1_1) / int(res_0_1), 2) * 100)) + '%'
            else:
                kw = '-'
            if res_0_1 != 0:
                kp = str(round(round(int(res_0_2) / int(res_0_1), 2) * 100)) + '%'
            else:
                kp = '-'
            if res_0_1 != 0:
                ks = str(round(round(int(res_0_1_s) / int(res_0_1), 2) * 100)) + '%'
            else:
                ks = '-'
            lg_str = 'Лига: {} В:{}({}) П:{}({}) П0:{}({})'.format(res_0_1, res_1_1, kw, res_0_2, kp, res_0_1_s, ks)
        except Exception:
            self.log.exception('message')
        return country_str + '\n' + lg_str




    def send_bot_message(self, current_game, exist_game, league_header):
        send_message = False
        predict_message = ''
        country = league_header.country
        chemp = league_header.caption
        last_score = exist_game.get_score()
        curr_score = current_game.get_score()
        total_str = ''
        if exist_game.odds.dog == '1':
            if int(curr_score[0]) > int(last_score[0]) and int(curr_score[1]) == 0 and int(last_score[0]) == 0:
                send_message = True
                predict_message = 'Ставка П2'

            if int(curr_score[0]) > int(last_score[0]) and int(curr_score[1]) == 0 and int(last_score[0]) == 1:
                send_message = True
                predict_message = 'Отрыв хозяев увеличился('

            if int(curr_score[0]) == int(last_score[0]) and int(curr_score[1]) == 1 and int(last_score[0]) == 2:
                send_message = True
                predict_message = 'Гости сократили разрыв'

            if int(curr_score[0]) == int(last_score[0]) == 1 and int(curr_score[1]) == 1:
                send_message = True
                predict_message = 'СТАВКА ЗАШЛА!'

            if int(curr_score[0]) == int(last_score[0]) == 2 and int(curr_score[1]) == 2:
                send_message = True
                predict_message = 'ОТЫГРАЛИСЬ!'


        if exist_game.odds.dog == '2':
            total_str = self.calc_stat(league_header.html_link, exist_game.odds.dog)
            if int(curr_score[1]) > int(last_score[1]) and int(curr_score[0]) == 0 and int(last_score[1]) == 0:
                send_message = True
                predict_message = 'Ставка П1'

            if int(curr_score[1]) > int(last_score[1]) and int(curr_score[0]) == 0 and int(last_score[1]) == 1:
                send_message = True
                predict_message = 'Отрыв гостей увеличился('

            if int(curr_score[1]) == int(last_score[1]) and int(curr_score[0]) == 1 and int(last_score[1]) == 2:
                send_message = True
                predict_message = 'Хозяева сократили разрыв'

            if int(curr_score[1]) == int(last_score[1]) == 1 and int(curr_score[0]) == 1:
                send_message = True
                predict_message = 'СТАВКА ЗАШЛА!'

            if int(curr_score[1]) == int(last_score[1]) == 2 and int(curr_score[0]) == 2:
                send_message = True
                predict_message = 'ОТЫГРАЛИСЬ!'

        info = """<a href="http://t.myscore.ru/#!/match/{}/match-summary">Подробности</a>""".format(exist_game.html_link)
        stat_str = ''
        if exist_game.stat_home and exist_game.stat_away:
            home = json.loads(exist_game.stat_home)
            away = json.loads(exist_game.stat_away)
            stat_str = '{} {}\nИ:{} В:{} Н:{} П:{} Г:{} {}\nkЗ: {} kП: {}\n\n{} {}\nИ:{} В:{} Н:{} П:{} Г:{} {}\nkЗ: {} kП: {}'.format(
                home['place'], home['team'], home['cnt'], home['w'], home['d'], home['l'], home['g'], home['f'],
                home.get('kw', ''), home.get('kl', ''),
                away['place'], away['team'], away['cnt'], away['w'], away['d'], away['l'], away['g'], away['f'],
                away.get('kw', ''), away.get('kl', '')
            )



        message = "<b>{}</b>\n {} {} \n{} - {} dog:{}\n <i> Счет: {} Время:{}</i>\n <i> Кэфы:{} {} {}</i>\n\n{}\n\n{}\n\n{} ".format(
            predict_message, country, chemp, current_game.team_home, current_game.team_away,
            exist_game.odds.dog, current_game.score, current_game.timer,
            exist_game.odds.pre_p1, exist_game.odds.pre_x, exist_game.odds.pre_p2, stat_str, total_str, info)

        self.log.info(message)
        if send_message:
            for i in range(11):
                try:
                    proxy_list = [
                        'https://195.201.43.199:3128',
                        'https://66.70.255.195:3128',
                        'https://198.50.142.59:8080',
                        'https://158.69.206.181:8888',
                        'https://144.76.62.29:3128', #jr
                        'https://94.242.58.108:10010',
                        'https://66.70.147.196:3128',
                        'https://66.70.147.197:3128',
                        'https://54.39.46.86:3128',
                        'https://52.91.209.114:8888',
                        'https://52.91.209.147:8888',
                    ]
                    REQUEST_KWARGS = {
                         'proxy_url': proxy_list[i],
                    }
                    updater = Updater(TOKEN, request_kwargs=REQUEST_KWARGS)
                    updater.bot.send_message(chat_id=BOT_FATHER, text=message, parse_mode='HTML', disable_web_page_preview=True)
                    updater.bot.send_message(chat_id=DOCENT, text=message, parse_mode='HTML', disable_web_page_preview=True)
                    updater.bot.send_message(chat_id=ALEX, text=message, parse_mode='HTML', disable_web_page_preview=True)
                    updater.bot.send_message(chat_id=VOVEI, text=message, parse_mode='HTML',
                                             disable_web_page_preview=True)
                except Exception:
                    self.log.exception('message')
                else:
                    break


    def process_league(self, league):
        """
        Update events
        :param table_dict:
        :return: True if ok
        """

        self._insert_league(league.header)
        for game in league.game:
            # if len(league.game[game].score) > 4:
            #     pass
            #     self.log.info("{} \t {} - {} \t {}".format(league.game[game].timer, league.game[game].team_home,
            #                                                league.game[game].team_away, league.game[game].score))

            exist_game = self._get_current_game(league.game[game])
            if exist_game:
                exist_game = Game(exist_game)
                event_odds = self._get_event_odds(exist_game.html_link)
                event_stat = self._get_event_stat(exist_game.html_link)
                exist_game.odds = event_odds
                exist_game.stat_home = event_stat[0]
                exist_game.stat_away = event_stat[1]
                current_game, event_type = self._check_current_diff(exist_game, league.game[game])
                # test
                # current_stat = self._get_current_game_table(current_game)
                if event_type == EventType.new_game:
                    if not exist_game.odds.pre_p1 or not exist_game.odds.live_p1:
                        current_odds = self._get_current_game_odds(current_game)
                        # test
                        current_stat = self._get_current_game_table(current_game)
                        self._update_stat(current_game, current_stat)
                        self._update_odds(current_game, current_odds)
                        self.log.info("{}\t\t{}".format((current_odds.get_pre_odds()), (current_odds.get_live_odds())))
                if event_type == EventType.goal:
                    self._update_odds(current_game, exist_game.odds)
                    self._update_stat(current_game, [exist_game.stat_home, exist_game.stat_away])
                    if event_odds.dog:
                        current_score = current_game.get_score()
                        if current_score[0] and current_score[1]:
                            if 0 < int(current_score[0]) + int(current_score[1]) <= 4:
                                self.send_bot_message(current_game, exist_game, league.header)

            else:
                self._insert_game(league.header, league.game[game])
        pass


if __name__ == '__main__':
    with WebParser('https://www.myscore.ru/', True, myscoresettings.MSC_MAIN_TABLE) as w:
        myscore = MyScore(w.get_source_html())
        cnt = myscoresettings.WORK_TIME_HOUR * 60
        while cnt > 0:
            try:
                myscore.renew_html(w.get_source_html())
                # main_table = myscore.get_div(myscoresettings.MSC_MAIN_TABLE)
                soccer_tables = myscore.get_table(myscoresettings.MSC_SOCCER_TABLE)
                if soccer_tables:
                    # soccer_tables = myscore.get_table(main_table[0], myscoresettings.MSC_SOCCER_TABLE)
                    for table in soccer_tables:
                        league = myscore.parse_league_table(table)
                        myscore.process_league(league)
            except Exception as e:
                myscore.log.exception("message")
            sleep(w.sleeptime)
            print(cnt)
            cnt -= 1



        # main_table = myscore.get_table(class_name=myscoresettings.MSC_SOCCER_TABLE)
        # print(main_table)
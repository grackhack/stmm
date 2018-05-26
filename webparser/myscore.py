import re
from datetime import datetime
from time import sleep
import logging

import sys
from bs4 import BeautifulSoup
from webparser import myscoresettings
from webparser.dbconnection import run_sql
from webparser.seleniumparser import WebParser
from webparser import sql

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

    def get_pre_odds(self):
        return self.pre_p1, self.pre_x, self.pre_p2

    def get_live_odds(self):
        return self.live_p1, self.live_x, self.live_p2

    def get_odds(self):
        return self.pre_p1, self.pre_x, self.pre_p2, self.live_p1, self.live_x, self.live_p2


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

        if (new_score[0] == new_score[1] == '0' or new_score[0] == new_score[1] == '') and new_game.rhcard == new_game.racard == ''\
                and re.search(r'[\d]+', new_game.timer):
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
                    time = cols[1].text
                    timer = cols[2].text.strip()
                    team_home = cols[3].text
                    rhcard = cols[3].findAll('span', {"class": "rhcard"})
                    rhcard = rhcard[0].get('class')[1][-1:] if rhcard else ''
                    score = cols[4].text
                    team_away = cols[5].text
                    racard = cols[5].findAll('span', {"class": "racard"})
                    racard = racard[0].get('class')[1][-1:] if racard else ''
                    part_top = cols[6].text
                    curren_league.add_game(Game((time, timer, team_home, rhcard, score, team_away, racard, part_top, html_link)))

                cnt += 1
        except Exception as e:
            self.log.logging.exception("message")

        return curren_league

    def _parse_pre_odds(self, table_odds):
        odds = Odds()
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
            if table_id == myscoresettings.MSC_LIVE_ODDS_TABLE:
                rows = tmp_table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if cols:
                        odds.live_p1 = cols[1].text.strip().split()[1] if cols[1] else ''
                        odds.live_x = cols[2].text.strip().split()[1] if cols[1] else ''
                        odds.live_p2 = cols[3].text.strip().split()[1] if cols[1] else ''
            if table_id == myscoresettings.MSC_FLASH_FACTS_TABLE:
                rows = tmp_table.find_all('tr')
                for row in rows:
                    odds.flash_facts += row.text
        return odds

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
        with WebParser(current_link, False, myscoresettings.MSC_MATCH_SUMMARY_CLASS) as cu:
            msc_local = MyScore(cu.get_source_html())
            try:
                odds_table = msc_local.get_table(myscoresettings.MSC_ODDS)
                if odds_table:
                    current_odds = self._parse_pre_odds(odds_table)
                    return current_odds
            except Exception:
                myscore.log.exception("message")

    @staticmethod
    def _update_odds(current_game, odds):
        update_sql = sql.UPDATE_GAME_ODDS.format(tbl=myscoresettings.MSC_EVENT_TABLE, link=current_game.html_link)
        params = (odds.get_odds())
        run_sql(update_sql, params=params)

    def process_league(self, league):
        """
        Update events
        :param table_dict:
        :return: True if ok
        """

        self._insert_league(league.header)
        for game in league.game:
            if len(league.game[game].score) > 4:
                self.log.info("{} \t {} - {} \t {}".format(league.game[game].timer, league.game[game].team_home,
                                                           league.game[game].team_away, league.game[game].score))

            exist_game = self._get_current_game(league.game[game])
            if exist_game:
                current_game, event_type = self._check_current_diff(Game(exist_game), league.game[game])
                if event_type == EventType.new_game:
                    if not Game(exist_game).odds.pre_p1:
                        current_odds = self._get_current_game_odds(current_game)
                        self.log.info("{}\t\t{}".format((current_odds.get_pre_odds()), (current_odds.get_live_odds())))
                        self._update_odds(current_game, current_odds)

            else:
                self._insert_game(league.header, league.game[game])
        pass


if __name__ == '__main__':
    with WebParser('https://www.myscore.ru/', False, myscoresettings.MSC_MAIN_TABLE) as w:
        myscore = MyScore(w.get_source_html())
        cnt = 5*60
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
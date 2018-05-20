import re
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

    def get_game_params(self):
        return self.time, self.timer, self.team_home, self.rhcard, self.score, self.team_away, self.racard, self.part_top, self.html_link

    @staticmethod
    def get_diff_game(game, new_game):
        new_score = myscoresettings.MSC_SCORE_REGEX.search(new_game.score)
        new_score = new_score.groups() if new_score else ('', '')
        game_score = myscoresettings.MSC_SCORE_REGEX.search(game.score)
        game_score = game_score.groups() if game_score else ('', '')
        return any([new_game.rhcard != game.rhcard, new_game.rhcard != game.rhcard,
                    new_score[0] != game_score[0], new_score[1] != game_score[1]]
                   )


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

    def renew_html(self, html):
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
                html_link = row.get('id')
                cols = row.find_all('td')
                if cols:
                    time = cols[1].text
                    timer = cols[2].text
                    team_home = cols[3].text
                    rhcard = cols[3].findAll('span', {"class":"rhcard"})
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

    def _update_game(self, game):
        update_sql = sql.UPDATE_ONE_GAME_BY_LINK.format(tbl=myscoresettings.MSC_SOCCER_TABLE,
                                                        link=game.html_link)
        params = (game.get_game_params())
        run_sql(update_sql, params=params)

    def _check_current_diff(self, exist_game, current_game):
        diff = Game.get_diff_game(exist_game, current_game)
        if diff:
            self._insert_event(current_game)
        self._update_game(current_game)
        return diff

    def _insert_event(self, game):
        insert_sql = sql.INSERT_ONE_EVENT.format(tbl=myscoresettings.MSC_EVENT_TABLE)
        params = (game.get_game_params())
        run_sql(insert_sql, params)
        print('New event')


    def _get_current_game(self, game):
        sql_get_game = sql.SELECT_GAME_BY_LINK.format(tbl=myscoresettings.MSC_SOCCER_TABLE,
                                                      link=game.html_link)
        result = run_sql(sql_get_game)
        return result

    def _insert_league(self, header):
        insert_sql = sql.INSERT_LEAGUE_IF_EXIST.format(tbl=myscoresettings.MSC_LEAGUE_TABLE,
                                                       link=header.html_link,
                                                       cap=header.caption,
                                                       country=header.country)
        run_sql(insert_sql)

    def _insert_game(self, header, game):
        sql_leagie_id = sql.SELECT_LEAGUE_ID.format(tbl=myscoresettings.MSC_LEAGUE_TABLE, link=header.html_link)
        result = run_sql(sql_leagie_id)
        if result:
            id_league = result[0]
            insert_sql = sql.INSERT_ONE_GAME.format(tbl=myscoresettings.MSC_SOCCER_TABLE, league_id=id_league)
            params = (game.get_game_params())
            self.log.info(params)
            run_sql(insert_sql, params=params)

    def process_league(self, league):
        """
        Update db for laegue
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
                self._check_current_diff(Game(exist_game), league.game[game])
            else:
                self._insert_game(league.header, league.game[game])
        pass


if __name__ == '__main__':
    with WebParser('https://www.myscore.ru/', False) as w:
        myscore = MyScore(w.get_source_html())
        cnt = 30
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
            cnt -= 1



        # main_table = myscore.get_table(class_name=myscoresettings.MSC_SOCCER_TABLE)
        # print(main_table)
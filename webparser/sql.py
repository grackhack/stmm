SELECT_GAME_BY_LINK = """SELECT begin_time, timer,team_home,rhcard,score,
                      team_away, racard, part_top, html_link from {tbl} where html_link = '{link}'"""

SELECT_LEAGUE_ID = "SELECT id FROM {tbl} WHERE html_link = '{link}'"

INSERT_LEAGUE_IF_EXIST = """ INSERT INTO {tbl} (html_link, caption, country)
                              SELECT * FROM (SELECT '{link}', '{cap}', '{country}') AS tmp
                              WHERE NOT EXISTS (
                              SELECT html_link FROM {tbl} WHERE html_link = '{link}'
                             ) LIMIT 1;"""

INSERT_ONE_GAME = """INSERT into {tbl} (begin_time, timer,team_home,rhcard,score,
                    team_away, racard, part_top, html_link, league_id) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, {league_id})"""

UPDATE_ONE_GAME_BY_LINK = """UPDATE {tbl} set begin_time=?, timer=?, team_home=?, rhcard=?, score=?,
                    team_away=?, racard=?, part_top=?, html_link=? where html_link='{link}'"""

INSERT_ONE_EVENT = """INSERT into {tbl} (begin_time, timer,team_home,rhcard,score,
                    team_away, racard, part_top, html_link) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""

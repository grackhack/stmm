SELECT_GAME_BY_LINK = """SELECT begin_time, timer,team_home, rhcard, score,
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
                    team_away, racard, part_top, html_link, event_type, time_stamp,
                    live_p1, live_p2, live_x, pre_p1, pre_p2, pre_x, dog) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,? , '', '', '', '', '', '', '')"""

UPDATE_GAME_ODDS = """UPDATE {tbl} set pre_p1=?, pre_x=?, pre_p2=?, 
                      live_p1=?, live_x=?, live_p2=? where html_link='{link}'"""

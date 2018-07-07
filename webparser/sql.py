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
                    live_p1, live_p2, live_x, pre_p1, pre_p2, pre_x, dog, stat_home, stat_away) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,? , '', '', '', '', '', '', '', '', '')"""

UPDATE_GAME_ODDS = """UPDATE {tbl} set pre_p1=?, pre_x=?, pre_p2=?, 
                      live_p1=?, live_x=?, live_p2=?, dog=? where html_link='{link}'"""

UPDATE_GAME_STAT = """UPDATE {tbl} set stat_home=?, stat_away=? where html_link='{link}'"""

SELECT_ODDS_BY_LINK = """SELECT live_p1, live_p2, live_x, pre_p1, pre_p2, pre_x, dog
                         from {tbl} where html_link = '{link}' and pre_p1<>'' LIMIT 1"""

SELECT_STAT_BY_LINK = """SELECT stat_home, stat_away
                         from {tbl} where html_link = '{link}' and stat_home<>'' LIMIT 1"""

SELECT_0_1_BY_COUNTRY = """
SELECT count(DISTINCT html_link) 
  FROM event_game
 WHERE html_link IN (
           SELECT DISTINCT html_link
             FROM soccer
            WHERE league_id IN (
                      SELECT id
                        FROM League
                       WHERE country = '{country}'
                  )
       )
AND 
       dog = '{dog}' AND 
       score IN ('0-1') AND 
       timer <= '45'
  """

SELECT_0_2_BY_COUNTRY = """
SELECT count(DISTINCT html_link)
  FROM event_game
 WHERE html_link IN (
           SELECT html_link
             FROM event_game
            WHERE html_link IN (
                      SELECT DISTINCT html_link
                        FROM soccer
                       WHERE league_id IN (
                                 SELECT id
                                   FROM League
                                  WHERE country = '{country}'
                             )
                  )
AND 
                  dog = '{dog}' AND 
                  score IN ('0-1')  AND 
                  timer <= '45'
       )
AND 
       score IN ('0-2')
"""

SELECT_1_1_BY_COUNTRY = """
SELECT count(DISTINCT html_link)
  FROM event_game
 WHERE html_link IN (
           SELECT html_link
             FROM event_game
            WHERE html_link IN (
                      SELECT DISTINCT html_link
                        FROM soccer
                       WHERE league_id IN (
                                 SELECT id
                                   FROM League
                                  WHERE country = '{country}'
                             )
                  )
AND 
                  dog = '{dog}' AND 
                  score IN ('0-1')  AND timer <= '45'                  
       )
AND 
       score IN ('1-1')
"""

SELECT_0_1_STAY_BY_COUNTRY = """
SELECT count(DISTINCT html_link)
  FROM event_game
 WHERE html_link IN (
           SELECT DISTINCT html_link
             FROM soccer
            WHERE league_id IN (
                      SELECT id
                        FROM League
                       WHERE country = '{country}'
                  )
       )
AND 
       dog = '{dog}' AND 
       score IN ('0-1') AND 
       timer <= '45' AND 
       html_link NOT IN (
           SELECT html_link
             FROM event_game
            WHERE html_link IN (
                      SELECT html_link
                        FROM event_game
                       WHERE html_link IN (
                                 SELECT DISTINCT html_link
                                   FROM soccer
                                  WHERE league_id IN (
                                            SELECT id
                                              FROM League
                                             WHERE country = '{country}'
                                        )
                             )
AND 
                             dog = '{dog}' AND 
                             score IN ('0-1') AND 
                             timer <= '45' 
                  )
AND 
                  score IN ('0-2') 
       )
AND 
       html_link NOT IN (
           SELECT html_link
             FROM event_game
            WHERE html_link IN (
                      SELECT html_link
                        FROM event_game
                       WHERE html_link IN (
                                 SELECT DISTINCT html_link
                                   FROM soccer
                                  WHERE league_id IN (
                                            SELECT id
                                              FROM League
                                             WHERE country = '{country}'
                                        )
                             )
AND 
                             dog = '{dog}' AND 
                             score IN ('0-1') AND 
                             timer <= '45'
                  )
AND 
                  score IN ('1-1') 
       )
"""

SELECT_0_1_BY_LG = """
SELECT count(DISTINCT html_link) 
  FROM event_game
 WHERE html_link IN (
           SELECT DISTINCT html_link
             FROM soccer
            WHERE league_id = {lg}
       )
AND 
       dog = '{dog}' AND 
       score IN ('0-1') AND 
       timer <= '45'
  """

SELECT_0_2_BY_LG = """
SELECT count(DISTINCT html_link)
  FROM event_game
 WHERE html_link IN (
           SELECT html_link
             FROM event_game
            WHERE html_link IN (
                      SELECT DISTINCT html_link
                        FROM soccer
                       WHERE league_id = {lg}
                  )
AND 
                  dog = '{dog}' AND 
                  score IN ('0-1')  AND 
                  timer <= '45'
       )
AND 
       score IN ('0-2')
"""

SELECT_1_1_BY_LG = """
SELECT count(DISTINCT html_link)
  FROM event_game
 WHERE html_link IN (
           SELECT html_link
             FROM event_game
            WHERE html_link IN (
                      SELECT DISTINCT html_link
                        FROM soccer
                       WHERE league_id = {lg}
                  )
AND 
                  dog = '{dog}' AND 
                  score IN ('0-1')  AND timer <= '45'                  
       )
AND 
       score IN ('1-1')
"""

SELECT_0_1_STAY_BY_LG = """
SELECT count(DISTINCT html_link)
  FROM event_game
 WHERE html_link IN (
           SELECT DISTINCT html_link
             FROM soccer
            WHERE league_id = {lg}
       )
AND 
       dog = '{dog}' AND 
       score IN ('0-1') AND 
       timer <= '45' AND 
       html_link NOT IN (
           SELECT html_link
             FROM event_game
            WHERE html_link IN (
                      SELECT html_link
                        FROM event_game
                       WHERE html_link IN (
                                 SELECT DISTINCT html_link
                                   FROM soccer
                                  WHERE league_id = {lg}
                             )
AND 
                             dog = '{dog}' AND 
                             score IN ('0-1') AND 
                             timer <= '45' 
                  )
AND 
                  score IN ('0-2') 
       )
AND 
       html_link NOT IN (
           SELECT html_link
             FROM event_game
            WHERE html_link IN (
                      SELECT html_link
                        FROM event_game
                       WHERE html_link IN (
                                 SELECT DISTINCT html_link
                                   FROM soccer
                                  WHERE league_id = {lg}
                             )
AND 
                             dog = '{dog}' AND 
                             score IN ('0-1') AND 
                             timer <= '45'
                  )
AND 
                  score IN ('1-1') 
       )
"""

SELECT_LG_ID_AND_COUNTRY = """
SELECT id, country FROM league where html_link = '{link}'
"""


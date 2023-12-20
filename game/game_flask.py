import flask
import sqlite3

app = flask.Flask(__name__, template_folder="views")
@app.route('/')
def home():
   connection = sqlite3.connect('../resources/SQLITE/rpg_game.db')
   cursor = connection.cursor()
   cursor.execute('SELECT * FROM stats')
   players = cursor.fetchall()
   connection.close()

   list_players = []

   for player in players:
     list_players.append({
        "player_id":                   player[0],
        "player_name":                 player[1],
        "player_attack":               player[2],
        "player_attack_speed":         player[3],
        "player_defense":              player[4],
        "player_life":                 player[5],
        "player_regeneration_speed":   player[6],
        "player_level":                player[7]
     })

   return flask.render_template('index.html', players_stats_list=list_players)

@app.route('/add', methods=['GET', 'POST'])
def add():
   if flask.request.method == 'POST':
      parameters = {}
      parameters["name"]               = flask.request.values.get('name')
      parameters["attack"]             = flask.request.values.get('attack')
      parameters["attack_speed"]       = flask.request.values.get('attack_speed')
      parameters["defense"]            = flask.request.values.get('defense')
      parameters["life"]               = flask.request.values.get('life')
      parameters["regeneration_speed"] = flask.request.values.get('regeneration_speed')
      parameters["level"]              = flask.request.values.get('level')

      connection = sqlite3.connect('../resources/SQLITE/rpg_game.db')

      cursor = connection.cursor()
      cursor.execute('INSERT INTO stats (player_name, player_attack, player_attack_speed, player_defense, player_life, player_regeneration_speed, player_level) VALUES(:name, :attack, :attack_speed, :defense, :life, :regeneration_speed, :level)',
                     parameters)
      connection.commit()
      connection.close()

      return flask.redirect('/')
   else:
      return flask.render_template('add.html')

@app.route('/delete/<player_id>')
def delete(player_id):
   connection = sqlite3.connect('../resources/SQLITE/rpg_game.db')

   cursor = connection.cursor()
   cursor.execute('DELETE FROM stats WHERE player_id = ' + player_id)
   connection.commit()
   connection.close()

   return flask.redirect('/')

@app.route('/Area')
def Area():
   connection = sqlite3.connect('../resources/SQLITE/rpg_game.db')
   cursor = connection.cursor()
   cursor.execute("""
                  SELECT areas.area_id, areas.area_name, areas.area_max_entity_count, asp.area_source_id, asp.area_destination_id, bsp.area_source_id, bsp.area_destination_id FROM areas
                     left outer JOIN areas_paths asp ON areas.area_id = asp.area_source_id
                     left outer JOIN areas_paths bsp ON areas.area_id = bsp.area_destination_id 
                  GROUP BY(asp.area_source_id, asp.area_destination_id)
                  """)
   areas = cursor.fetchall()

   connection.close()
   areas_list = []

   for area in areas:
     areas_list.append({
        "area_id":                   area[0],
        "area_name":                 area[1],
        "area_max_entity_count":     area[2],
        "area_source_id_0":          area[3],
        "area_destination_id_0":     area[4],
        "area_source_id_1":          area[5],
        "area_destination_id_1":     area[6],
     })

   return flask.render_template('Area.html')

@app.route('/api/players', methods=['GET'])
def get_players():
   connection = sqlite3.connect('../resources/SQLITE/rpg_game.db')
   cursor = connection.cursor()
   cursor.execute('SELECT * FROM players')
   players = cursor.fetchall()
   connection.close()

   list_players = []

   for player in players:
     list_players.append({
        "player_id":                   player[0],
        "player_name":                 player[1],
        "player_attack":               player[2],
        "player_attack_speed":         player[3],
        "player_defense":              player[4],
        "player_life":                 player[5],
        "player_regeneration_speed":   player[6],
        "player_level":                player[7]
     })

   return flask.jsonify(list_players)

'''
@app.route('/api/dogs', methods=['POST'])
def add_dog():
   if flask.request.method == 'POST':
      # get data from request body
      name = flask.request.json['name']
      age = flask.request.json['age']
      race = flask.request.json['race']


      connection = sqlite3.connect('data.db')

      cursor = connection.cursor()
      cursor.execute('INSERT INTO dogs (name, age, race) VALUES ("' + name + '", "' + str(age) + '", "' + race + '")')
      connection.commit()
      connection.close()

      return flask.jsonify({
         "message": "Dog added successfully"
      })
'''
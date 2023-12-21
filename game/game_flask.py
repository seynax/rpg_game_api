import flask
import sqlite3

app = flask.Flask(__name__, template_folder="views")
@app.route('/')
def home():
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

   return flask.render_template('index.html', players_stats_list=list_players)

@app.route('/add', methods=['GET', 'POST'])
def add():
   if flask.request.method == 'POST':
      parameters = {}
      parameters["name"]               = flask.request.values.get('name')
      parameters["zone_active"]        = 1
      parameters["attack"]             = flask.request.values.get('attack')
      parameters["attack_speed"]       = flask.request.values.get('attack_speed')
      parameters["defense"]            = flask.request.values.get('defense')
      parameters["life"]               = flask.request.values.get('life')
      parameters["regeneration_speed"] = flask.request.values.get('regeneration_speed')
      parameters["level"]              = flask.request.values.get('level')

      connection = sqlite3.connect('../resources/SQLITE/rpg_game.db')

      cursor = connection.cursor()
      cursor.execute('INSERT INTO players (player_name, player_zone_active, player_attack, player_attack_speed, player_defense, player_life, player_regeneration_speed, player_level) VALUES(:name, :zone_active, :attack, :attack_speed, :defense, :life, :regeneration_speed, :level)',
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
   cursor.execute('DELETE FROM players WHERE player_id = ' + player_id)
   connection.commit()
   connection.close()

   return flask.redirect('/')

@app.route('/Area')
def Area():
   connection = sqlite3.connect('../resources/SQLITE/rpg_game.db')
   cursor = connection.cursor()
   cursor.execute('SELECT * FROM areas')
   areas = cursor.fetchall()

   areas_list = []

   for area in areas:
      cursor.execute("SELECT areas_paths.area_source_id, areas_paths.area_destination_id FROM areas_paths WHERE areas_paths.area_source_id = " + str(area[0]))
      areas_source_paths = cursor.fetchall()
      cursor.execute("SELECT areas_paths.area_destination_id, areas_paths.area_source_id FROM areas_paths WHERE areas_paths.area_destination_id = " + str(area[0]))
      areas_destination_paths = cursor.fetchall()

      paths = []
      for source_path in areas_source_paths:
         paths.append((source_path[0], source_path[1]))
      for destination_path in areas_destination_paths:
         paths.append((destination_path[0], destination_path[1]))

      areas_list.append({
         "area_id":                   area[0],
         "area_name":                 area[1],
         "area_max_entity_count":     area[2],
         "area_paths":                paths
      })

   connection.close()

   return flask.render_template('Area.html', areas_list=areas_list)

@app.route('/api/players', methods=['GET'])
def get_players():
   connection = sqlite3.connect('../resources/SQLITE/rpg_game.db')
   cursor = connection.cursor()
   cursor.execute('SELECT * FROM players')
   players = cursor.fetchall()
   connection.close()

   players_list = []

   for player in players:
     players_list.append({
        "player_id":                   player[0],
        "player_name":                 player[1],
        "player_attack":               player[2],
        "player_attack_speed":         player[3],
        "player_defense":              player[4],
        "player_life":                 player[5],
        "player_regeneration_speed":   player[6],
        "player_level":                player[7]
     })

   return flask.jsonify(players_list)

@app.route('/api/areas', methods=['GET'])
def get_areas():
   connection = sqlite3.connect('../resources/SQLITE/rpg_game.db')
   cursor = connection.cursor()
   cursor.execute('SELECT * FROM areas')
   areas = cursor.fetchall()

   areas_list = []

   for area in areas:
      cursor.execute("SELECT areas_paths.area_source_id, areas_paths.area_destination_id FROM areas_paths WHERE areas_paths.area_source_id = " + str(area[0]))
      areas_source_paths = cursor.fetchall()
      cursor.execute("SELECT areas_paths.area_destination_id, areas_paths.area_source_id FROM areas_paths WHERE areas_paths.area_destination_id = " + str(area[0]))
      areas_destination_paths = cursor.fetchall()

      paths = []
      for source_path in areas_source_paths:
         paths.append((source_path[0], source_path[1]))
      for destination_path in areas_destination_paths:
         paths.append((destination_path[0], destination_path[1]))

      areas_list.append({
         "area_id":                   area[0],
         "area_name":                 area[1],
         "area_max_entity_count":     area[2],
         "area_paths":                paths
      })

   connection.close()

   return flask.jsonify(areas_list)

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
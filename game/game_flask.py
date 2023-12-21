import flask
import sqlite3

app = flask.Flask(__name__, template_folder="views")

## HOME

@app.route('/')
def home():
   return get_players()

## Function AND API REQUESTS Management

## PLAYERS
@app.route('/players')
def get_players():
   return flask.render_template('index.html', players_stats_list=get_players_list())

@app.route('/player/<player_id>')
def get_player(player_id):
   return flask.render_template('index.html', players_stats_list=get_player(player_id))

@app.route('/add/player', methods=['GET', 'POST'])
def add_player():
   values = get_form_values(["name", "zone_active", "attack", "attack_speed", "defense", "life", "regeneration_speed", "level"])
   if values == None:
      return flask.render_template('add.html')



   return flask.redirect('/')

@app.route('/delete/player/<player_id>')
def delete_player(player_id):
   commit_request("DELETE FROM players WHERE player_id = " + str(player_id))

   return flask.redirect('/')

@app.route('/api/players', methods=['GET'])
def api_get_players():
   return flask.jsonify(get_players_list())

@app.route('/api/player/<player_id>')
def api_get_player(player_id):
   return flask.jsonify(get_player(player_id))

@app.route('/api/add/player', methods=['GET', 'POST'])
def api_add_player():
   player = get_json_values(["name", "zone_active", "attack", "attack_speed", "defense", "life", "regeneration_speed", "level"])
   return json_success_message("Player added") if insert_player(player) else json_failed_message("Player add")

@app.route('/api/add/players', methods=['GET', 'POST'])
def api_add_players():
   player = get_json_array_values(["name", "zone_active", "attack", "attack_speed", "defense", "life", "regeneration_speed", "level"])
   return json_success_message("Players added") if insert_players(player) else json_failed_message("Players add")

@app.route('/delete/<player_id>')
def api_delete_player(player_id):
   commit_request("DELETE FROM players WHERE player_id = " + str(player_id))

   return flask.redirect('/')

## AREAS
@app.route('/areas')
def Area():
   return flask.render_template('Area.html', areas_list=get_areas_and_path_list())

@app.route('/api/areas', methods=['GET'])
def get_areas():
   return flask.jsonify(get_areas_and_path_list())

## JSON UTILS METHODS
def json_failed_message(text):
   return flask.jsonify({
      "message": text + " failed"
   })

def json_success_message(text):
   return flask.jsonify({
      "message": text + " successfully"
   })

## FLASK UTILS METHODS

def get_form_values(values_names):
   if flask.request.method != 'POST':
      return None
   values = {}
   for value_name in values_names:
      values[value_name] = flask.request.values.get(value_name)
   return values

def get_json_values(values_names):
   if flask.request.method != 'POST':
      return None
   values = {}
   for value_name in values_names:
      values[value_name] = flask.request.json[value_name]
   return values

def get_json_array_values(values_names):
   if flask.request.method != 'POST':
      return None
   players = []
   for json_player in flask.request.json:
      player = {}
      for value_name in values_names:
         player[value_name] = json_player[value_name]
      players.append(player)
   return players

## DATABASE UTILS METHODS

def commit_request(request, values):
   connection = sqlite3.connect('../resources/SQLITE/rpg_game.db')
   cursor = connection.cursor()
   cursor.execute(request, values)
   selecteds = cursor.fetchall()
   connection.commit()
   connection.close()

   return selecteds

def select_request(request):
   connection = sqlite3.connect('../resources/SQLITE/rpg_game.db')
   cursor = connection.cursor()
   cursor.execute("select" + request)
   selecteds = cursor.fetchall()
   connection.close()

   return selecteds

def get_players_list():
   return make_players_list(select_request("* FROM players"))

def get_player(player_id):
   return make_players_list(select_request("* FROM players WHERE player_id = " + player_id))

def insert_players(players):
   if players == None:
      return False

   for player in players:
      insert_player(player)

   return True

def insert_player(player):
   if player == None:
      return False

   if not "zone_active" in player:
      player["zone_active"]        = 1 ## Make zone active text box in form
   commit_request("""
                     INSERT INTO players( player_name, player_zone_active, player_attack, player_attack_speed, player_defense, player_life,  player_regeneration_speed,  player_level)
                                 VALUES (:name,       :zone_active,       :attack,       :attack_speed,       :defense,              :life, :regeneration_speed,        :level)
                     """, player)
   return True

def make_players_list(players):
   players_list = []
   for player in players:
      if player == None:
         continue

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
   return players_list

def get_areas_and_path_list():
   connection = sqlite3.connect('../resources/SQLITE/rpg_game.db')
   cursor = connection.cursor()
   cursor.execute('SELECT * FROM areas')
   areas = cursor.fetchall()

   areas_list = []

   for area in areas:
      cursor.execute("SELECT areas_paths.area_source_id, areas_paths.area_destination_id FROM areas_paths WHERE areas_paths.area_source_id = " + str(area[0]))
      areas_source_paths = cursor.fetchget_playerall()
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

   return areas_list
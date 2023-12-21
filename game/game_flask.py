import flask
import sqlite3

app = flask.Flask(__name__, template_folder="views")

## HOME

@app.route('/')
def home():
   return get_players()

## Function AND API REQUESTS Management

## AUTO FORM
@app.route('/autoshow/<table_name>')
def autoform(table_name):
   columns = get_request("PRAGMA table_info(" + table_name + ")")
   if columns == None:
      return home()

   columns_list = []
   for column in columns:
      column_info = {}
      column_info["column_name"]      = column[1]
      column_info["column_show_name"] = str(column[1]).replace(table_name[0:len(table_name) - 1] + "_", "").replace("_", " ").capitalize()
      column_info["column_type"]      = column[2]
      columns_list.append(column_info)
   selecteds_lines = select_request("* FROM " + table_name)

   lines_list = []
   for selected_line in selecteds_lines:
      line = []
      for value in selected_line:
         line.append(value)
      lines_list.append(line)

   return flask.render_template('autoshow.html', columns_list=columns_list, lines_list=lines_list)

## PLAYERS
@app.route('/players')
def get_players():
   return flask.render_template('index.html', players_stats_list=get_players_list())

@app.route('/player/<player_id>')
def get_player(player_id):
   return flask.render_template('index.html', players_stats_list=get_player(player_id))

@app.route('/player/add', methods=['GET', 'POST'])
def add_player():
   player = get_form_values(["name", "zone_active", "attack", "attack_speed", "defense", "life", "regeneration_speed", "level"])
   if player == None:
      return flask.render_template('player_add.html')

   insert_player(player)

   return flask.redirect('/')

@app.route('/delete/player/<player_id>')
def delete_player(player_id):
   db_delete_player(player_id)

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

@app.route('/api/delete/player', methods=['POST'])
def api_delete_player():
   return json_success_message("Player deleted") if delete_player(get_json_value("player_id")) else json_failed_message("Player deletion")

@app.route('/api/delete/players', methods=['POST'])
def api_delete_players():
   return json_success_message("Players deleted") if db_delete_players(get_json_array_value( ["player_id"])) else json_failed_message("Players deletion")

## AREAS
@app.route('/areas')
def areas():
   return flask.render_template('areas.html', areas_list=get_areas_and_path_list())

@app.route('/api/areas', methods=['GET'])
def get_areas():
   return flask.jsonify(get_areas_and_path_list())

## JSON UTILS METHODS
def json_message(text):
   return flask.jsonify({
      "message": text
   })

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

def get_json_value(value_name):
   if flask.request.method != 'POST':
      return None

   return flask.request.json[value_name]

def get_json_array_value(values_names):
   if flask.request.method != 'POST':
      return None

   values = []
   for json_value in flask.request.json:
      for value_name in values_names:
         values.append(json_value[value_name])

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

   values = []
   for json_value in flask.request.json:
      value = {}
      for value_name in values_names:
         value[value_name] = json_value[value_name]
      values.append(value)

   return values

## DATABASE UTILS METHODS

def commit_request(request, values=None):
   connection = sqlite3.connect('../resources/SQLITE/rpg_game.db')
   cursor = connection.cursor()
   if values == None:
      cursor.execute(request)
   else:
      cursor.execute(request, values)
   selecteds = cursor.fetchall()
   connection.commit()
   connection.close()

   return selecteds

def get_request(request):
   print("get request : " + request)
   connection = sqlite3.connect('../resources/SQLITE/rpg_game.db')
   cursor = connection.cursor()
   cursor.execute(request)
   selecteds = cursor.fetchall()
   connection.close()

   return selecteds

def select_request(request):
   return get_request("SELECT " + request)

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

   if player["zone_active"] == None:
      player["zone_active"]        = 1 ## Make zone active text box in form
   commit_request("""
                     INSERT INTO players( player_name, player_zone_active, player_attack, player_attack_speed, player_defense, player_life,  player_regeneration_speed,  player_level)
                                 VALUES (:name,       :zone_active,       :attack,       :attack_speed,       :defense,              :life, :regeneration_speed,        :level)
                     """, player)
   return True

def db_delete_player(player_id):
   if player_id == None:
      return False

   commit_request("DELETE FROM players WHERE player_id = " + str(player_id))

   return True

def db_delete_players(players_id):
   if players_id == None:
      return False

   for player_id in players_id:
      delete_player(player_id)

   return True

def make_players_list(players):
   players_list = []
   for player in players:
      if player == None:
         continue

      players_list.append({
         "player_id":                   player[0],
         "player_name":                 player[1],
         "player_zone_active":          player[2],
         "player_attack":               player[3],
         "player_attack_speed":         player[4],
         "player_defense":              player[5],
         "player_life":                 player[6],
         "player_regeneration_speed":   player[7],
         "player_level":                player[8]
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

   return areas_list
from flask import Flask, jsonify, request, send_from_directory
from game import SimpleBig2, Player, Deck, Card
import time

app = Flask(__name__, static_folder='static')

# Create the initial game state
players = [Player("Adam"), Player("Ben"), Player("Charlie"), Player("Derek")]
game = SimpleBig2(players)
game.setup()

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# @app.route("/start", methods=["POST"])
# def start_game():
#     """Start a new game, reset everything."""
#     global game, players
#     game.reset()
#     return jsonify({"message": "New game started", "players": [player.name for player in players]})

@app.route("/game-state", methods=["GET"])
def get_game_state():
    """Retrieve the current state of the game."""
    state = {
        "players": [
            {
                "name": player.name,
                "cards": [str(card) for card in player.deck.cards] if player.deck else [],
                "has_card": player.has_card()
            }
            for player in game.players
        ],
        "last_played_card": str(game.last_played_card) if game.last_played_card else None,
        "last_played_player": game.last_played_player.name if game.last_played_player else None
    }
    return jsonify(state)

@app.route("/play", methods=["POST"])
def play_card():
    """Play a card for a given player."""
    data = request.json
    player_name = data.get("player_name")
    card_str = data.get("card")

    player = next((p for p in game.players if p.name == player_name), None)
    if not player:
        return jsonify({"error": "Player not found"}), 404

    # Parse card string to Card object
    try:
        rank, suit = card_str[:-1], card_str[-1]
        card = Card(rank, suit)
    except Exception as e:
        return jsonify({"error": "Invalid card format"}), 400

    # Play the card if possible
    try:
        played_card = player.play(game.last_played_card)
        if played_card:
            game.last_played_card = played_card
            game.last_played_player = player
            return jsonify({"message": f"{player.name} played {played_card}"})
        else:
            return jsonify({"message": f"{player.name} passed this turn"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    
@app.route('/start_game', methods=['POST'])
def start_game():
    # Call the next_turn function of the SimpleBig2 class
    game.start()  # Add logic to handle turns
    return jsonify(game.get_game_state())  # Adjust this to return the necessary state

@app.route('/reset', methods=['POST'])
def reset_game():
    game.reset()
    return jsonify(game.get_game_state())  # Adjust this to return the necessary state


if __name__ == "__main__":
    app.run(debug=True)

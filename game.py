"""
Inspired by https://realpython.com/python-data-classes/
"""

from dataclasses import dataclass, field
import random
from typing import Self

type Rank = str
type Suit = str

RANKS = "3 4 5 6 7 8 9 10 J Q K A 2".split()
SUITS = "♢ ♣ ♡ ♠".split()


@dataclass(order=True)
class Card:
    # Note that .sort_index is added as the first field of the class. That way, the comparison is first done using .sort_index and only if there are ties are the other fields used.
    # .sort_index should not be included as a parameter in the .__init__() method (because it is calculated from the .rank and .suit fields)
    # remove .sort_index from the repr of the class to avoid confusing the user about this implementation detail
    sort_index: int = field(init=False, repr=False)
    rank: Rank
    suit: Suit

    def __post_init__(self):
        self.sort_index = RANKS.index(self.rank) * len(SUITS) + SUITS.index(self.suit)

    def __str__(self):
        return f"{self.rank}{self.suit}"


class Deck:
    def __init__(self, cards: list[Card] | None = None):
        self.cards: list[Card] = (
            [Card(r, s) for r in RANKS for s in SUITS] if cards is None else cards
        )

    def __repr__(self):
        return repr(self.cards)

    def __len__(self):
        return len(self.cards)

    def shuffle(self) -> Self:
        random.shuffle(self.cards)
        return self

    def order(self) -> Self:
        self.cards.sort()
        return self

    def draw(self, number: int = 1) -> list[Card]:
        """
        Draw the first n number of card from the deck.
        """
        if number > len(self.cards):
            raise ValueError(f"Cannot draw more cards than are in the deck, {number=}, {len(self.cards)=}")
        drawn_cards = self.cards[:number]
        self.cards = self.cards[number:]
        return drawn_cards

    def get_smallest_card(self, card_index: int = 0) -> Card | None:
        """
        Find the smallest card with a sort_index greater than card_index.
        Default card_index is 0, so the smallest card would be the smallest in the deck.
        """
        for card in sorted(self.cards, key=lambda c: c.sort_index):
            if card.sort_index > card_index:
                return card
        return None
    
    def play(self, card: Card) -> Card:
        if card not in self.cards:
            raise ValueError(f'{card=} not found in the deck.')
        self.cards.remove(card)
        return card

    @property
    def count(self) -> int:
        return len(self.cards)

    @staticmethod
    def make_french_deck() -> "Deck":
        return Deck([Card(r, s) for s in SUITS for r in RANKS])


class Player:
    def __init__(self, name: str):
        self.name = name
        self.deck: Deck | None= None

    def __repr__(self) -> str:
        return self.name

    def dealt(self, deck: Deck) -> None:
        self.deck = deck

    def play(self, last_played_card: Card | None) -> Card | None:
        if self.deck is None:
            raise ValueError("Player's deck should not be empty")
        card_index = 0 if last_played_card is None else last_played_card.sort_index
        smallest_playable_card = self.deck.get_smallest_card(card_index)
        if smallest_playable_card is None:
            print(f'{self.name} pass this turn')
            return None
        return self.deck.play(smallest_playable_card)
    
    def has_card(self) -> bool:
        return len(self.deck) > 0 if self.deck is not None else False
    
    def discard_all_cards(self) -> None:
        self.deck = None


class SimpleBig2:
    """
    A simple Big2 that each player only draw 1 card
    """

    MAX_CARDS_PER_PLAYER = 12

    def __init__(self, players: list[Player]):
        self.poker: Deck = Deck()
        self.players = players
        self.last_played_card: Card | None = None
        self.last_played_player: Player | None = None

    def deal_cards(self) -> Self:
        for player in self.players:
            assigned_deck = Deck(self.poker.draw(self.MAX_CARDS_PER_PLAYER)).order()
            player.dealt(assigned_deck)
            print(f"initial deck: {player.name=}: {player.deck=}")
        assert len(self.poker) == 52 - len(self.players) * self.MAX_CARDS_PER_PLAYER

    def determine_starting_player(self) -> Player:
        """
        Determine the player who should start based on the smallest card.
        The player with the smallest card (by sort_index) starts the game.
        """
        starting_player = None
        smallest_card = None

        for player in self.players:
            # Assuming each player has a 'hand' attribute which is a Deck of cards
            player_smallest_card = player.deck.get_smallest_card()
            # Compare to find the absolute smallest card across all players
            if smallest_card is None or player_smallest_card < smallest_card:
                smallest_card = player_smallest_card
                starting_player = player
        return starting_player

    def rotate_players(self, starting_player: Player) -> None:
        """
        Rotate the order of players so that it starts from the given starting player.
        """
        starting_index = self.players.index(starting_player)
        # Rotate the players list to start from the starting_index
        self.players = self.players[starting_index:] + self.players[:starting_index]
        print(self.players)

    def setup(self) -> Self:
        self.poker.shuffle()
        self.deal_cards()
        starting_player = self.determine_starting_player()
        self.rotate_players(starting_player=starting_player)
        return self
    
    def reset(self) -> Self:
        self.poker = Deck()
        self.last_played_card = None
        self.last_played_player = None
        for player in self.players:
            player.discard_all_cards()
        return self.setup()
    
    def reset_last_played_card_if_all_players_passed(self, player: Player) -> None:
        if player == self.last_played_player:
            self.last_played_card = None

    def next_turn(self, player: Player) -> None:
        self.reset_last_played_card_if_all_players_passed(player)
        played_card = player.play(self.last_played_card)
        if played_card is not None:
            self.last_played_card = played_card
            self.last_played_player = player
            print(f"{player.name} played {played_card}")

    def start(self) -> None:
        """
        Main game logic for playing a round of SimpleBig2.
        Each player draws the smallest card that is larger than the last played card.
        If last_played_player is the current player, they play their smallest card.
        If no player can play, reset to allow smallest cards again.
        """
        while all(
            player.has_card() for player in self.players
        ):  # Continue while players have cards
            for player in self.players:
                self.next_turn(player)
        winner = [player for player in self.players if not player.has_card()][0]
        print(f"Game over! The winner is {winner.name}")


if __name__ == "__main__":
    players = [Player("Adam"), Player("Ben"), Player("Charlie"), Player("Derek")]
    game = SimpleBig2(players)
    game.setup().start()

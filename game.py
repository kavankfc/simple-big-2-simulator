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
        return f"{self.suit}{self.rank}"


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
        if number > len(self.cards):
            raise ValueError("Cannot draw more cards than are in the deck.")
        drawn_cards = self.cards[:number]
        self.cards = self.cards[number:]
        return drawn_cards

    def draw_smallest(self, card_index: int) -> Card | None:
        # Find the smallest card with a sort_index greater than card_index
        for card in sorted(self.cards, key=lambda c: c.sort_index):
            if card.sort_index > card_index:
                self.cards.remove(card)
                return card
        return None

    @staticmethod
    def make_french_deck() -> Self:
        return Deck([Card(r, s) for s in SUITS for r in RANKS])


class Player:
    def __init__(self, name: str):
        self.name = name
        self.deck = None

    def __repr__(self) -> str:
        return self.name

    def dealt(self, deck: Deck):
        self.deck = deck

    def play(self, last_played_card: Card | None) -> Card | None:
        if self.deck is None:
            raise ValueError("Player's deck should not be empty")
        return self.deck.draw_smallest(last_played_card.sort_index)

    def has_card(self) -> bool:
        if self.deck is None:
            return False
        return len(self.deck) > 0


class SimpleBig2:
    """
    A simple Big2 that each player only draw 1 card
    """

    MAX_CARDS_PER_PLAYER = 12

    def __init__(self, players: list[Player]):
        self.poker: Deck = Deck()
        self.last_played_card: Card | None = None
        self.players = players
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
            player_smallest_card = min(
                player.deck.cards, key=lambda card: card.sort_index
            )

            # Compare to find the absolute smallest card across all players
            if (
                smallest_card is None
                or player_smallest_card.sort_index < smallest_card.sort_index
            ):
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

    def play(self) -> None:
        """
        Main game logic for playing a round of SimpleBig2.
        Each player draws the smallest card that is larger than the last played card.
        If last_played_player is the current player, they play their smallest card.
        If no player can play, reset to allow smallest cards again.
        """
        while all(
            player.has_card() for player in self.players
        ):  # Continue while players have cards
            played_this_round = False

            for player in self.players:
                # Determine the card to play
                if player == self.last_played_player:
                    # If the current player was the last to play, they play their smallest card
                    card_to_play = player.deck.draw_smallest(-1)
                else:
                    # Otherwise, they play the smallest card larger than last played card
                    card_to_play = (
                        player.deck.draw_smallest(self.last_played_card.sort_index)
                        if self.last_played_card
                        else player.deck.draw_smallest(-1)
                    )

                if card_to_play:
                    self.last_played_card = card_to_play
                    self.last_played_player = player
                    print(f"{player} played {card_to_play}")
                    played_this_round = True
                else:
                    print(f"{player} cannot play a card this round.")

            # Check if no player could play a card this round
            if not played_this_round:
                print(
                    "No player could play a card this round. Resetting last played card."
                )
                self.last_played_card = None
                self.last_played_player = None

        winner = [player for player in self.players if not player.has_card()][0]

        print(f"Game over! The winner is {winner.name}")


if __name__ == "__main__":
    players = [Player("Adam"), Player("Ben"), Player("Charlie"), Player("Derek")]
    game = SimpleBig2(players)
    game.setup()
    game.play()

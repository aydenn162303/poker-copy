"""
Random Bot - Makes random legal decisions
This is a simple example bot for testing the tournament system
"""
from typing import List, Dict, Any

import random
from bot_api import PokerBotAPI, PlayerAction, GameInfoAPI
from engine.cards import Card, Rank
from engine.poker_game import GameState



class ayden_random_but_not_random(PokerBotAPI):
    """
    A simple bot that makes random legal decisions.
    Useful for testing the tournament system.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.hands_played = 0
        
        self.dont_play = [
            (Rank.ACE, Rank.TWO), (Rank.TWO, Rank.TWO), (Rank.THREE, Rank.TWO),
            (Rank.THREE, Rank.THREE), (Rank.FOUR, Rank.THREE), (Rank.FOUR, Rank.FOUR), (Rank.FIVE, Rank.FOUR),
            (Rank.FIVE, Rank.FIVE), (Rank.FIVE, Rank.SIX), (Rank.SIX, Rank.SIX), (Rank.SEVEN, Rank.SIX),
            (Rank.SIX, Rank.SIX), (Rank.SIX, Rank.SEVEN), (Rank.SEVEN, Rank.SEVEN), (Rank.EIGHT, Rank.SEVEN),
            (Rank.EIGHT, Rank.EIGHT), (Rank.EIGHT, Rank.NINE)
        ]

        self.play_if_suited = [
            (Rank.ACE, Rank.ACE), (Rank.KING, Rank.ACE), (Rank.KING, Rank.KING), (Rank.KING, Rank.QUEEN)
        ]
    
        self.allin = [
            (Rank.ACE, Rank.ACE)
        ]
        
    
    def get_action(self, game_state: GameState, hole_cards: List[Card], 
                   legal_actions: List[PlayerAction], min_bet: int, max_bet: int) -> tuple:
        """Make a random legal action"""

        action = PlayerAction.FOLD

        card1, card2 = hole_cards
        
        # Check if we have a premium hand
        hand_tuple1 = (card1.rank, card2.rank)
        hand_tuple2 = (card2.rank, card1.rank)  # Check both orders
        
        no_play = (hand_tuple1 in self.dont_play or 
                     hand_tuple2 in self.dont_play)
        
        is_suited = (hand_tuple1 in self.play_if_suited or
                     hand_tuple2 in self.play_if_suited)
        
        allin = (hand_tuple1 in self.allin or
                     hand_tuple2 in self.allin)

        if(allin):
            if (PlayerAction.ALL_IN in legal_actions):
                return PlayerAction.ALL_IN, 0
            
        if (is_suited):
            if (PlayerAction.RAISE in legal_actions):
                action = PlayerAction.RAISE

        if(no_play):
            if (PlayerAction.FOLD in legal_actions):
                return PlayerAction.FOLD, 0
        
        # Choose a random legal action
        if not is_suited:
            action = random.choice(legal_actions)

        # If raising, choose a random valid amount
        if action == PlayerAction.RAISE:
            # More realistic random raise - between min raise and pot size
            max_raise = min(game_state.pot * 1.5, max_bet) # Raise up to 1.5x pot
            if max_raise < min_bet:
                max_raise = min_bet
                
            amount = random.randint(min_bet, int(max_raise))
            return action, amount
        
        # All other actions don't need an amount

        return action, 0
    
    def hand_complete(self, game_state: GameState, hand_result: Dict[str, Any]):
        """Track hands played"""
        self.hands_played += 1
        
        if self.hands_played > 0 and self.hands_played % 50 == 0:
            self.logger.info(f"Played {self.hands_played} hands randomly")
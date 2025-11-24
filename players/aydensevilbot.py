"""
Copy of random bot but I changed a lot

"""
from typing import List, Dict, Any
import random

from bot_api import PokerBotAPI, PlayerAction, GameInfoAPI
from engine.cards import Card, Rank, HandEvaluator
from engine.poker_game import GameState


class aydenbot(PokerBotAPI):
    """
    A simple bot that makes random legal decisions.
    Useful for testing the tournament system.
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.hands_played = 0
        self.play_frequency = 0.8

        self.premium_hands = [
            (Rank.ACE, Rank.ACE), (Rank.KING, Rank.KING), (Rank.QUEEN, Rank.QUEEN),
            (Rank.JACK, Rank.JACK), (Rank.TEN, Rank.TEN),
            (Rank.ACE, Rank.KING), (Rank.ACE, Rank.QUEEN), (Rank.ACE, Rank.JACK),
            (Rank.KING, Rank.QUEEN)
        ]
        self.good_suited_connectors = [
            (Rank.KING, Rank.JACK), (Rank.QUEEN, Rank.JACK), (Rank.JACK, Rank.TEN),
            (Rank.TEN, Rank.NINE), (Rank.NINE, Rank.EIGHT)
        ]
    

    def get_action(self, game_state: GameState, hole_cards: List[Card], 
                   legal_actions: List[PlayerAction], min_bet: int, max_bet: int) -> tuple:
        
        if game_state.round_name == "preflop":
            return self._preflop_strategy(game_state, hole_cards, legal_actions, min_bet, max_bet)
        else:
            return self._postflop_strategy(game_state, hole_cards, legal_actions, min_bet, max_bet)



    def _preflop_strategy(self, game_state: GameState, hole_cards: List[Card], legal_actions: List[PlayerAction], 
                            min_bet: int, max_bet: int) -> tuple:
            """Strategy for pre-flop betting"""
            if len(hole_cards) != 2:
                return PlayerAction.FOLD, 0
            
            card1, card2 = hole_cards
            hand_tuple1 = (card1.rank, card2.rank)
            hand_tuple2 = (card2.rank, card1.rank)
            
            is_premium = (hand_tuple1 in self.premium_hands or hand_tuple2 in self.premium_hands)
            is_suited_connector = (card1.suit == card2.suit and 
                                (hand_tuple1 in self.good_suited_connectors or 
                                hand_tuple2 in self.good_suited_connectors))
            is_pocket_pair = card1.rank == card2.rank

            if not (is_premium or is_suited_connector or is_pocket_pair):
                if PlayerAction.CHECK in legal_actions:
                    return PlayerAction.CHECK, 0
                return PlayerAction.FOLD, 0
                
            # With a good hand, either raise or call
            if PlayerAction.RAISE in legal_actions:
                # Raise 3x the big blind
                raise_amount = min(3 * game_state.big_blind, max_bet)
                raise_amount = max(raise_amount, min_bet)
                return PlayerAction.RAISE, raise_amount
            
            if PlayerAction.CALL in legal_actions:
                return PlayerAction.CALL, 0
                
            return PlayerAction.CHECK, 0



    def _postflop_strategy(self, game_state: GameState, hole_cards: List[Card], 
                           legal_actions: List[PlayerAction], min_bet: int, max_bet: int) -> tuple:
                
        all_cards = hole_cards + game_state.community_cards
        hand_type, _, _ = HandEvaluator.evaluate_best_hand(all_cards)
        hand_rank = HandEvaluator.HAND_RANKINGS[hand_type]

        # Choose a random legal action
        if hand_rank >= HandEvaluator.HAND_RANKINGS['two_pair']:
            if PlayerAction.RAISE in legal_actions:
                action = PlayerAction.RAISE
            elif PlayerAction.CALL in legal_actions:
                action = PlayerAction.CALL
            elif PlayerAction.CHECK in legal_actions:
                action = PlayerAction.CHECK
            else:
                action = random.choice(legal_actions)
        else:
            action = random.choice(legal_actions)


        # If raising, choose a random valid amount
        if action == PlayerAction.RAISE:
            # More realistic random raise - between min raise and pot size
            max_raise = min(game_state.pot * 1.25, max_bet) # Raise up to 1.5x pot
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
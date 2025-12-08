"""
plays only good hands
"""
from typing import List, Dict, Any

from bot_api import PokerBotAPI, PlayerAction, GameInfoAPI
from engine.cards import Card, Rank, HandEvaluator
from engine.poker_game import GameState



class aydenbutbetter(PokerBotAPI):
    """
    ALL IN
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.hands_played = 0
        self.hands_won = 0
        
        # Define strong starting hands
        self.premium_hands = [
            (Rank.ACE, Rank.ACE), (Rank.KING, Rank.KING), (Rank.QUEEN, Rank.QUEEN),
        ]

        self.maybestayingame_hands = [ # do later around line 62-66
            (Rank.JACK, Rank.JACK), (Rank.ACE, Rank.KING)
        ]
        
    
    def get_action(self, game_state: GameState, hole_cards: List[Card], 
                   legal_actions: List[PlayerAction], min_bet: int, max_bet: int) -> tuple:
        """Play very conservatively - only strong hands"""

        if len(hole_cards) != 2:
            return PlayerAction.FOLD, 0
        
        card1, card2 = hole_cards
        
        # Check if we have a premium hand
        hand_tuple1 = (card1.rank, card2.rank)
        hand_tuple2 = (card2.rank, card1.rank)  # Check both orders
        
        is_premium = (hand_tuple1 in self.premium_hands or 
                     hand_tuple2 in self.premium_hands)
               
        is_same_suit = (card1.suit == card2.suit)
        #if is_same_suit == True: print("same suit, SWEET!")

    #    if "random_bot" in game_state.active_players and len(game_state.active_players) == 2:
    #       return PlayerAction.ALL_IN, 0
    # hopefully i can push this

        if PlayerAction.ALL_IN in legal_actions and is_premium:
            return PlayerAction.ALL_IN, 0
        elif is_same_suit and game_state.round_name == "preflop":     #if preflop basically
            if PlayerAction.CHECK in legal_actions:
                return PlayerAction.CHECK, 0
            if PlayerAction.RAISE in legal_actions: 
                return PlayerAction.RAISE, game_state.pot // 3 #CHANGE AND SEE WHAT CHANGING DOES
        else:
            #todo for later: something that checks if the bet is being raised a lot and if it isn't it might stay in game
            if PlayerAction.FOLD in legal_actions:
                return PlayerAction.FOLD, 0
 
        
        # Check for high pocket pairs
        is_high_pocket_pair = (card1.rank == card2.rank and 
                              card1.rank.value >= 9)  # 9s or better
        
        #custom thingy but not really because i think i deleted it earlier
 
        
        # Only play premium hands or high pocket pairs
        if not (is_premium or is_high_pocket_pair or is_same_suit):
            return PlayerAction.FOLD, 0
        
        # We have a good hand - decide what to do
        # Prioritize actions: RAISE, then CALL, then CHECK, otherwise FOLD

        if PlayerAction.RAISE in legal_actions:
            # Conservative raise - don't go too big
            current_pot = game_state.pot
            # Ensure raise amount is at least min_bet and within max_bet
            # Attempt to raise by a third of the pot, but adjust if it's too small or too large
            raise_amount = game_state.pot // 2
            
            # Ensure raise amount is actually greater than current_bet if raising
            if raise_amount > game_state.current_bet:
                return PlayerAction.RAISE, raise_amount
            elif PlayerAction.CALL in legal_actions:
                return PlayerAction.CALL, 0
            elif PlayerAction.CHECK in legal_actions:
                return PlayerAction.CHECK, 0
        
        if PlayerAction.CALL in legal_actions:
            return PlayerAction.CALL, 0
        
        if PlayerAction.CHECK in legal_actions:
            return PlayerAction.CHECK, 0
        
        if PlayerAction.ALL_IN in legal_actions:
            return PlayerAction.ALL_IN, 0
        
        # If no other legal action, fold as fallback (should be handled by game engine anyway)
        return PlayerAction.FOLD, 0
    
    def hand_complete(self, game_state: GameState, hand_result: Dict[str, Any]):
        """Track hands played"""
        self.hands_played += 1
        
        if self.hands_played > 0 and self.hands_played % 50 == 0:
            self.logger.info(f"Played {self.hands_played} hands randomly")
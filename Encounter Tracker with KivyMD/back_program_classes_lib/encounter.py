import copy

class Encounter:
    
    def __init__(self, name) -> None:
        
        self.name = name
        self.started = False
        
        self.added_monsters_list = [] #This list contains items in shape of "[Monster(), amount: int]". 
        #We use this with encounter making screens monster items. We save their info in this list. "amount" default = 0
        self.monsters = []
        self.players = []
        self.initiative_order = []
        self.current_index = 0
        self.round = 1

    def __str__(self) -> str:
        return self.name

    
    def add_creature(self, creature):
        """Adds creature to this encounter"""
        
        self.initiative_order.append(creature)
    
    def remove_creature(self, creature):
        """Removes creature from this encounter"""
        
        self.initiative_order.remove(creature)

    def clone_creatures(self, players):
        """Clones players and appends to self.players.
        Clones self.added_monsters_list monsters up to stated amounts that in same lists index 1 and appends self.player"""

        for player in players:
            player_clone = copy.copy(player)  
            self.players.append(player_clone)
        
        for monsters_with_amount in self.added_monsters_list:
            for i in range(monsters_with_amount[1]):
                monster_clone = copy.copy(monsters_with_amount[0])
                monster_clone.name = f"#{i + 1} {monster_clone.name}"
                self.monsters.append(monster_clone)

    def sort_creatures(self):
        """set creatures initiave_order and sorts them by their initiatives."""
        
        self.__roll_monsters_initiatives__()
        self.initiative_order.extend(self.players)
        self.initiative_order.extend(self.monsters)
        self.initiative_order.sort(reverse = True, key = lambda creature: creature.initiative)
        
    def __roll_monsters_initiatives__(self):
        """Rolls initiatives for monsters."""

        for m in self.monsters:
            m.roll_initiative()

    def print_initiative_order(self):
        
        for creature in self.initiative_order:
            print(creature)

    def print_added_monsters(self):
        
        for i in self.added_monsters_list:
            print("name:",i[0],"amount:",i[1])

    
            
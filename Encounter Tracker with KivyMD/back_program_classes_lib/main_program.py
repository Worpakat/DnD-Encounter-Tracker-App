from creature_classes import Creature, Player, Monster
from encounter import Encounter

player1 = Player("Dieter", 10, 14, 13)
player2 = Player("Nelo", 10, 14, 13)
player3 = Player("Soox", 10, 14, 13)
player4 = Player("Alastair", 10, 14, 13)

wolf1 = Monster("wolf1", 21, 12, 16, -4)
wolf2 = Monster("wolf2", 21, 12, 16, +4)
wolf3 = Monster("wolf3", 21, 12, 16, +4)

player1.initiative = 12
# player2.initiative = 11
player3.initiative = 15
player4.initiative = 1

# wolf1.roll_initiative()
wolf2.roll_initiative()
wolf3.roll_initiative()

encounter1 = Encounter("kurt encounter")
encounter1.players.append(player1)
encounter1.players.append(player2)
encounter1.players.append(player3)
encounter1.players.append(player4)
encounter1.monsters.append(wolf1)
encounter1.monsters.append(wolf2)
encounter1.monsters.append(wolf3)

encounter1.sort_creatures()
# encounter1.print_initiative_order

print(encounter1.__dict__)


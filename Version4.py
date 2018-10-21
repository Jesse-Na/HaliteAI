#!/usr/bin/env python3

# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import constants

import random
import logging


# This game object contains the initial game state.
game = hlt.Game()
# Respond with your name.
game.ready("SodiumMachine")
number_of_ships = 0
number_of_dropoffs = 0
ship_status = {}

while True:
    # Get the latest game state.
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map
    
    dropoff_points = me.get_dropoffs()

    # A command queue holds all the commands you will run this turn.
    command_queue = []

    for ship in me.get_ships():
        game_map[ship.position].mark_unsafe(ship)
    
        if ship.id not in ship_status:
            ship_status[ship.id] = "exploring"
        
        if ship_status[ship.id] == "returning":
            if ship.position == me.shipyard.position:
                ship_status[ship.id] = "exploring"
            #elif number_of_dropoffs < 1 and game_map.calculate_distance(ship, me.shipyard.position) >= 5 and me.halite_amount >= 10000 and not game_map[ship.position].has_structure:
             #   command_queue.append(ship.make_dropoff())
              #  number_of_ships -= 1
            else:
                return_position = me.shipyard.position
                for dropoff in dropoff_points:
                    if game_map.calculate_distance(ship, dropoff.position) < game_map.calculate_distance(ship, me.shipyard.position):
                        return_position = dropoff.position
                move = game_map.naive_navigate(ship, return_position)   
                if not move == "still":
                    command_queue.append(ship.move(move))
                elif number_of_dropoffs < 1 and me.halite_amount >= constants.SHIP_COST * 2 and not game_map[ship.position].is_occupied:
                    command_queue.append(ship.make_dropoff())
                    number_of_ships -= 1
                    number_of_dropoffs += 1
                else:
                    command_queue.append(ship.move(random.choice(["w", "n"])))
                continue

        elif ship.is_full:
            ship_status[ship.id] = "returning"

        
        if ship_status[ship.id] == "exploring":
            target_space = ship.position
            surrounding_positions = ship.position.get_surrounding_cardinals()
            for space in range(len(surrounding_positions)):
                if game_map[surrounding_positions[space]].halite_amount > game_map[target_space].halite_amount:
                    target_space = surrounding_positions[space]
            if game_map[ship.position].halite_amount < constants.MAX_HALITE / 10 or ship.is_full:
                command_queue.append(ship.move(game_map.naive_navigate(ship, target_space)))
        
        logging.info("Ship {} has {} halite. Its targets space is {}. Its status is {}".format(ship.id,ship.halite_amount,target_space, ship_status[ship.id]))        
        logging.info(me.shipyard.position)
            

    # If you're on the first turn and have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though.
    if number_of_ships < 6 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        number_of_ships += 1
        command_queue.append(game.me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

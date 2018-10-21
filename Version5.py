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
        target_space = ship.position
        surrounding_positions = ship.position.get_surrounding_cardinals()
    
        if ship.id not in ship_status:
            ship_status[ship.id] = "exploring"
        
        if ship_status[ship.id] == "returning":
            if ship.position == me.shipyard.position:
                ship_status[ship.id] = "exploring"
            else:
                target_space = me.shipyard.position
                move = game_map.naive_navigate(ship, target_space) 
                command_queue.append(ship.move(move))

        elif ship.is_full:
            ship_status[ship.id] = "returning"

        
        if ship_status[ship.id] == "exploring":
            for space in range(len(surrounding_positions)):
                if game_map[surrounding_positions[space]].halite_amount > game_map[target_space].halite_amount and not game_map[surrounding_positions[space]].is_occupied:
                    target_space = surrounding_positions[space]
            if game_map[ship.position].halite_amount < constants.MAX_HALITE / 10 or ship.is_full:
                move = game_map.naive_navigate(ship, target_space)
                command_queue.append(ship.move(move))

        
        logging.info("Ship {} has {} halite and is {}".format(ship.id,ship.halite_amount,ship_status[ship.id]))
        logging.info(move)
            

    # If you're on the first turn and have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though.
    if game.turn_number <= constants.MAX_TURNS / 4 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(game.me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

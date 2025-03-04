from app import app, db, Event  # Make sure Event is imported from your models

with app.app_context():
    # Create the events – no need to set id manually if auto-increment is enabled
    events = [
        Event(
            event_name="ROBO WARS",
            description="Imagine the adrenaline rush of fighting in a tug of war. Exciting isn't it? Now think what it would be like if robots played the sport. Tug of War is for the strongest among the strong. Start building your Tug of War robot now",
            event_date="2025-03-04"
        ),
        Event(
            event_name="ROBO ROVER",
            description="Bots on wheels, exploring surreal landscapes of innovation. Roving into the future with gears and circuits. Dare to rove where no bot has roved before. Fasten your seatbelts; the robo rover ride is about to begin!",
            event_date="2025-03-04"
        ),
        Event(
            event_name="LINE FOLLOWER",
            description="Finish the line to shine. Create your bot and let it follow a black line on a white surface. Only the smartest can survive the complex tracks filled with crazy twists and turns. Can your bot navigate the challenges and claim victory?",
            event_date="2025-03-04"
        ),
        Event(
            event_name="DRONE RACING",
            description="Zooming through the skies, chasing the thrill of victory. Drones in flight, competing for the title of the fastest in the air. The race is on, and the drones are ready to defy gravity!",
            event_date="2025-03-04"
        ),
        Event(
            event_name="ROBO SOCCER",
            description="Feel like Messi? Build a bot and play soccer. Not just handling the ball, but tackle the opponent's bot and score a goal. 'To become successful set your goals' at the goal post!",
            event_date="2025-03-04"
        ),
        Event(
            event_name="ROBO SUMO",
            description="Welcome to the robo sumo battlefield! Bots in the ring, gears engaged – it's time for the ultimate robo sumo showdown! Enter the arena where only the strongest robo bots survive!",
            event_date="2025-03-04"
        ),
        Event(
            event_name="MAZE SOLVER",
            description="An autonomous robot has to complete a tricky maze in the shortest possible time. The quickest one to finish the maze wins!",
            event_date="2025-03-04"
        )
    ]
    
    for event in events:
        db.session.add(event)
    
    db.session.commit()
    print("Event data inserted successfully!")

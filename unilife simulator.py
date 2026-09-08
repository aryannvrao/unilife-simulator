import os
import random
import time

# ==============================================================================
# SECTION: DISPLAY AND ANIMATION FUNCTIONS
# ==============================================================================
def center_screen_clear(lines=6):
    """Clears the terminal/console and prints a number of blank lines."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" * lines)

def center_screen():
    """Backward-compatible wrapper that centers the screen like before."""
    center_screen_clear(lines=10)

def typewriter_print(text, delay=0.03):
    """Prints text with a typewriter effect."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def spinner_pause(duration, text="Processing..."):
    """Displays an animated spinner for a set duration."""
    spinner_chars = ['|', '/', '-', '\\']
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        char = spinner_chars[i % len(spinner_chars)]
        print(f'\r{text} {char}', end='', flush=True)
        time.sleep(0.1)
        i += 1
    print('\r' + ' ' * (len(text) + 5) + '\r', end='')

def progress_bar(duration, text):
    """Displays an animated progress bar for actions."""
    total_blocks = 20
    print()
    for i in range(total_blocks + 1):
        percent = i / total_blocks
        filled_blocks = int(percent * total_blocks)
        bar = '█' * filled_blocks + ' ' * (total_blocks - filled_blocks)
        print(f'\r{text} [{bar}] {int(percent*100)}%', end='', flush=True)
        time.sleep(duration / total_blocks)
    print()

def display_welcome():
    """Displays the initial welcome message."""
    center_screen()
    print("#########################################################")
    print("#                                                       #")
    print("#      UniLife Simulator: The Freshman's Fortune        #")
    print("#                                                       #")
    print("#########################################################")
    print("\n")
    premise = (
        "You are a freshman, just arrived at University. This is your first week of true\n"
        "independence, a whirlwind of new classes, new people, and new responsibilities.\n"
        "You have exactly 7 days until your first major quiz. Your goal is to not only\n"
        "pass the quiz but to survive the week with your sanity, social life, and bank\n"
        "account intact. Can you manage your time, money, and energy to conquer the\n"
        "freshman's fortune, or will you be calling home for a bailout by Friday?\n"
    )
    typewriter_print(premise, delay=0.01)
    input("Press Enter to begin...")

def display_status(game_state):
    """Displays the player's current statistics with better formatting."""
    stats, day, name = game_state['stats'], game_state['current_day'], game_state['player_name']
    
    print("╔═════════════════════════════════════════════════╗")
    print(f"║ DAY {day}           --- STATUS: {name} ---            ║")
    print("╠════════════════════╦════════════════════════════╣")
    print(f"║   Academic Score   ║ {stats['academic']:<3}/100                     ║")
    print(f"║   Social Score     ║ {stats['social']:<3}/100                     ║")
    print(f"║   Well-being       ║ {stats['wellbeing']:<3}/100                     ║")
    print(f"║   Cash             ║ ${game_state['cash']:<7.2f}                     ║")
    if game_state['active_buff_desc'] or game_state['temporary_effect'].get('desc'):
        print("╠════════════════════╩════════════════════════════╣")
    if game_state['active_buff_desc']:
        print(f"║ VIBE: {game_state['active_buff_desc']:<38}║")
    if game_state['temporary_effect'].get('desc'):
        print(f"║ EFFECT: {game_state['temporary_effect']['desc']:<36}║")
    print("╚═════════════════════════════════════════════════╝\n")

def display_final_report(game_state, result_message):
    """Displays the final outcome and stats at the end of the game."""
    center_screen()
    print("╔═════════════════════════════════════════════════╗")
    print("║               END OF WEEK REPORT                ║")
    print("╚═════════════════════════════════════════════════╝")
    display_status(game_state)
    print("\n--- OUTCOME ---")
    typewriter_print(result_message)
    print("="*50 + "\n")

# ==============================================================================
# SECTION: GAME LOGIC FUNCTIONS
# ==============================================================================

def initialize_game_state():
    """Creates a new game state dictionary with default values."""
    return {
        'player_name': 'Player', 'current_day': 1, 'actions_left': 2,
        'stats': {'academic': 15, 'social': 15, 'wellbeing': 85}, 'cash': 20.00,
        'tasks': [
            {'desc': 'Submit Programming Assignment', 'due_day': 4, 'complete': False, 'academic_reward': 15, 'wellbeing_penalty': 10},
            {'desc': 'Attend Calculus Lecture', 'due_day': 2, 'complete': False, 'academic_reward': 10, 'academic_penalty': 5}
        ],
        'active_buff': {}, 'active_buff_desc': None,
        'game_over': False, 'game_over_message': '',
        'playlist_selected_today': False,
        'temporary_effect': {}
    }

def apply_stat_change(game_state, stat, value):
    """Applies a change to a stat, handling buffs and clamping between 0 and 100."""
    if stat == 'academic' and 'academic_multiplier' in game_state['active_buff'] and value > 0:
        value = int(value * game_state['active_buff']['academic_multiplier'])
    if stat == 'academic' and game_state['temporary_effect'].get('academic_multiplier'):
        value = int(value * game_state['temporary_effect']['academic_multiplier'])
        
    game_state['stats'][stat] += value
    if game_state['stats'][stat] > 100: game_state['stats'][stat] = 100
    elif game_state['stats'][stat] < 0: game_state['stats'][stat] = 0
    return game_state

def resolve_action(game_state, success_chance, success_outcome, failure_outcome):
    """The core engine for the 'Focus' system. Resolves an action based on success chance."""
    roll, game_state['actions_left'] = random.random(), game_state['actions_left'] - 1

    if roll < success_chance:
        message, stat_changes = success_outcome['message'], success_outcome['stat_changes']
    else:
        message, stat_changes = failure_outcome['message'], failure_outcome['stat_changes']

    typewriter_print(message)
    for stat, value in stat_changes.items():
        if stat == 'cash': game_state['cash'] += value
        else: game_state = apply_stat_change(game_state, stat, value)
            
    changes_str = ", ".join([f"{k.capitalize()} {'+' if v > 0 else ''}{v}" for k, v in stat_changes.items()])
    typewriter_print(f"  ({changes_str})")
    
    return game_state

def select_playlist(game_state):
    """Manages the daily playlist selection and applies the corresponding buff."""
    print("Choose your playlist for the day to set the mood:")
    playlists = {
        '1': ("Focus Study Mix", {'academic_multiplier': 1.5}, "Grants a 1.5x boost to all 'Academic' gains today."),
        '2': ("High-Energy Workout Hits", {'wellbeing_boost': 15}, "Provides a significant boost to 'Well-being'."),
        '3': ("Chill Lo-Fi Beats", {'stress_reduction': 0.5}, "Reduces the negative impact of stressful events.")
    }
    for key, (name, _, desc) in playlists.items():
        print("  [" + key + "] " + name + ": " + desc)
    choice = input("> ")
    if choice in playlists:
        name, buff, _ = playlists[choice]
        game_state['active_buff'], game_state['active_buff_desc'] = buff, name
        typewriter_print("\nYou put on the '" + name + "'. You're ready for the day.")
        if 'wellbeing_boost' in buff:
            game_state = apply_stat_change(game_state, 'wellbeing', buff['wellbeing_boost'])
            typewriter_print("You feel energized! Well-being increased.")
    else:
        typewriter_print("\nYou decide to just go with the flow, no special playlist today.")
        game_state['active_buff'], game_state['active_buff_desc'] = {}, "None"
    
    game_state['playlist_selected_today'] = True
    spinner_pause(1.5, "Applying buff...")
    return game_state

def handle_action_study(game_state):
    """Defines the outcomes and stat changes for studying."""
    progress_bar(1.5, "Studying...")
    success_chance = game_state['stats']['wellbeing'] / 100.0
    success = {'message': "\nYou spend a solid three hours in the library. The concepts are clicking.", 'stat_changes': {'academic': 10, 'wellbeing': -8}}
    failure = {'message': "\nYou try to study, but your mind keeps drifting. You read the same page three times.", 'stat_changes': {'academic': 2, 'wellbeing': -10}}
    return resolve_action(game_state, success_chance, success, failure)

def handle_action_socialize(game_state):
    """Defines the outcomes and stat changes for socializing."""
    cost = 15.00
    if game_state['cash'] < cost:
        typewriter_print("\nYou want to go out, but you can't afford it right now.")
        return game_state
    progress_bar(1.5, "Socializing...")
    success_chance = game_state['stats']['wellbeing'] / 100.0
    success = {'message': f"\nYou grab lunch with people from your dorm. It was a great time!", 'stat_changes': {'social': 15, 'wellbeing': 5, 'cash': -cost}}
    failure = {'message': f"\nYou go out, but the conversation feels forced and awkward.", 'stat_changes': {'social': 0, 'wellbeing': -5, 'cash': -cost}}
    return resolve_action(game_state, success_chance, success, failure)

def handle_action_exercise(game_state):
    """Defines the outcomes and stat changes for exercising."""
    progress_bar(1.5, "Exercising...")
    success_chance = game_state['stats']['wellbeing'] / 100.0
    success = {'message': "\nYou go for a run around campus. You feel refreshed and clear-headed.", 'stat_changes': {'wellbeing': 15, 'academic': -5}}
    failure = {'message': "\nYou try to exercise, but you just don't have the energy and give up early.", 'stat_changes': {'wellbeing': 5, 'academic': -2}}
    return resolve_action(game_state, success_chance, success, failure)

def handle_action_work(game_state):
    """Defines the outcomes and stat changes for working."""
    progress_bar(2.0, "Working shift...")
    success_chance = game_state['stats']['wellbeing'] / 100.0
    success = {'message': "\nYou work an efficient shift at the campus coffee shop.", 'stat_changes': {'cash': 20.00, 'wellbeing': -15, 'social': -5}}
    failure = {'message': "\nYou have a clumsy shift, dropping a tray of drinks. It's embarrassing and tiring.", 'stat_changes': {'cash': 10.00, 'wellbeing': -20, 'social': -8}}
    return resolve_action(game_state, success_chance, success, failure)

def handle_action_party(game_state):
    """Defines the outcomes and stat changes for partying."""
    cost = 20.00
    if game_state['cash'] < cost:
        typewriter_print("\nYour friends invite you to a party, but you can't afford the cover charge.")
        return game_state
    progress_bar(2.0, "Partying...")
    success_chance = game_state['stats']['wellbeing'] / 100.0
    success = {'message': "\nThe party is amazing! You meet tons of new people and have a blast.", 'stat_changes': {'social': 25, 'wellbeing': -10, 'academic': -10, 'cash': -cost}}
    failure = {'message': "\nThe party is lame. You stand in a corner and leave early, feeling tired and poorer.", 'stat_changes': {'social': 5, 'wellbeing': -15, 'academic': -5, 'cash': -cost}}
    return resolve_action(game_state, success_chance, success, failure)

def handle_action_videogames(game_state):
    """Defines the outcomes and stat changes for playing video games."""
    progress_bar(1.5, "Gaming...")
    success_chance = game_state['stats']['wellbeing'] / 100.0
    success = {'message': "\nYou lose yourself in a video game for a few hours. It's a great way to unwind.", 'stat_changes': {'wellbeing': 15, 'academic': -10, 'social': -5}}
    failure = {'message': "\nYou get stuck on a hard level and rage quit. You feel more stressed than when you started.", 'stat_changes': {'wellbeing': -5, 'academic': -5, 'social': -5}}
    return resolve_action(game_state, success_chance, success, failure)

def handle_action_todo(game_state):
    """Manages the to-do list, allowing players to complete tasks."""
    print("\n--- YOUR TO-DO LIST ---")
    incomplete_tasks = [t for t in game_state['tasks'] if not t['complete']]
    if not incomplete_tasks: print("Nothing on your to-do list right now!"); return game_state
    for i, task in enumerate(incomplete_tasks): print("  [" + str(i + 1) + "] " + task['desc'] + " (Due: Day " + str(task['due_day']) + ")")
    print("  [0] Go back")
    choice = input("Enter task number to work on it, or 0 to go back: > ")
    if choice.isdigit():
        choice_num = int(choice)
        if 1 <= choice_num <= len(incomplete_tasks):
            task_to_complete = incomplete_tasks[choice_num - 1]
            for task in game_state['tasks']:
                if task['desc'] == task_to_complete['desc']: task['complete'] = True
            reward = task_to_complete['academic_reward']
            game_state, game_state['actions_left'] = apply_stat_change(game_state, 'academic', reward), game_state['actions_left'] - 1
            typewriter_print("\nTask '" + task_to_complete['desc'] + "' completed! Great job. (Academic +" + str(reward) + ")")
        elif choice_num != 0: print("Invalid choice.")
    else: print("Invalid input. Please enter a number.")
    return game_state

def end_of_day_update(game_state):
    """Manages end-of-day processes like missed tasks and random events."""
    print("\nThe day comes to an end...")
    for task in game_state['tasks']:
        if not task['complete'] and game_state['current_day'] >= task['due_day']:
            typewriter_print("You missed the deadline for: '" + task['desc'] + "'!")
            if 'academic_penalty' in task:
                game_state = apply_stat_change(game_state, 'academic', -task['academic_penalty'])
                typewriter_print(f"  (Academic -{task['academic_penalty']})")
            if 'wellbeing_penalty' in task:
                game_state = apply_stat_change(game_state, 'wellbeing', -task['wellbeing_penalty'])
                typewriter_print(f"  (Well-being -{task['wellbeing_penalty']})")
            task['complete'] = True
            time.sleep(1)
            
    if random.randint(1, 100) <= 60:
        spinner_pause(1, "...")
        typewriter_print("\n--- RANDOM EVENT ---")
        time.sleep(1)
        event_roll = random.randint(1, 5)
        if event_roll == 1:
            typewriter_print("You find a $20 bill on the sidewalk!")
            game_state['cash'] += 20.00
        elif event_roll == 2:
            typewriter_print("You get a surprise call from family. It's great to catch up.")
            game_state = apply_stat_change(game_state, 'wellbeing', 15)
        elif event_roll == 3:
            typewriter_print("You get a great night's sleep. You'll feel extra refreshed tomorrow.")
            game_state['temporary_effect'] = {'desc': "Well-Rested", 'stat_changes': {'wellbeing': 15}}
        elif event_roll == 4:
            typewriter_print("You toss and turn, feeling anxious about your classes.")
            game_state['temporary_effect'] = {'desc': "Anxious", 'academic_multiplier': 0.75}
        else:
            typewriter_print("A sudden headache makes it hard to focus. You feel drained.")
            game_state = apply_stat_change(game_state, 'wellbeing', -10)
    
    spinner_pause(2.5, "Ending the day...")
    game_state['current_day'] += 1
    game_state['actions_left'] = 2
    game_state['active_buff'], game_state['active_buff_desc'] = {}, None
    game_state['playlist_selected_today'] = False
    return game_state

def check_game_over(game_state):
    """Checks if the game has ended due to a stat falling to zero."""
    stats = game_state['stats']
    if stats['academic'] <= 0: game_state['game_over'], game_state['game_over_message'] = True, "You've fallen too far behind. Game Over."
    elif stats['social'] <= 0: game_state['game_over'], game_state['game_over_message'] = True, "You feel completely isolated. Game Over."
    elif stats['wellbeing'] <= 0: game_state['game_over'], game_state['game_over_message'] = True, "You're burnt out. Game Over."
    elif game_state['cash'] < 0: game_state['game_over'], game_state['game_over_message'] = True, "You're out of money. Game Over."
    return game_state

# ==============================================================================
# SECTION: DEMO MODE SCRIPT AND FUNCTIONS
# ==============================================================================

WINNING_DEMO_STORY = """
╔═════════════════════════════════════════════════╗
║ DAY 1           --- STATUS: Jordan (Winner) ---           ║
╠════════════════════╦════════════════════════════╣
║   Academic Score   ║ 15/100                     ║
║   Social Score     ║ 15/100                     ║
║   Well-being       ║ 85/100                     ║
║   Cash             ║ $20.00                      ║
╚═════════════════════════════════════════════════╝

Choose your playlist for the day to set the mood:
  [1] Focus Study Mix: Grants a 1.5x boost to all 'Academic' gains today.
  [2] High-Energy Workout Hits: Provides a significant boost to 'Well-being'.
  [3] Chill Lo-Fi Beats: Reduces the negative impact of stressful events.
> 1

You put on the 'Focus Study Mix'. You're ready for the day.
Applying buff... 

Your current Focus (from Well-being) gives you a 85% chance of success.
What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 7

--- YOUR TO-DO LIST ---
  [1] Attend Calculus Lecture (Due: Day 2)
  [2] Submit Programming Assignment (Due: Day 4)
  [0] Go back
Enter task number to work on it, or 0 to go back: > 1

Task 'Attend Calculus Lecture' completed! Great job. (Academic +15)

What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 1

Studying...
 [████████████████████] 100%

You spend a solid three hours in the library. The concepts are clicking.
  (Academic +15, Wellbeing -8)

The day comes to an end...
Ending the day... 

==================================================================

╔═════════════════════════════════════════════════╗
║ DAY 2           --- STATUS: Jordan (Winner) ---           ║
╠════════════════════╦════════════════════════════╣
║   Academic Score   ║ 45/100                     ║
║   Social Score     ║ 15/100                     ║
║   Well-being       ║ 77/100                     ║
║   Cash             ║ $20.00                      ║
╚═════════════════════════════════════════════════╝

Choose your playlist for the day to set the mood:
  [1] Focus Study Mix: Grants a 1.5x boost to all 'Academic' gains today.
  [2] High-Energy Workout Hits: Provides a significant boost to 'Well-being'.
  [3] Chill Lo-Fi Beats: Reduces the negative impact of stressful events.
> 3

You put on the 'Chill Lo-Fi Beats'. You're ready for the day.
Applying buff... 

Your current Focus (from Well-being) gives you a 77% chance of success.
What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 4

Working shift...
 [████████████████████] 100%

You work an efficient shift at the campus coffee shop.
  (Cash +20.0, Wellbeing -15, Social -5)

What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 4

Working shift...
 [████████████████████] 100%

You work an efficient shift at the campus coffee shop.
  (Cash +20.0, Wellbeing -15, Social -5)

The day comes to an end...
Ending the day... 

==================================================================

╔═════════════════════════════════════════════════╗
║ DAY 3           --- STATUS: Jordan (Winner) ---           ║
╠════════════════════╦════════════════════════════╣
║   Academic Score   ║ 45/100                     ║
║   Social Score     ║ 5/100                      ║
║   Well-being       ║ 47/100                     ║
║   Cash             ║ $60.00                      ║
╚═════════════════════════════════════════════════╝

Choose your playlist for the day to set the mood:
  [1] Focus Study Mix: Grants a 1.5x boost to all 'Academic' gains today.
  [2] High-Energy Workout Hits: Provides a significant boost to 'Well-being'.
  [3] Chill Lo-Fi Beats: Reduces the negative impact of stressful events.
> 2

You put on the 'High-Energy Workout Hits'. You're ready for the day.
You feel energized! Well-being increased.
Applying buff... 

Your current Focus (from Well-being) gives you a 62% chance of success.
What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 2

Socializing...
 [████████████████████] 100%

You grab lunch with people from your dorm. It was a great time!
  (Social +15, Wellbeing +5, Cash -15.0)

What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 3

Exercising...
 [████████████████████] 100%

You go for a run around campus. You feel refreshed and clear-headed.
  (Wellbeing +15, Academic -5)

The day comes to an end...
Ending the day... 

==================================================================

╔═════════════════════════════════════════════════╗
║ DAY 4           --- STATUS: Jordan (Winner) ---           ║
╠════════════════════╦════════════════════════════╣
║   Academic Score   ║ 40/100                     ║
║   Social Score     ║ 20/100                     ║
║   Well-being       ║ 82/100                     ║
║   Cash             ║ $45.00                      ║
╚═════════════════════════════════════════════════╝

Choose your playlist for the day to set the mood:
  [1] Focus Study Mix: Grants a 1.5x boost to all 'Academic' gains today.
  [2] High-Energy Workout Hits: Provides a significant boost to 'Well-being'.
  [3] Chill Lo-Fi Beats: Reduces the negative impact of stressful events.
> 1

You put on the 'Focus Study Mix'. You're ready for the day.
Applying buff... 

Your current Focus (from Well-being) gives you a 82% chance of success.
What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 7

--- YOUR TO-DO LIST ---
  [1] Submit Programming Assignment (Due: Day 4)
  [0] Go back
Enter task number to work on it, or 0 to go back: > 1

Task 'Submit Programming Assignment' completed! Great job. (Academic +22)

What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 1

Studying...
 [████████████████████] 100%

You spend a solid three hours in the library. The concepts are clicking.
  (Academic +15, Wellbeing -8)

The day comes to an end...
Ending the day... 

==================================================================

╔═════════════════════════════════════════════════╗
║ DAY 5           --- STATUS: Jordan (Winner) ---           ║
╠════════════════════╦════════════════════════════╣
║   Academic Score   ║ 77/100                     ║
║   Social Score     ║ 20/100                     ║
║   Well-being       ║ 74/100                     ║
║   Cash             ║ $45.00                      ║
╚═════════════════════════════════════════════════╝

Choose your playlist for the day to set the mood:
  [1] Focus Study Mix: Grants a 1.5x boost to all 'Academic' gains today.
  [2] High-Energy Workout Hits: Provides a significant boost to 'Well-being'.
  [3] Chill Lo-Fi Beats: Reduces the negative impact of stressful events.
> 2

You put on the 'High-Energy Workout Hits'. You're ready for the day.
You feel energized! Well-being increased.
Applying buff... 

Your current Focus (from Well-being) gives you a 89% chance of success.
What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 6

Gaming...
 [████████████████████] 100%

You lose yourself in a video game for a few hours. It's a great way to unwind.
  (Wellbeing +15, Academic -10, Social -5)

What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 2

Socializing...
 [████████████████████] 100%

You grab lunch with people from your dorm. It was a great time!
  (Social +15, Wellbeing +5, Cash -15.0)

The day comes to an end...
Ending the day... 

==================================================================

╔═════════════════════════════════════════════════╗
║ DAY 6           --- STATUS: Jordan (Winner) ---           ║
╠════════════════════╦════════════════════════════╣
║   Academic Score   ║ 67/100                     ║
║   Social Score     ║ 30/100                     ║
║   Well-being       ║ 100/100                    ║
║   Cash             ║ $30.00                      ║
╚═════════════════════════════════════════════════╝

Choose your playlist for the day to set the mood:
  [1] Focus Study Mix: Grants a 1.5x boost to all 'Academic' gains today.
  [2] High-Energy Workout Hits: Provides a significant boost to 'Well-being'.
  [3] Chill Lo-Fi Beats: Reduces the negative impact of stressful events.
> 3

You put on the 'Chill Lo-Fi Beats'. You're ready for the day.
Applying buff... 

Your current Focus (from Well-being) gives you a 100% chance of success.
What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 4

Working shift...
 [████████████████████] 100%

You work an efficient shift at the campus coffee shop.
  (Cash +20.0, Wellbeing -15, Social -5)

What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 2

Socializing...
 [████████████████████] 100%

You grab lunch with people from your dorm. It was a great time!
  (Social +15, Wellbeing +5, Cash -15.0)

The day comes to an end...
... 
--- RANDOM EVENT ---
A sudden headache makes it hard to focus. You feel drained.
  (Wellbeing -10)
Ending the day... 

==================================================================

╔═════════════════════════════════════════════════╗
║ DAY 7           --- STATUS: Jordan (Winner) ---           ║
╠════════════════════╦════════════════════════════╣
║   Academic Score   ║ 67/100                     ║
║   Social Score     ║ 40/100                     ║
║   Well-being       ║ 80/100                     ║
║   Cash             ║ $35.00                      ║
╚═════════════════════════════════════════════════╝

Choose your playlist for the day to set the mood:
  [1] Focus Study Mix: Grants a 1.5x boost to all 'Academic' gains today.
  [2] High-Energy Workout Hits: Provides a significant boost to 'Well-being'.
  [3] Chill Lo-Fi Beats: Reduces the negative impact of stressful events.
> 1

You put on the 'Focus Study Mix'. You're ready for the day.
Applying buff... 

Your current Focus (from Well-being) gives you a 80% chance of success.
What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 1

Studying...
 [████████████████████] 100%

You spend a solid three hours in the library. The concepts are clicking.
  (Academic +15, Wellbeing -8)

What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 1

Studying...
 [████████████████████] 100%

You spend a solid three hours in the library. The concepts are clicking.
  (Academic +15, Wellbeing -8)

The day comes to an end...
Ending the day... 

==================================================================

╔═════════════════════════════════════════════════╗
║               END OF WEEK REPORT                ║
╚═════════════════════════════════════════════════╝
╔═════════════════════════════════════════════════╗
║ DAY 8           --- STATUS: Jordan (Winner) ---           ║
╠════════════════════╦════════════════════════════╣
║   Academic Score   ║ 97/100                     ║
║   Social Score     ║ 40/100                     ║
║   Well-being       ║ 64/100                     ║
║   Cash             ║ $35.00                      ║
╚═════════════════════════════════════════════════╝

--- OUTCOME ---
Congratulations! You passed the quiz and successfully navigated the chaos of your first week!
==================================================
"""

LOSING_DEMO_STORY = """
╔═════════════════════════════════════════════════╗
║ DAY 1        --- STATUS: Casey (Struggler) ---        ║
╠════════════════════╦════════════════════════════╣
║   Academic Score   ║ 15/100                     ║
║   Social Score     ║ 15/100                     ║
║   Well-being       ║ 85/100                     ║
║   Cash             ║ $20.00                      ║
╚═════════════════════════════════════════════════╝

Choose your playlist for the day to set the mood:
  [1] Focus Study Mix: Grants a 1.5x boost to all 'Academic' gains today.
  [2] High-Energy Workout Hits: Provides a significant boost to 'Well-being'.
  [3] Chill Lo-Fi Beats: Reduces the negative impact of stressful events.
> 3

You put on the 'Chill Lo-Fi Beats'. You're ready for the day.
Applying buff... 

Your current Focus (from Well-being) gives you a 85% chance of success.
What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 5

Partying...
 [████████████████████] 100%

The party is amazing! You meet tons of new people and have a blast.
  (Social +25, Wellbeing -10, Academic -10, Cash -20.0)

What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 5

Your friends invite you to a party, but you can't afford the cover charge.

What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 4

Working shift...
 [████████████████████] 100%

You have a clumsy shift, dropping a tray of drinks. It's embarrassing and tiring.
  (Cash +10.0, Wellbeing -20, Social -8)

The day comes to an end...
Ending the day... 

==================================================================

╔═════════════════════════════════════════════════╗
║ DAY 2        --- STATUS: Casey (Struggler) ---        ║
╠════════════════════╦════════════════════════════╣
║   Academic Score   ║ 5/100                      ║
║   Social Score     ║ 32/100                     ║
║   Well-being       ║ 55/100                     ║
║   Cash             ║ $10.00                      ║
╚═════════════════════════════════════════════════╝

Choose your playlist for the day to set the mood:
  [1] Focus Study Mix: Grants a 1.5x boost to all 'Academic' gains today.
  [2] High-Energy Workout Hits: Provides a significant boost to 'Well-being'.
  [3] Chill Lo-Fi Beats: Reduces the negative impact of stressful events.
> 2

You put on the 'High-Energy Workout Hits'. You're ready for the day.
You feel energized! Well-being increased.
Applying buff... 

Your current Focus (from Well-being) gives you a 70% chance of success.
What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 7

--- YOUR TO-DO LIST ---
  [1] Attend Calculus Lecture (Due: Day 2)
  [2] Submit Programming Assignment (Due: Day 4)
  [0] Go back
Enter task number to work on it, or 0 to go back: > 1

Task 'Attend Calculus Lecture' completed! Great job. (Academic +10)

What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 1

Studying...
 [████████████████████] 100%

You try to study, but your mind keeps drifting. You read the same page three times.
  (Academic +2, Wellbeing -10)

The day comes to an end...
... 
--- RANDOM EVENT ---
You toss and turn, feeling anxious about your classes.
Ending the day... 

==================================================================

╔═════════════════════════════════════════════════╗
║ DAY 3        --- STATUS: Casey (Struggler) ---        ║
╠════════════════════╦════════════════════════════╣
║   Academic Score   ║ 17/100                     ║
║   Social Score     ║ 32/100                     ║
║   Well-being       ║ 60/100                     ║
║   Cash             ║ $10.00                      ║
╚═════════════════════════════════════════════════╝

Last night's event effect 'Anxious' is now active...

Choose your playlist for the day to set the mood:
  [1] Focus Study Mix: Grants a 1.5x boost to all 'Academic' gains today.
  [2] High-Energy Workout Hits: Provides a significant boost to 'Well-being'.
  [3] Chill Lo-Fi Beats: Reduces the negative impact of stressful events.
> 2

You put on the 'High-Energy Workout Hits'. You're ready for the day.
You feel energized! Well-being increased.
Applying buff... 

Your current Focus (from Well-being) gives you a 75% chance of success.
What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 2

You want to go out, but you can't afford it right now.

What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 6

Gaming...
 [████████████████████] 100%

You lose yourself in a video game for a few hours. It's a great way to unwind.
  (Wellbeing +15, Academic -10, Social -5)

The day comes to an end...
Ending the day... 

==================================================================

╔═════════════════════════════════════════════════╗
║ DAY 4        --- STATUS: Casey (Struggler) ---        ║
╠════════════════════╦════════════════════════════╣
║   Academic Score   ║ 7/100                      ║
║   Social Score     ║ 27/100                     ║
║   Well-being       ║ 90/100                     ║
║   Cash             ║ $10.00                      ║
╚═════════════════════════════════════════════════╝

Choose your playlist for the day to set the mood:
  [1] Focus Study Mix: Grants a 1.5x boost to all 'Academic' gains today.
  [2] High-Energy Workout Hits: Provides a significant boost to 'Well-being'.
  [3] Chill Lo-Fi Beats: Reduces the negative impact of stressful events.
> 1

You put on the 'Focus Study Mix'. You're ready for the day.
Applying buff... 

Your current Focus (from Well-being) gives you a 90% chance of success.
What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 7

--- YOUR TO-DO LIST ---
  [1] Submit Programming Assignment (Due: Day 4)
  [0] Go back
Enter task number to work on it, or 0 to go back: > 1

Task 'Submit Programming Assignment' completed! Great job. (Academic +22)

What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 1

Studying...
 [████████████████████] 100%

You spend a solid three hours in the library. The concepts are clicking.
  (Academic +15, Wellbeing -8)

The day comes to an end...
... 
--- RANDOM EVENT ---
A sudden headache makes it hard to focus. You feel drained.
  (Wellbeing -10)
Ending the day... 

==================================================================

╔═════════════════════════════════════════════════╗
║ DAY 5        --- STATUS: Casey (Struggler) ---        ║
╠════════════════════╦════════════════════════════╣
║   Academic Score   ║ 44/100                     ║
║   Social Score     ║ 27/100                     ║
║   Well-being       ║ 72/100                     ║
║   Cash             ║ $10.00                      ║
╚═════════════════════════════════════════════════╝

Choose your playlist for the day to set the mood:
  [1] Focus Study Mix: Grants a 1.5x boost to all 'Academic' gains today.
  [2] High-Energy Workout Hits: Provides a significant boost to 'Well-being'.
  [3] Chill Lo-Fi Beats: Reduces the negative impact of stressful events.
> 3

You put on the 'Chill Lo-Fi Beats'. You're ready for the day.
Applying buff... 

Your current Focus (from Well-being) gives you a 72% chance of success.
What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 5

Your friends invite you to a party, but you can't afford the cover charge.

What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 4

Working shift...
 [████████████████████] 100%

You work an efficient shift at the campus coffee shop.
  (Cash +20.0, Wellbeing -15, Social -5)

What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 6

Gaming...
 [████████████████████] 100%

You get stuck on a hard level and rage quit. You feel more stressed than when you started.
  (Wellbeing -5, Academic -5, Social -5)

The day comes to an end...
Ending the day... 

==================================================================

╔═════════════════════════════════════════════════╗
║ DAY 6        --- STATUS: Casey (Struggler) ---        ║
╠════════════════════╦════════════════════════════╣
║   Academic Score   ║ 39/100                     ║
║   Social Score     ║ 17/100                     ║
║   Well-being       ║ 52/100                     ║
║   Cash             ║ $30.00                      ║
╚═════════════════════════════════════════════════╝

Choose your playlist for the day to set the mood:
  [1] Focus Study Mix: Grants a 1.5x boost to all 'Academic' gains today.
  [2] High-Energy Workout Hits: Provides a significant boost to 'Well-being'.
  [3] Chill Lo-Fi Beats: Reduces the negative impact of stressful events.
> 2

You put on the 'High-Energy Workout Hits'. You're ready for the day.
You feel energized! Well-being increased.
Applying buff... 

Your current Focus (from Well-being) gives you a 67% chance of success.
What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 5

Partying...
 [████████████████████] 100%

The party is lame. You stand in a corner and leave early, feeling tired and poorer.
  (Social +5, Wellbeing -15, Academic -5, Cash -20.0)

What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 2

You want to go out, but you can't afford it right now.

What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 4

Working shift...
 [████████████████████] 100%

You have a clumsy shift, dropping a tray of drinks. It's embarrassing and tiring.
  (Cash +10.0, Wellbeing -20, Social -8)

The day comes to an end...
... 
--- RANDOM EVENT ---
You get a surprise call from family. It's great to catch up.
  (Wellbeing +15)
Ending the day... 

==================================================================

╔═════════════════════════════════════════════════╗
║ DAY 7        --- STATUS: Casey (Struggler) ---        ║
╠════════════════════╦════════════════════════════╣
║   Academic Score   ║ 34/100                     ║
║   Social Score     ║ 14/100                     ║
║   Well-being       ║ 47/100                     ║
║   Cash             ║ $20.00                      ║
╚═════════════════════════════════════════════════╝

Choose your playlist for the day to set the mood:
  [1] Focus Study Mix: Grants a 1.5x boost to all 'Academic' gains today.
  [2] High-Energy Workout Hits: Provides a significant boost to 'Well-being'.
  [3] Chill Lo-Fi Beats: Reduces the negative impact of stressful events.
> 1

You put on the 'Focus Study Mix'. You're ready for the day.
Applying buff... 

Your current Focus (from Well-being) gives you a 47% chance of success.
What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 1

Studying...
 [████████████████████] 100%

You try to study, but your mind keeps drifting. You read the same page three times.
  (Academic +3, Wellbeing -10)

What would you like to do?
  [1] Study at the Library
  [2] Grab lunch with friends
  [3] Go for a run
  [4] Work a shift
  [5] Go to a Party
  [6] Play Video Games
  [7] Check your To-Do List
> 6

Gaming...
 [████████████████████] 100%

You lose yourself in a video game for a few hours. It's a great way to unwind.
  (Wellbeing +15, Academic -10, Social -5)

The day comes to an end...
Ending the day... 

==================================================================

╔═════════════════════════════════════════════════╗
║               END OF WEEK REPORT                ║
╚═════════════════════════════════════════════════╝
╔═════════════════════════════════════════════════╗
║ DAY 8        --- STATUS: Casey (Struggler) ---        ║
╠════════════════════╦════════════════════════════╣
║   Academic Score   ║ 27/100                     ║
║   Social Score     ║ 9/100                      ║
║   Well-being       ║ 52/100                     ║
║   Cash             ║ $20.00                      ║
╚═════════════════════════════════════════════════╝

--- OUTCOME ---
You sit down for the quiz, but the questions look like a foreign language. You failed. Game Over.
==================================================
"""

def run_demo(title, story):
    """Displays a pre-written story as a single block of text for presentation scrolling."""
    center_screen_clear()
    
    # Simply print the entire story string at once
    print(story.strip())

    print("\n\n--- DEMO COMPLETE ---")
    input("Press Enter to return to the main menu...")

def play_full_game():
    """Contains the original, interactive game loop for a human player."""
    display_welcome()
    game_state = initialize_game_state()
    
    player_name = input("Please enter your name: > ")
    if player_name: game_state['player_name'] = player_name
    else: game_state['player_name'] = "Alex"

    while game_state['current_day'] <= 7 and not game_state['game_over']:
        center_screen()
        
        if game_state['temporary_effect']:
            effect = game_state['temporary_effect']
            typewriter_print(f"Last night's event effect '{effect['desc']}' is now active...")
            if 'stat_changes' in effect:
                for stat, value in effect['stat_changes'].items():
                    game_state = apply_stat_change(game_state, stat, value)
            game_state['temporary_effect'] = {}
            time.sleep(2.5) 
            center_screen()

        display_status(game_state)
        
        if not game_state['playlist_selected_today']:
            game_state = select_playlist(game_state)
            center_screen()
            display_status(game_state)
        
        print(f"Your current Focus (from Well-being) gives you a {game_state['stats']['wellbeing']}% chance of success.")
        print("You have " + str(game_state['actions_left']) + " actions left today.")
        print("What would you like to do?")
        
        actions = {"1":handle_action_study,"2":handle_action_socialize,"3":handle_action_exercise,"4":handle_action_work,"5":handle_action_party,"6":handle_action_videogames,"7":handle_action_todo}
        descriptions = {"1":"Study at the Library","2":"Grab lunch with friends","3":"Go for a run","4":"Work a shift","5":"Go to a Party","6":"Play Video Games","7":"Check your To-Do List"}
        for key, description in descriptions.items():
            print("  [" + key + "] " + description)

        player_choice = input("> ")
        if player_choice in actions:
            action_function = actions[player_choice]
            game_state = action_function(game_state)
            game_state = check_game_over(game_state)
        else:
            print("Invalid choice. Please select from the menu.")
        
        if game_state['actions_left'] > 0 and not game_state['game_over']:
            input("\nPress Enter to continue...")

        if game_state['actions_left'] <= 0 and not game_state['game_over']:
            game_state = end_of_day_update(game_state)
            game_state = check_game_over(game_state)

    if game_state['game_over']:
        display_final_report(game_state, game_state['game_over_message'])
    else:
        typewriter_print("\nIt's the end of the week. Time for your first big quiz...")
        time.sleep(2)
        quiz_success = game_state['stats']['academic'] >= 60
        win_condition = (quiz_success and game_state['stats']['social'] >= 30 and
                                 game_state['stats']['wellbeing'] >= 30 and game_state['cash'] > 0)
        if win_condition: final_message = "Congratulations! You passed the quiz and successfully navigated the chaos of your first week!"
        elif not quiz_success: final_message = "You sit down for the quiz, but the questions look like a foreign language. You failed. Game Over."
        else: final_message = "You passed your quiz, but at what cost? You're broke, stressed, or lonely. Game Over."
        display_final_report(game_state, final_message)

# ==============================================================================
# SECTION: MAIN GAME EXECUTION
# ==============================================================================

def main():
    """The main function to run the game, now featuring a main menu."""
    while True:
        center_screen_clear(lines=4)
        print("#########################################################")
        print("#                                                       #")
        print("#      UniLife Simulator: The Freshman's Fortune        #")
        print("#                                                       #")
        print("#########################################################\n")
        print("Welcome! Please choose an option:")
        print("  [1] Start a New Game")
        print("  [2] Watch Demo: The Successful Student (WIN)")
        print("  [3] Watch Demo: The Downward Spiral (LOSS)")
        print("  [4] Exit")
        choice = input("> ")

        if choice == '1':
            play_full_game()
            if input("\nPlay again? (Y/N) > ").lower() != 'y':
                break
        elif choice == '2':
            run_demo("The Successful Student", WINNING_DEMO_STORY)
        elif choice == '3':
            run_demo("The Downward Spiral", LOSING_DEMO_STORY)
        elif choice == '4':
            print("Thanks for playing!")
            break
        else:
            print("Invalid choice. Please enter a number.")
            time.sleep(1.5)

if __name__ == "__main__":
    main()
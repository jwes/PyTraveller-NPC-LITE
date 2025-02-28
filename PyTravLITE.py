#
# LITE chargen app for Traveller NPCs v0.3.2.
# https://github.com/ShawnDriscoll/PyTraveller-NPC-LITE
#
# This LITE CharGen for Traveller is a Python 3.9.13 program for generating
# NPCs for Traveller.
#
# bottle testing has begun with the release of 0.1.0.
# Run this code at the CMD prompt while pointing your web browser
# to http://localhost:8080/generate
#
#
# The Traveller game in all forms is owned by Far Future Enterprises.
# Copyright 1977 - 2022 Far Future Enterprises.
# Traveller is a registered trademark of Far Future Enterprises.
#

from rpg_tools.pydice.pydice import roll
import os
import logging
from random import randint
from bottle import route, run, template, get, post, request
import json


__author__ = 'Shawn Driscoll <shawndriscoll@hotmail.com>\nshawndriscoll.blogspot.com'
__version__ = '0.3.2'
__app__ = 'PyTravLITE ' + __version__


def app():

    def pick_sound(s_type):
        '''
        Pick a vowel or consonant, as well as initial and final ones.
        '''
        if s_type == V:
            sound = v_sounds[randint(1, len(v_sounds)) - 1]
        if s_type == CV:
            sound = ic_sounds[randint(1, len(ic_sounds)) - 1] + v_sounds[randint(1, len(v_sounds)) - 1]
        if s_type == VC:
            sound = v_sounds[randint(1, len(v_sounds)) - 1] + fc_sounds[randint(1, len(fc_sounds)) - 1]
        if s_type == CVC:
            sound = ic_sounds[randint(1, len(ic_sounds)) - 1] + v_sounds[randint(1, len(v_sounds)) - 1] \
            + fc_sounds[randint(1, len(fc_sounds)) - 1]
        if s_type == CC:
            sound = mc_sounds[randint(1, len(mc_sounds)) - 1]
        return sound
        
    def gen_word(length):
        '''
        Generate a word
        '''
        proper = False
        while not(proper):
            temp = CC
            while temp == CC:
                temp = syllable_type[randint(1, len(syllable_type)) - 1]
            s_type = temp
            word = pick_sound(s_type)
            building = True
            while building:
                syllable = syllable_type[randint(1, len(syllable_type)) - 1]
                while temp == CC and (syllable == CV or syllable == CVC or syllable == CC):
                    syllable = syllable_type[randint(1, len(syllable_type)) - 1]
                while temp == V and (syllable == V or syllable == VC):
                    syllable = syllable_type[randint(1, len(syllable_type)) - 1]
                while temp == CV and (syllable == V or syllable == VC):
                    syllable = syllable_type[randint(1, len(syllable_type)) - 1]
                while temp == VC and (syllable == CV or syllable == CVC or syllable == CC):
                    syllable = syllable_type[randint(1, len(syllable_type)) - 1]
                while temp == CVC and (syllable == CV or syllable == CVC or syllable == CC):
                    syllable = syllable_type[randint(1, len(syllable_type)) - 1]
                if temp == VC or temp == CVC:
                    building = False
                else:
                    s_type = syllable
                    word += pick_sound(s_type)
                    temp = syllable
            
            if len(word) > 3 and len(word) < length:
                proper = True
        return chr(ord(word[0]) - 32) + word[1:len(word)]
    
    def add_background_skills(skill):
        temp = len(background_skills)
        for i in range(4):
            skill[background_skills[randint(1,temp)-1]] = 0
        
    def add_skill(job, skill, n):
        temp = len(grinder[job][3])
        for i in range(n):
            picked_skill = grinder[job][3][randint(1,temp)-1]
            if picked_skill in skill:
                #print picked_skill, '+1'
                skill[picked_skill] += 1
            else:
                #print picked_skill, '0'
                skill[picked_skill] = 0
    
    def grind(characteristic, age):
        '''
        Grind the NPC in this.
        '''
        skill = {}
        add_background_skills(skill)
        #print 'Background Skills:', skill
        terms = roll('2d6-2')
        if terms == 0:
        
            # No career
            name_title = 'Young'
            job = 'None'
        else:
            if roll('d2') == '1':
                skill['Anglic'] = 0        # Default skill
            else:
                skill['Vilani'] = 0
            skill['Jack of all Trades'] = 0     # Default skill
            
            job = career[roll('1d12-1')]
            if terms > grinder[job][1]:
                temp = grinder[job][1]
            else:
                temp = terms
            characteristic[grinder[job][0]] += temp
            
            if terms > len(grinder[job][2]):
                temp = len(grinder[job][2])-1
            else:
                temp = terms
            name_title = grinder[job][2][randint(1,temp)-1]
            
            # Add skills per terms
            for i in range(terms):
                add_skill(job, skill, 2)
            
            # NPC ages
            age += terms * 4
            
            # NPC could have crisis
            crisis = (age - 34) // 4
            if crisis > 0:
                for i in range(crisis):
                    temp = roll('1d3-1')
                    characteristic[characteristic_name[temp]] -= roll('1d3')
                    if characteristic[characteristic_name[temp]] < 1:
                        characteristic[characteristic_name[temp]] = 1
                    else:
                        add_skill(job, skill, 1)
            else:
                add_skill(job, skill, 1)
            
        return terms, age, name_title, job, skill
        
    # UPP Code Table

    hex_code = ['0', '1', '2', '3', '4', '5', '6',
                '7', '8', '9', 'A', 'B', 'C', 'D',
                'E', 'F', 'G', 'H', 'J', 'K',
                'L', 'M', 'N', 'P', 'Q', 'R',
                'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    
    noble_hex_code = ['0', '1', '2', '3', '4', '5', '6',
                      '7', '8', '9', 'A', 'B', 'c', 'C',
                      'D', 'e', 'E', 'f', 'F', 'G',
                      'G', 'H', 'H', 'H', 'H', 'H',
                      'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H']
    
    career = ['Agent', 'Army', 'Citizen', 'Drifter', 'Entertainer', 'Marines', 'Merchants', 'Navy', 'Nobility',
              'Rogue', 'Scholar', 'Scout']

    background_skills = ['Animals', 'Zero-G', 'Survival', 'Seafarer', 'Computers', 'Streetwise', 'Vacc Suit', 'Trade', 'Carouse']

    grinder = {               
               'Agent'      : ['INT', 3, ['Rookie', 'Agent', 'Field Agent', 'Field Agent', 'Special Agent', 'Assistant Director', 'Director'],
                              ['Admin', 'Holography', 'Writing', 'Carouse', 'Comms', 'Computers', 'Deception', 'Wheeled', 'Electronics', 'Explosives',
                               'Grav', 'Rotor', 'Wing', 'Gambler', 'Investigate', 'Unarmed Combat', 'Persuade', 'Motorboats',
                               'Streetwise', 'Slug Pistol', 'Energy Pistol', 'Vilani', 'Zdetl', 'Stealth', 'Recon']],
               'Army'       : ['STR', 4, ['Private', 'Lance Corporal', 'Corporal', 'Lance Sergeant', 'Sergeant', 'Gunnery Sergeant', 'Sergeant Major'],
                              ['Riding', 'Endurance', 'Explosives', 'Comms', 'Leadership', 'Mechanic', 'Medic',
                               'Remote Operations', 'Survival', 'Military Tactics', 'Tracked', 'Slug Rifle', 'Slug Pistol', 'Energy Rifle', 'Energy Pistol',
                               'Unarmed Combat', 'Recon', 'Man Portable Artillery']],
               'Citizen'    : ['EDU', 3, ['Citizen', 'Citizen', 'Technician', 'Technician', 'Craftsman', 'Craftsman', 'Master Technician'],
                              ['Advocate', 'Holography', 'Broker', 'Computers', 'Wheeled', 'Grav', 'Gambler', 'Slug Pistol', 'Anglic', 'Vilani', 'Steward',
                               'Streetwise', 'Trade', 'Veterinary', 'Civil Engineering', 'Space Construction', 'Navigation', 'Hydroponics',
                               'Polymers', 'Belter', 'Mole', 'Mechanic', 'Vacc Suit', 'Zero-G', 'Jack of all Trades']],
               'Drifter'    : ['END', 3, ['Barbarian', 'Barbarian', 'Warrior', 'Warrior', 'Chieftain', 'Chieftain', 'Chieftain'],
                              ['Deception', 'Gambler', 'Jack of all Trades', 'Vilani', 'Melee', 'Recon', 'Streetwise', 'Slug Rifle', 'Slug Pistol',
                               'Survival', 'Riding', 'Training', 'Farming', 'Co-ordination', 'Endurance', 'Shotgun', 'Unarmed Combat',
                               'Blade', 'Bludgeon', 'Natural Weapons', 'Belter', 'Navigation', 'Wheeled', 'Grav', 'Motorboats']],
               'Entertainer': ['SOC', 5, ['Extra', 'Extra', 'Extra', 'Extra', 'Extra', 'Extra', 'Famous Performer'],
                              ['Co-ordination', 'Carouse', 'Steward', 'Riding', 'Acting', 'Writing', 'Dance', 'Streetwise',
                               'Instrument', 'Wheeled', 'Wing', 'Vilani', 'Holography', 'Persuade', 'Deception']],
               'Marines'    : ['STR', 4, ['Marine', 'Lance Corporal', 'Corporal', 'Lance Sergeant', 'Sergeant', 'Gunnery Sergeant', 'Sergeant Major'],
                              ['Battle Dress', 'Explosives', 'Recon', 'Remote Operations', 'Sensors', 'Survival',
                               'Military Tactics', 'Strength', 'Flying', 'Mole', 'Rotor', 'Energy Rifle', 'Launchers', 'Field Artillery',
                               'Robotics', 'Military Tactics', 'Motorboats', 'Navigation']],
               'Merchants'  : ['INT', 3, ['Crewman', 'Senior Crewman', '4th Officer', '3rd Officer', '2nd Officer', '1st Officer', 'Captain'],
                              ['Admin', 'Broker', 'Carouse', 'Deception', 'Anglic', 'Vilani', 'Persuade', 'Steward', 'Streetwise', 'Economics',
                               'Sophontology', 'Small Craft', 'Spacecraft']],
               'Navy'       : ['SOC', 6, ['Crewman', 'Able Spacehand', 'Petty Officer 3rd Class', 'Petty Officer 2nd Class', 'Petty Officer 1st Class', 'Chief Petty Officer', 'Master Chief'],
                              ['Admin', 'Co-ordination', 'Astrogation', 'Comms', 'Computers', 'Diplomat',
                               'Wing', 'Anglic', 'Vilani', 'Leadership', 'Medic', 'Sensors', 'Stealth', 'Tactics', 'Vacc Suit',
                               'Zero-G', 'Maneuver Drive', 'Jump Drive', 'Electronics', 'Grav', 'Turrets', 'Ortillery', 'Screens',
                               'Capital Weapons', 'Unarmed Combat', 'Small Craft', 'Spacecraft', 'Capital Ships', 'Sail',
                               'Submarine', 'Naval Tactics', 'Blade', 'Ocean Ships']],
               'Nobility'   : ['SOC', 7, ['Wastrel', 'Wastrel', 'Ingrate', 'Ingrate', 'Black Sheep', 'Black Sheep', 'Scoundrel'],
                              ['Admin', 'Advocate', 'Art', 'Carouse', 'Deception', 'Diplomat', 'Wheeled', 'Rotor', 'Co-ordination', 'Gambler', 'Vilani', 'Persuade',
                               'Riding', 'Dance', 'Instrument', 'Sculpting', 'Slug Pistol', 'Blade', 'Small Craft',
                               'Archeology', 'Economics', 'History', 'Ocean Ships', 'Philosophy']],
               'Rogue'      : ['DEX', 4, ['Lackey', 'Henchman', 'Corporal', 'Sergeant', 'Lieutenant', 'Leader', 'Captain'],
                              ['Co-ordination', 'Art', 'Astrogation', 'Broker', 'Carouse', 'Comms', 'Computers', 'Deception', 'Diplomat', 'Drive', 'Explosives',
                               'Gambler', 'Leadership', 'Medic', 'Melee', 'Navigation', 'Persuade',
                               'Recon', 'Remote Operations', 'Motorboats', 'Submarine', 'Sensors', 'Stealth', 'Streetwise', 'Military Tactics', 'Vacc Suit',
                               'Riding', 'Co-ordination', 'Holography', 'Wheeled', 'Jump Drive', 'Grav', 'Slug Rifle', 'Slug Pistol',
                               'Shotgun', 'Unarmed Combat', 'Blade', 'Natural Weapons', 'Anglic', 'Vilani', 'Zdetl', 'Small Craft', 'Spacecraft',
                               'Cybernetics', 'Archeology', 'Economics', 'Robotics']],
               'Scholar'    : ['EDU', 3, ['', '', '', '', '', '', ''],
                              ['Astrogation', 'Computers', 'Medic', 'Veterinary',
                               'Holography', 'Writing', 'Maneuver Drive', 'Jump Drive', 'Electronics', 'Life Support', 'Power', 'Anglic', 'Vilani', 'Zdetl', 'Oynprith',
                               'Physics', 'Chemistry', 'Computer Science', 'Biology', 'Cybernetics', 'Genetics', 'Psionicology', 'Archeology', 'Economics', 'History', 'Linguistics',
                               'Philosophy', 'Psychology', 'Sophontology', 'Planetology', 'Robotics', 'Xenology', 'Biologicals', 'Hydroponics']],
               'Scout'      : ['END', 3, ['Trainee', 'Scout', 'Scout', 'Senior Scout', 'Senior Scout', 'Senior Scout', 'Senior Scout'],
                              ['Co-ordination', 'Astrogation', 'Comms', 'Computers', 'Diplomat', 'Drive', 'Grav',
                               'Life Sciences', 'Medic', 'Navigation', 'Sail', 'Sensors', 'Survival', 'Vacc Suit', 'Zero-G',
                               'Riding', 'Jump Drive', 'Life Support', 'Slug Rifle', 'Anglic', 'Vilani',
                               'Zdetl', 'Rotor', 'Small Craft', 'Spacecraft', 'Biology', 'Archeology', 'History', 'Sophontology',
                               'Linguistics', 'Planetology', 'Xenology']]               
              }
    
    social_standing_male = ['NOT USED','NOT USED','NOT USED','NOT USED','NOT USED','NOT USED',
                            'NOT USED','NOT USED','NOT USED','NOT USED','NOT USED',
                            'Sir','Baronet','Baron','Marquis','Viscount','Count','Duke','Duke',
                            'Archduke','Prince','Emperor',
                            'Emperor','Emperor','Emperor','Emperor','Emperor','Emperor',
                            'Emperor','Emperor','Emperor','Emperor','Emperor','Emperor']

    social_standing_female = ['NOT USED','NOT USED','NOT USED','NOT USED','NOT USED','NOT USED',
                              'NOT USED','NOT USED','NOT USED','NOT USED','NOT USED',
                              'Lady','Baronetess','Baroness','Marchioness','Viscountess','Countess','Duchess','Duchess',
                              'Archduchess','Princess','Empress',
                              'Empress','Empress','Empress','Empress','Empress','Empress',
                              'Empress','Empress','Empress','Empress','Empress','Empress']
    
    social_class = ['Outcast',
                    'Misfit',
                    'Dregs of Society',
                    'Lower Low',
                    'Middle Low',
                    'Upper Low',
                    'Low Middle',
                    'Middle',
                    'Upper Middle',
                    'Low Upper',
                    'Middle Upper',
                    'Upper Upper',
                    'Remarkable',
                    'Extraordinary',
                    'Extreme',
                    'Supreme']
    
    # Character Quirks

    quirks_table = [['Loyal', 'Distracted by other worries', 'In debt to criminals', 'Makes very bad jokes', 'Will betray characters', 'Aggressive'],
                    ['Has secret allies', 'Secret anagathic user', 'Looking for something', 'Helpful', 'Forgetful', 'Wants to hire the Travellers'],
                    ['Has useful contacts', 'Artistic', 'Easily confused', 'Unusually ugly', 'Worried about current situation', 'Shows pictures of his/her children'],
                    ['Rumor-monger', 'Unusually provincial', 'Drunkard or drug addict', 'Government informant', 'Mistakes a Traveller for someone else', 'Possesses unusually advanced technology'],
                    ['Unusually handsome or beautiful', 'Spying on the Travellers', 'Possesses TAS membership', 'Is secretly hostile towards the Travellers', 'Wants to borrow money', 'Is convinced the Travellers are dangerous'],
                    ['Involved in political intrigue', 'Has a dangerous secret', 'Wants to get off planet as soon as possible', 'Attracted to a Traveller', 'From offworld', 'Possesses telepathy or other unusual quality']]

    male = 'Male'
    female = 'Female'
    sex = ''
    
    # Characteristic Names
    
    characteristic_name = ['STR', 'DEX', 'END', 'INT', 'EDU', 'SOC']
    
    # Sound Tables

    V   = 1
    CV  = 2
    VC  = 3
    CVC = 4
    CC  = 5
    
    ic_sound = ['b','br','c','ch','d','g',
                     'h','j','k','l','m','p',
                     'r','s','st','sh',
                     't','v','w','z']
    ic_freq = [28,12,20,16,27,9,20,20,13,
                    28,24,27,24,30,13,25,
                    20,6,16,4]
    
    v_sound = ['a','e','i','o','u']
    v_freq = [16,20,10,7,3]

    mc_sound = ['g','lt','ns','nst','ls','ll','nn']
    mc_freq = [20,3,18,16,18,4,3]

    fc_sound = ['ch','ck','d','dy','dyne',
                     'hl','li','la','le','ler',
                     'nn','m','man','ma','mer','ny',
                     'me','n','nas','ne','ng',
                     'ner','nor','nie',
                     'rie','rlie','rly','rie','rt',
                     'ry','sa','sha','nshi','nski','son',
                     'nson','th','ta','ti','t','v',
                     'za','ue','than',
                     'lam','lis','lus','ton','tis','tus',
                     'love','se','nter','ll']
    fc_freq = [6,13,22,12,3,3,3,10,6,10,7,
                    25,10,4,13,12,5,27,11,4,14,13,17,7,6,5,5,6,3,
                    21,10,3,8,3,20,9,14,10,16,11,8,6,8,10,7,6,5,7,7,4,
                    4,12,5,4]
    
    for i in range(len(ic_sound)):
        log.debug(ic_sound[i] + ' ' + str(ic_freq[i]))
    
    for i in range(len(v_sound)):
        log.debug(v_sound[i] + ' ' + str(v_freq[i]))
        
    for i in range(len(mc_sound)):
        log.debug(mc_sound[i] + ' ' + str(mc_freq[i]))

    for i in range(len(fc_sound)):
        log.debug(fc_sound[i] + ' ' + str(fc_freq[i]))

    syllable_type = [V,V,V,V,V,V,V,V,VC,VC,VC,VC,CV,CV,CV,CV,CVC,CVC,CVC,CVC,CVC,CVC,CC,CC]
    
    ic_sounds = []
    for i in range(len(ic_freq)):
        for j in range(ic_freq[i]):
            ic_sounds.append(ic_sound[i])
    v_sounds = []
    for i in range(len(v_freq)):
        for j in range(v_freq[i]):
            v_sounds.append(v_sound[i])
    mc_sounds = []
    for i in range(len(mc_freq)):
        for j in range(mc_freq[i]):
            mc_sounds.append(mc_sound[i])
    fc_sounds = []
    for i in range(len(fc_freq)):
        for j in range(fc_freq[i]):
            fc_sounds.append(fc_sound[i])
    
    def check_number(num_npcs, fnum, snum):
        if num_npcs >= fnum and num_npcs <= snum:
            return True
        else:
            return False

# Set defalt generation values that can be changed as needed for input

    @get('/generate')
    def input_gen_variables():
        '''
        Variables needed for NPC generation are:
            Sex
            Number of NPCs to generate
            Characteristic roll type
        '''
        return '''<html>
<head>
<title>''' + __app__ + '''</title>
<link href='https://shawndriscollrpg.blogspot.com/favicon.ico' rel='icon' type='image/x-icon'/>
</head>
<body>
<br><br>
<h1>''' + __app__ + '''</h1>
<form action="/generate" method="post">
    <br>
    <label for="sex_chosen">Sex (Male, Female, Random):</label><br>
    <input type="text" name="sex_chosen" value="Random"><br><br>
    <label for="no_of_npcs">How many NPCs (1 - 199):</label><br>
    <input type="text" name="no_of_npcs" value="25"><br><br>
    <label for="roll_type">Characteristic Roll (2d6, Boon, 1d6+6, etc):</label><br>
    <input type="text" name="roll_type" value="2d6"><br><br>
    <input value="Generate" type="submit">
</form>
</body>
</html>'''

# Start NPC generation
    
    @post('/generate') # or @route('/generate', method='POST')
    def do_generation():   
        '''
        Get the form values from the web browser and begin NPC generation
        '''
        sex_chosen = request.forms.get('sex_chosen')
        no_of_npcs = request.forms.get('no_of_npcs')
        roll_type = request.forms.get('roll_type')

        if sex_chosen == '':
            sex_chosen = 'Random'
        if no_of_npcs == '':
            no_of_npcs = 1
        else:
            no_of_npcs = int(no_of_npcs)
        if roll_type == '':
            roll_type = '2d6'

        if check_number(no_of_npcs, 1, 199):
            if sex_chosen == 'Random':
                random_sex = True
            else:
                random_sex = False
        
            if sex_chosen in ['Random', 'Male', 'Female']:
            
                if not os.path.exists('data'):
                    os.mkdir('data')
        
                json_file_out = open('data/PyTravLITE_NPCs.json', 'w')
               
                # Start with a blank slate
                trav_rec = {}
                trav_rec['NPCs'] = []
                npc_list = '''<html>
<head>
'''
                if no_of_npcs > 1:
                    npc_list += '''<title>''' + str(no_of_npcs) + ''' NPCs Were'''
                else:
                    npc_list += '''<title>Only One NPC Was'''
                npc_list += ''' Generated</title>
<link href='https://shawndriscollrpg.blogspot.com/favicon.ico' rel='icon' type='image/x-icon'/>
</head>
<body>
<br>'''
                
                # NPC generation loop
                
                log.info('sex_chosen = ' + sex_chosen)
                log.info('no_of_npcs = ' + str(no_of_npcs))
                log.info('roll_type = ' + roll_type)
                
                if no_of_npcs > 1:
                    npc_list += '''
<table>
'''
                
                for i in range(no_of_npcs):
                    
                    # What are the six characteristics for this NPC?
                    
                    characteristic = {}
                    
                    #
                    # Create a dictionary for the NPC's characteristics.
                    # I could have used a list instead of a dict, but I
                    # wanted to learn how to do dict for a change.
                    #
                    
                    for key in characteristic_name:
                        
                        characteristic[key] = roll(roll_type) # entered in web browser
                        #characteristic[key] = roll('2d6') # normal two 6-sided roll
                        #characteristic[key] = roll('boon') # Method I roll
                        #characteristic[key] = roll('1d6+6') # Nexus roll
                    
                    # Generate NPC's name

                    sex = ''
                    #sex_chosen = 'Random'
                    while sex != sex_chosen:
                        first_name = gen_word(11)
                        last_name = gen_word(11)
                        middle_name = gen_word(11)
                        homeworld_name = gen_word(14)

                        if len(first_name) > len(last_name):
                            temp = first_name
                            first_name = last_name
                            last_name = temp

                        if first_name[len(first_name) - 1] == 'a' \
                               or first_name[len(first_name) - 3:len(first_name)] == 'nny' \
                               or first_name[len(first_name) - 2:len(first_name)] == 'ne' \
                               or first_name[len(first_name) - 2:len(first_name)] == 'se' \
                               or first_name[len(first_name) - 2:len(first_name)] == 'ie' \
                               or first_name[len(first_name) - 1] == 'i' \
                               or first_name[len(first_name) - 3:len(first_name)] == 'del' \
                               or first_name[len(first_name) - 2:len(first_name)] == 'ly' \
                               or first_name[len(first_name) - 2:len(first_name)] == 'll' \
                               or first_name[len(first_name) - 4:len(first_name)] == 'lynn' \
                               or first_name[len(first_name) - 2:len(first_name)] == 'le' \
                               or first_name[len(first_name) - 3:len(first_name)] == 'ndy' \
                               or first_name[0:2] == 'Gw' \
                               or first_name[0:2] == 'Qu':
                            sex = female
                        else:
                            sex = male
                        if random_sex:
                            sex_chosen = sex
                    
                    # Randomize the starting age of NPC
                    
                    age = 18 + roll('1D4') - roll('1D4')
                    
                    # Get their social class
                    
                    vp_soc = characteristic['SOC']
                    # print '[' + hex_code[characteristic['STR']] + \
                                # hex_code[characteristic['DEX']] + \
                                # hex_code[characteristic['END']] + \
                                # hex_code[characteristic['INT']] + \
                                # hex_code[characteristic['EDU']] + \
                                # noble_hex_code[characteristic['SOC']] + ']', age, social_class[vp_soc]
                    
                    # Grind the NPC down (age them)

                    terms, age, name_title, job, skill = grind(characteristic, age)

                    # Spit out their number of terms, their age, their title, job, and skills
                    
                    # Now make a full name for the NPC based on their life

                    if characteristic['SOC'] > 10:
                        if sex == male:
                            if characteristic['SOC'] > 11:
                                full_name = social_standing_male[characteristic['SOC']] + ' ' + first_name + ' ' + middle_name + ' ' + last_name + ' of ' + homeworld_name
                            else:
                                full_name = social_standing_male[characteristic['SOC']] + ' ' + first_name + ' ' + chr(randint(1,26) + 64) + '. ' + last_name
                        else:
                            if characteristic['SOC'] > 11:
                                full_name = social_standing_female[characteristic['SOC']] + ' ' + first_name + ' ' + middle_name + ' ' + last_name + ' of ' + homeworld_name
                            else:
                                full_name = social_standing_female[characteristic['SOC']] + ' ' + first_name + ' ' + chr(randint(1,26) + 64) + '. ' + last_name
                    else:
                        if name_title == '':
                            #if skill_level[27] == 3:
                            if characteristic['INT'] == 11:
                                full_name = 'Dr. ' + first_name + ' ' + last_name
                            #elif characteristic['EDU'] > 11 or skill_level[27] > 3:
                            elif characteristic['EDU'] > 11 or characteristic['INT'] > 11:
                                full_name = 'Dr. ' + first_name + ' ' + chr(randint(1,26) + 64) + '. ' + last_name
                            else:
                                full_name = first_name + ' ' + last_name
                        else:
                            full_name = name_title + ' ' + first_name + ' ' + chr(randint(1,26) + 64) + '. ' + last_name

                    if no_of_npcs > 1:
                        npc_list += '''<tr>
    <td>''' + '%s<br><br><br><br><br><br></td>' % ('{0:03d}'.format(i + 1))
                        npc_list += '''
    <td>'''
                    npc_list += full_name + ' [' + hex_code[characteristic['STR']] + \
                                                   hex_code[characteristic['DEX']] + \
                                                   hex_code[characteristic['END']] + \
                                                   hex_code[characteristic['INT']] + \
                                                   hex_code[characteristic['EDU']] + \
                                                   noble_hex_code[characteristic['SOC']] + ']<br>%s, age %d, %s class' % (sex, age, social_class[vp_soc])
                                                   
                    if terms > 0:
                        npc_list += ', %d-term %s' % (terms, job)
                        
                    npc_list += '<br>'
                    
                    trained_skills = {}
                    
                    # Sort skill list
                    skill_item = []
                    skill_amount = []
                    for i in range(80):
                        skill_item.append(-1)
                        skill_amount.append(-1)
                        
                    key_count = 0
                    for key in skill:
                        #print key, skill[key]
                        skill_item[key_count] = key
                        skill_amount[key_count] = skill[key]
                        key_count += 1
                    
                    key_count -= 1
                    swapping = True
                    while swapping:
                        swapping = False
                        for i in range(key_count):
                            if skill_item[i] > skill_item[i + 1]:
                                temp = skill_item[i]
                                skill_item[i] = skill_item[i + 1]
                                skill_item[i + 1] = temp
                                temp = skill_amount[i]
                                skill_amount[i] = skill_amount[i + 1]
                                skill_amount[i + 1] = temp
                                swapping = True
                    
                    key_count += 1
                    skill_count = 0
                    for i in range(key_count):
                        npc_list += '%s %d, ' % (skill_item[i], skill_amount[i])
                        
                        trained_skills[skill_item[i]] = skill_amount[i]
                        
                        skill_count += 1
                        if skill_count == 6 and i != key_count - 1:
                            npc_list += '<br>'
                            skill_count = 0
                    npc_list = npc_list[0:len(npc_list) - 2] + '<br>'

                    # Add Quirk
                    character_quirk = quirks_table[roll('d6-1')][roll('d6-1')]
                    npc_list += character_quirk + '<br><br><br>'

                    if no_of_npcs > 1:
                        npc_list += '''</td>
'''
                    if terms > 0:
                        temp_terms = terms
                    else:
                        temp_terms = 0

                    trav_rec['NPCs'].append({
                    'Traveller_Name': full_name,
                    'STR': hex_code[characteristic['STR']],
                    'DEX': hex_code[characteristic['DEX']],
                    'END': hex_code[characteristic['END']],
                    'INT': hex_code[characteristic['INT']],
                    'EDU': hex_code[characteristic['EDU']],
                    'SOC': noble_hex_code[characteristic['SOC']],
                    'Sex': sex,
                    'Age': age,
                    'Social_Class': social_class[vp_soc],
                    'Terms': temp_terms,
                    'Career': job,
                    'Skills': trained_skills,
                    'Quirk': character_quirk
                    })                
                    
                    log.info(full_name + ' was generated.')
                    
                #return "<p>It worked!</p>"
                if no_of_npcs > 1:
                    npc_list += '''</tr>
</table>'''
                npc_list += '''
</body>
</html>'''
                json.dump(trav_rec, json_file_out, ensure_ascii = True)
                
                json_file_out.close()
                
                return npc_list

            else:
                return "<p><br><br>Enter Sex. Not gender, please.</p>"
                                       
        else:
            return "<p><br><br>Enter a value of 1 to 199 NPCs, please.</p>"

    run(host='localhost', port='8080')

#
# Program exits here!
#


if __name__ == '__main__':
    
    log = logging.getLogger('PyTravLITE')
    log.setLevel(logging.DEBUG)

    if not os.path.exists('Logs'):
        os.mkdir('Logs')
    
    fh = logging.FileHandler('Logs/PyTravLITE.log', 'w')
 
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s - %(message)s',
                                  datefmt = '%a, %d %b %Y %H:%M:%S')
    fh.setFormatter(formatter)
    log.addHandler(fh)
    
    log.info('Logging started.')
    log.info(__app__ + ' starting...')
    print()
    print('Thank you for giving', __app__, 'a try.')
    vernum, release = roll('info')
    print('This program is using', release)
    print()
    print('----------------------------')
    print(__author__)
    print()
    
    log.info(__app__ + ' started, and running...')
    
    app()

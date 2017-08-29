#!/usr/bin/python3

#ARTCbot. Responds to ! commands 
#To do list:
#1 - Calendar integration? !upcoming <user> and !upcoming 
#2 - Training paces from popular books. Pfitz, JD, Hansons, Lore of Running.
#3 - Race predictor. Should be same as the age grading. Just parse that website.

import codecs
from datetime import datetime, timedelta
from math import exp

#Functions to read and write files into arrays.
def get_array(input_string):
    with open("textfiles/"+input_string+".txt","r") as f:
        input_array = f.readlines()
    input_array = [x.strip("\n") for x in input_array]
    return(input_array)

def write_out(input_string,input_array):
    with open("textfiles/"+input_string+".txt","w") as f:
        for i in input_array:
            f.write(i+"\n")
    return

#Fetching arrays
command_list = get_array("command_list")
last_edit = get_array("last_edit")
jd_paces = get_array("jd_paces")
pf_paces = get_array("pf_paces")
han_paces = get_array("han_paces")
#Defining built in commands
built_in = ["add","edit","delete","vdot","planner","pacing","splits","convertpace","convertdistance"]
#Need to do this better
temp_array=[]
for i in jd_paces:
    temp_array.append(i.split(','))
jd_paces = temp_array[1:]
temp_array=[]
for i in pf_paces:
    temp_array.append(i.split(','))
pf_paces = temp_array[1:]
temp_array=[]
for i in han_paces:
    temp_array.append(i.split(','))
han_paces = temp_array[1:]
#Defining VDOT ranges.
vdot_range=[30.0,85.0]

#Parsing distances and units
def parseDistance(orig):
    dist = 0
    unit = 'na'

    ary = orig.split()

    if (len(ary) == 1):
        m = re.match(r'([0-9.]+)([A-Za-z]+)', ary[0])
        if m:
            dist = float(m.group(1))
            unit = m.group(2)
    elif (len(ary) == 2):
        dist = float(ary[0])
        unit = ary[1]

    if (unit.startswith(('km', 'ki')) or unit == 'k'):
        unit = 'kilometer'
    elif (unit.startswith('mi')):
        unit = 'mile'

    return [dist, unit]

#Return date to start training
def planner(date,time):
    formatting = date.split('/')
    #Checking the date format
    if(len(formatting[0]) > 2 or len(formatting[1]) > 2 or len(formatting[2]) > 2):
        return "Your date is the wrong format. Please put your date in mm/dd/yy format."
    date = datetime.strptime(date, "%m/%d/%y")
    time_new = date - timedelta(weeks=int(time))
    return "For a "+time+" week plan, start training on "+str(time_new.month)+"/"+str(time_new.day)+"/"+str(time_new.year)+"."

#Get the time from a comment and return seconds
def get_time(time):
    time = time.split(':')
    if(len(time) < 3):
        return float(time[0])+float(time[1])/60.0
    elif(len(time) == 3):
        return float(time[0])*60.0+float(time[1])+float(time[2])/60.0

#Time formatting function. Time given in minutes as a float.
def time_format(time):
    minutes = int(time % 100)
    seconds = int((time % 1)*60)
    str_seconds = str(seconds)
    if(seconds < 10):
        str_seconds = "0"+str(seconds)
    return (minutes, str_seconds)
    
#Calculating VDOT
#Time given in minutes as a float, distance as a float in kilometers
def VDOT(time, distance):
    num = -4.6+0.182258*(distance*1e3/time)+0.000104*(distance*1e3/time)**2
    denom = 0.8+0.1894393*exp(-0.012778*time)+0.2989558*exp(-0.1932605*time)
    return round(num/denom,2)

#Conversion function
#Time in minutes as a float, distance as a float, unit as a string, inputs as a string, string is obvious.
def convert(time, distance, unit,inputs, string):
    if(unit == "miles" or unit == "m" or unit == "mile"):
        distance_conversion = str(round(distance*1.60934,1))
        time_conversion = time/1.60934
        minutes, str_seconds = time_format(time_conversion)
        time_sec = time*60.0
        split = int(400.0*time_sec/1609.0)
        split_perm = time_sec/(float(distance)*60.0)
        minutes_perm, str_seconds_perm = time_format(split_perm)
        split_perk = time_sec/(float(distance_conversion)*60.0)
        minutes_perk, str_seconds_perk = time_format(split_perk)
        v_dot = VDOT(time,float(distance_conversion))

        #Checking command
        if(string == "!convertdistance"):
            message = str(distance)+" miles is "+distance_conversion+" kilometers."
        if(string == "!convertpace"):
            message = "A "+inputs+" mile is a "+str(minutes)+":"+str_seconds+" kilometer."
        if(string == "!splits"):
            message = "For a "+inputs+" mile, run "+str(split)+" second 400s."
        if(string == "!pacing"):
            message = "To run "+str(distance)+" "+unit+" in "+inputs+" you need to run each mile in "+str(minutes_perm)+":"+str_seconds_perm+", or each kilometer in "+str(minutes_perk)+":"+str_seconds_perk+"."

    if(unit == "kilometers" or unit == "km" or unit == "kilometer"):
        distance_conversion = str(round(distance/1.60934,1))
        time_conversion = time*1.60934
        minutes, str_seconds = time_format(time_conversion)
        time_sec = time*60.0
        split = int(400.0*time_sec/1000.0)
        split_perk = time_sec/(float(distance)*60.0)
        minutes_perk, str_seconds_perk = time_format(split_perk)
        split_perm = time_sec/(float(distance_conversion)*60.0)
        minutes_perm, str_seconds_perm = time_format(split_perm)
        v_dot = VDOT(time,distance)

        #Checking command
        if(string == "!convertdistance"):
            message = str(distance)+" kilometers is "+distance_conversion+" miles."
        if(string == "!convertpace"):
            message = "A "+inputs+" kilometer is a "+str(minutes)+":"+str_seconds+" mile."
        if(string == "!splits"):
            message = "For a "+inputs+" kilometer, run "+str(split)+" second 400s."
        if(string == "!pacing"):
            message = "To run "+str(distance)+" "+unit+" in "+inputs+" you need to run each kilometer in "+str(minutes_perk)+":"+str_seconds_perk+", or each mile in "+str(minutes_perm)+":"+str_seconds_perm+"."
    
    if(string == "!vdot"):
        message = "A "+inputs+" "+str(distance)+" "+unit+" corresponds to a "+str(v_dot)+" VDOT."
    if(string == "!trainingpaces"):
        return v_dot


    return message 

#Add/Edit/Delete user commands function
def aed(comment_list,comment,author):
    #Adding commands
    if(comment_list.count("!add")):
        index = comment_list.index("!add")
        add_command = comment_list[index+1]

        #Searching if command already exists.
        if("!"+add_command in command_list):
            reply = ("The command !"+add_command+" already exists. Please try !edit instead.")
            return reply

        #Stopping people from overwriting built in commands
        if(add_command in built_in):
            reply = ("That command cannot be added as it's built into my programming. Please try a different name.")
            return reply

        #Taking the rest of the comment as the new command and stripping it downs
        new_command = comment.replace("!add","")
        new_command = new_command.replace(add_command,"",1)
        new_command = new_command.lstrip()
    
        #Stopping command responses that start with !
        if(add_command[0] == "!" or new_command[0] == "!"):
            reply = "That command cannot be added because it either has an extra ! in the command or the response starts with !\n\n The command is `!add new_command response."
            return reply

        #Human friendly version of the edit
        temp = new_command
        new_command = new_command.splitlines()
        #Doing fancy shit to make the commands work
        new_command = r'\n'.join(map(str, new_command))
        #Actually adding the command
        command_list.append("!"+add_command)
        command_list.append(new_command)
        last_edit.append(author)
        write_out('command_list',command_list) 
        write_out('last_edit',last_edit)
        reply = "Successfully added !"+add_command+"\n\n The new response is:\n\n"+temp
        return reply

    #Deleting commands
    elif(comment_list.count("!delete")):
        index = comment_list.index("!delete")
        delete_command = comment_list[index+1]
        command_index = command_list.index("!"+delete_command)
        #Actually deleting command
        del command_list[command_index]
        del command_list[command_index]
        del last_edit[int(command_index/2)]
        write_out('command_list',command_list)
        write_out('last_edit',last_edit)
        reply = "Successfully deleted !"+delete_command
        return reply

    elif(comment_list.count("!edit")):
        #Editing commands
        index = comment_list.index("!edit")
        edit_command = comment_list[index+1]
        #Taking the rest of the comment as the new command and stripping it down
        new_command = comment.replace("!edit","")
        new_command = new_command.replace(edit_command,"",1)
        new_command = new_command.lstrip()
        #Human friendly version of the edit
        temp = new_command
        new_command = new_command.splitlines()
        #Doing fancy shit to make the commands work
        new_command = r'\n'.join(map(str, new_command))
        #Making sure the command exists
        if("!"+edit_command not in command_list):
            reply = "That command does not exist. Try !add instead."
            return reply
            
        #Actually replacing the command
        command_index = command_list.index("!"+edit_command)
        #Easier to delete both old command and response and append the new ones
        del command_list[command_index] 
        del command_list[command_index]
        del last_edit[int(command_index/2)]
        command_list.append("!"+edit_command)
        command_list.append(new_command)
        last_edit.append(author)
        write_out('command_list',command_list)
        write_out('last_edit',last_edit)
        reply = "Successfully edited !"+edit_command+"\n\n The new response is:\n\n"+temp
        return reply

#Responding to help commands
def help(comment_list):
    #Having to convert back from raw string
    index = command_list.index("!help")
    reply = codecs.decode(command_list[index+1], 'unicode_escape')
    reply += "\n\n **Community made commands and quick links are (user who edited the command in parentheses):** \n\n"
    for i in range(0,len(command_list)-1,2):
        if(i != index and i < len(command_list)-2):
            reply += command_list[i]+" ("+last_edit[int(i/2)]+"), "
        elif(i != index): 
            reply += command_list[i]+" ("+last_edit[int(i/2)]+")"
    reply += "\n\n**I can reply to multiple commands at a time, so don't be picky.**"
    return reply

#Paces based on VDOT
#Needs to not be shit
def trainingpaces(comment_list):
    reply = ""
    indices = [i for i, x in enumerate(comment_list) if x == "!trainingpaces"]
    for i in indices:
        if(len(comment_list) > 2):
            if(comment_list[i+3] == 'miles' or comment_list[i+3] == 'kilometers' or comment_list[i+3] == 'mile' or comment_list[i+3] == 'kilometer' or comment_list[i+3] == 'm' or comment_list[i+3] == 'km'):
                time = get_time(comment_list[i+1])
                distance = float(comment_list[i+2])
                unit = comment_list[i+3].lower()
                v_dot = convert(time, distance, unit, comment_list[i+1], "!trainingpaces")
                reply += "\n\nA "+comment_list[i+1]+" "+str(distance)+" "+unit+" corresponds to a "+str(v_dot)+" VDOT."
                #Rounding
                v_dot = str(round(v_dot,0))
            else:
                v_dot = str(round(float(comment_list[i+1]),0))
            reply += "\n\n For a "+v_dot+" VDOT here are training paces from popular books."
            for j in range(0,len(jd_paces)-1,1):
                if(jd_paces[j][0]+'.0' == v_dot):
                    #Reddit table formatting
                    reply += "\n\n **Jack Daniels:**\n\nEasy/Long | Marathon | Tempo | Interval | Repetition"
                    reply += "\n -- | -- | -- | -- | --"
                    reply += "\n"+jd_paces[j][1]+"-"+jd_paces[j][2]+" | "+jd_paces[j][3]+" | "+jd_paces[j][4]+" | "+jd_paces[j][5]+" | "+jd_paces[j][6]
            for j in range(0,len(pf_paces)-1,1):
                if(pf_paces[j][0]+'.0' == v_dot):
                    reply += "\n\n **Pete Pfitzinger:**\n\nLong run | Long run (km) | LT | LT (km)  | VO2 (400) | Speed (300) | Speed (200)"
                    reply += "\n -- | -- | -- | -- | -- | -- | -- "
                    reply += "\n"+pf_paces[j][1]+"-"+pf_paces[j][2]+" | "+pf_paces[j][3]+"-"+pf_paces[j][4]+" | "+pf_paces[j][5]+" | "+pf_paces[j][6]+" | "+pf_paces[j][7]+" | "+pf_paces[j][8]+" | "+pf_paces[j][9]
            for j in range(0,len(han_paces)-1,1):
                if(han_paces[j][0]+'.0' == v_dot):
                    reply += "\n\n **Hanson's**\n\nRecovery | Easy | Long Run | Marathon | Strength | 10k | 5k"
                    reply += "\n -- | -- | -- | -- | -- | -- | --"
                    reply += "\n"+han_paces[j][1]+" | "+han_paces[j][2]+"-"+han_paces[j][3]+" | "+han_paces[j][4]+" | "+han_paces[j][5]+" | "+han_paces[j][6]+" | "+han_paces[j][7]+" | "+han_paces[j][8]
            if(float(v_dot) < min(vdot_range) or float(v_dot) > max(vdot_range)):
                reply += "\n\nThere are no listed training paces for a "+v_dot+" VDOT."
    return reply

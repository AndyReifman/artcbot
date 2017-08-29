#!/usr/bin/python3

#ARTCbot. Responds to ! commands 
#To do list:
#1 - Calendar integration? !upcoming <user> and !upcoming 
#2 - Age grading
#3 - Race prediction from vdot
#4 - New way to parse distance/unit
#5 - Make !trainingpaces not shit

import artcbot
import praw
import codecs
from config_bot import *

#Reddit stuff
r = praw.Reddit("ARTCbot 1.2.4 by herumph")
r.login(REDDIT_USERNAME, REDDIT_PASS)
subreddit = r.get_subreddit("RumphyBot")
#subreddit = r.get_subreddit("artc")
subreddit_comments = subreddit.get_comments()

#Fetching arrays
already_done = artcbot.get_array("already_done")
command_list = artcbot.get_array("command_list")

#Defining built in commands
built_in = ["add","edit","delete","vdot","planner","pacing","splits","convertpace","convertdistance","trainingpaces"]

print("\n * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * \n")

#Looking at comments
def main():
    for comment in subreddit_comments:
        reply=""
        if(comment.id not in already_done and str(comment.author) != "artcbot"):
            already_done.append(comment.id)
            #Making sure the already_done file doesn't get too big. 
            del already_done[0]
            artcbot.write_out("already_done",already_done)

            #Saving comment
            comment_list = str(comment.body)
            comment_list = comment_list.split()

            #Add/edit/delete
            if(comment.body.count("!add") or comment.body.count("!delete") or comment.body.count("!edit")):
                #Getting subreddit contributors
                contributors=[]
                for contributor in subreddit.get_contributors():
                    contributors.append(str(contributor))
        
                if(str(comment.author) not in contributors):
                    reply += "Sorry, you are not allowed to edit commands."
                    comment.reply(reply)
                    return
                else:
                    reply += artcbot.aed(comment_list,str(comment.body),str(comment.author))
                    comment.reply(reply)
                    return

            #Help
            if(comment.body.count("!help")):
                reply += artcbot.help(comment_list)
                comment.reply(reply)
                return

            #User commands
            common = list(set(comment_list).intersection(command_list))
            if(len(common) > 0 and common.count("!help") < 1):
                for i in range(0,len(common)):
                    command_index = command_list.index(common[i])
                    reply += "\n\n"+codecs.decode(command_list[command_index+1], 'unicode_escape')

            #Distance conversions
            if(comment.body.count("!convertdistance")):
                indices = [i for i, x in enumerate(comment_list) if x == "!convertdistance"]
                for i in indices:
                    unit = comment_list[i+2].lower()
                    distance = comment_list[i+1]
                    distance = float(distance)
                    reply += "\n\n"+artcbot.convert(1, distance, unit, 1,"!convertdistance")

            #Converting paces
            if(comment.body.count("!convertpace")):
                indices = [i for i, x in enumerate(comment_list) if x == "!convertpace"]
                for i in indices:
                    unit = comment_list[i+2].lower()
                    time = artcbot.get_time(comment_list[i+1])
                    reply += "\n\n"+artcbot.convert(time, 1, unit, comment_list[i+1], "!convertpace")

            #Track split calculator
            if(comment.body.count("!splits")):
                indices = [i for i, x in enumerate(comment_list) if x == "!splits"]
                for i in indices:
                    unit = comment_list[i+2].lower()
                    time = artcbot.get_time(comment_list[i+1])
                    reply += "\n\n"+artcbot.convert(time, 1, unit, comment_list[i+1], "!splits")

            #Training plan calculator
            if(comment.body.count("!planner")):
                indices = [i for i, x in enumerate(comment_list) if x == "!planner"]
                for i in indices:
                    reply += "\n\n"+artcbot.planner(comment_list[i+1],comment_list[i+2])

            #Race pace calculator
            if(comment.body.count("!pacing")):
                indices = [i for i, x in enumerate(comment_list) if x == "!pacing"]
                for i in indices:
                    time = artcbot.get_time(comment_list[i+1])
                    distance = float(comment_list[i+2])
                    unit = comment_list[i+3].lower()
                    reply += "\n\n"+artcbot.convert(time, distance, unit, comment_list[i+1], "!pacing")

            #VDOT calculator
            if(comment.body.count("!vdot")):
                indices = [i for i, x in enumerate(comment_list) if x == "!vdot"]
                for i in indices:
                    time = artcbot.get_time(comment_list[i+1])
                    distance = float(comment_list[i+2])
                    unit = comment_list[i+3].lower()
                    reply += "\n\n"+artcbot.convert(time, distance, unit, comment_list[i+1], "!vdot")

            if(comment.body.count("!trainingpaces")):
                reply += artcbot.trainingpaces(comment_list)

            #Responding if needed
            if(len(reply) > 1):
                comment.reply(reply)

main()

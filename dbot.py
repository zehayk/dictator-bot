# Copyright 2020, Hayk Petrosyan, All Rights Reserved
# https://discord.com/api/oauth2/authorize?client_id=753392788640366704&permissions=36702528&scope=bot
from __future__ import division

import discord
from discord import FFmpegPCMAudio
from discord.utils import get
import random
import gtts
import asyncio
import os
import shutil
from dotenv import load_dotenv
import datetime
import json
import sys
import operator

load_dotenv()
client = discord.Client()
words = {}
scoreboard = {}
# [str(msg.guild.id)]
TOKEN = os.getenv('DB_BOT_TOKEN')
# TOKEN = os.getenv('TESTING_BOT')
ffmpeg_options = {
    'options': '-vn'
}


async def forward_console_logs():
    await client.wait_until_ready()
    console_channel = client.get_channel(756566130767691863)  # (754878455887167581)

    while not client.is_closed():
        '''from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()

        # sys.stdout = await console_channel.send(sys.stdout)

        # from subprocess import Popen, PIPE
        # pipe = Popen("pwd", shell=True, stdout=PIPE).stdout
        # output = pipe.read()
        # await console_channel.send('ee' + output.decode("utf-8"))

        sys.stdout.mode ='r'
        sys.stdout = old_stdout
        await console_channel.send('ee' + str(sys.stdout.read()))
        # await console_channel.send('ee' + str(sys.stdout))'''
        import contextlib
        import io
        file = io.StringIO()
        with contextlib.redirect_stdout(file):
            print('a')
            print('b')
            print('c')
        await console_channel.send(f'{file.getvalue()!s}')




@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="db$help"))
    print(f'Bot "{client.user}" is ready!')
    # client.loop.create_task(forward_console_logs())

    now = datetime.datetime.now()
    curhour = now.strftime("%H")
    curmin = now.strftime("%M")
    restartschan = client.get_channel(int(os.getenv('RESTART_CHANNEL_ID')))

    file = open('dictating_program/configfile.json', 'r+')
    data = json.load(file)
    file.close()
    restart_message = ''
    if data['restart']['already_sent'] == 'false':
        restart_message = f"\n**`Restart Message:`** {data['restart']['message']}"
        data['restart']['already_sent'] = 'true'
        file.close()
        file = open("dictating_program/configfile.json", "w")
        json.dump(data, file)
        file.close()
        try:
            schoolrestartchannel = client.get_channel(int(os.getenv('SCHOOL_CHANNEL_ID')))
            await schoolrestartchannel.send(f'<@{client.user.id}> just restarted at `{curhour}:{curmin}`.{restart_message}')
        except:
            # print('eeeeee')
            data['restart']['already_sent'] = 'false'
            file = open("dictating_program/configfile.json", "w")
            json.dump(data, file)
            file.close()

    await restartschan.send(f'<@{client.user.id}> just restarted at `{curhour}:{curmin}`.{restart_message}')

    # await forward_console_logs()


async def clear_words(msg, words, channel):
    for word in words[str(msg.guild.id)]:
        # shutil.rmtree('sounds/')
        word = word.replace('\n', '')
        os.remove(f'dictating_program/sounds/{word}.mp3')

    words[str(msg.guild.id)].clear()

    await channel.send('Words cleared!')


async def pick_word(channel, msg):
    try:
        vchannel = msg.author.voice.channel
    except:
        await msg.channel.send("You are not connected to a voice channel")
        return
    while True:
        word = random.choice(list(words[str(msg.guild.id)].items()))
        mmm = str(word).split("'")
        word = mmm[1]
        if words[str(msg.guild.id)][word] == 'false':
            # playsound('sounds/' + word + '.mp3')
            words[str(msg.guild.id)][word] = 'true'
            break
    # print(word)
    voice = get(client.voice_clients, guild=msg.guild)
    if voice and voice.is_connected():
        await voice.move_to(vchannel)
    else:
        voice = await vchannel.connect()
    # source = FFmpegPCMAudio('text.mp3')
    player = voice.play(FFmpegPCMAudio(
        source=f"dictating_program/sounds/{word}.mp3"))
    # executable="ffmpeg/bin/ffmpeg.exe",

    await channel.send(f'||{word}||')
    return word


async def show_list(channel, msg):
    messagetosend = ''
    for word, stat in words[str(msg.guild.id)].items():
        messagetosend = f'{messagetosend}{word} => {stat} \n'
    if messagetosend != '':
        await channel.send(str(messagetosend))
    else:
        await channel.send('Word list is empty')


async def insert_word(msg, channel, messagelist):
    await channel.send('working...')
    message = ''
    words[str(msg.guild.id)] = {}
    for word in messagelist:
        print(f'[PROG] make_sound_files({word}.mp3) -> done!')
        words[str(msg.guild.id)][word] = 'false'
        # print(word)
        if not os.path.isdir('dictating_program/sounds/'):
            os.mkdir('dictating_program/sounds/')
        if os.path.exists('dictating_program/sounds/' + word + '.mp3'):
            pass
        else:
            tts = gtts.tts.gTTS(word)
            tts.save('dictating_program/sounds/' + word + '.mp3')
        message = message + f'{word}, '
        # await channel.send(f'inserted: "{word}"')
    # await channel.send('`done`')
    await channel.send(f'inserted: {message}')


async def pick_random_text(channel, msg):
    file = open('dictating_program/random_texts/text1.txt', encoding='utf-8')
    lines = file.readlines()
    text_count = int(len(lines)/2)
    selected_text = random.randint(1, text_count)
    return lines[(selected_text*2)-1], lines[(selected_text*2)-2]


@client.event
async def on_guild_join(guild):
    await client.get_channel(740234911159549992).send(f'{client.user} just joined '
                                                      f'another server! => {guild}')


@client.event
async def on_message(msg):
    content = msg.content
    channel = msg.channel
    if content == 'db$keep-bot-alive-ping':
        await channel.send("db$response-im_still_alive")
    if msg.content.startswith('db$greet'):
        def check(m):
            return m.content == 'hello' and m.channel == channel

        message = await client.wait_for('message', check=check)
        await channel.send('Hello {.author}!'.format(message))
    if content.startswith('db$help'):
        await channel.send('**- `insert`** -> inserts one or many words into word list\n'
                           '**- `startdictgame (start)`** -> will start a game\n'
                           '**- `endgame (end)`** -> ends game (disconnects from vc and clears words list)\n'
                           '**- `clearlist (clear)`** -> will reset the word list\n'
                           '**- `showlist (list)`** -> shows the list and its cycle status\n'
                           '**- `typingspeed (typing) {@another_person}`** -> gives you random text so you type and '
                           'will tell you your WPM '
                           '( you can also race with your friends :D )\n'
                           '**- `englishvocab (vocab) [start-end]`** -> dictate from the english vocab sheet'
                           '(ex: db$vocab 31-45 -> will add the words 31 to 45 to the dictating word list)\n'
                           '**- `showvocab`** -> will show the whole english vocab list added till now\n'
                           '`() => alias to the command`')

    if content.startswith('db$setrestartmessage'):
        if msg.author.id == 391692290382495746:
            file = open('dictating_program/configfile.json', 'r+')
            data = json.load(file)
            file.close()
            data['restart']['message'] = msg.content.replace('db$setrestartmessage ', '')
            data['already_sent'] = 'false'
            file = open("dictating_program/configfile.json", "w")
            json.dump(data, file)
            file.close()
        else:
            await channel.send('You do not have permission to do that.')

    if content.startswith('db$insert'):
        messagelist = msg.content.split()
        # print(messagelist)
        del messagelist[0]
        await insert_word(msg, channel, messagelist)

    if content.startswith('db$clearlist') or content.startswith('db$clear'):
        await clear_words(msg, words, channel)

    if content.startswith('db$showlist') or content.startswith('db$list'):
        await show_list(channel, msg)

    if content.startswith('db$endgame') or content.startswith('db$end'):
        await clear_words(msg, words, channel)
        voice = get(client.voice_clients, guild=msg.guild)
        await voice.disconnect()
        scores = ''
        for player, points in scoreboard[str(msg.guild.id)].items():
            scores = scores + f'<@{player}>: `{points}`\n'
        scoreboard[str(msg.guild.id)].clear()
        scores = '`Scoreboard:`\n' + scores
        await channel.send(scores)

    if content.startswith('db$startdictgame') or content.startswith('db$start'):
        # print(f'chanId dict: {words}')
        scoreboard[str(msg.guild.id)] = {}
        while True:
            if len(words[str(msg.guild.id)]) == 0:
                await channel.send('`[ERROR]` word list **empty**')
                return

            word = await pick_word(channel, msg)
            start_time = datetime.datetime.now()
            print(word)
            def check(m, word=word):
                return m.content.lower() == f'{word}' and m.channel == channel

            attempt = await client.wait_for('message', check=check)
            scorer = attempt.author.id
            end_time = datetime.datetime.now()
            attempt_duration = end_time - start_time
            await channel.send(f'Eyyyy! <@{attempt.author.id}> got it right! Time: `{attempt_duration}`')
            try:
                if scoreboard[str(msg.guild.id)][scorer]:
                    pass
            except:
                scoreboard[str(msg.guild.id)][scorer] = 0
            scoreboard[str(msg.guild.id)][scorer] += 1

            nb_words = len(words[str(msg.guild.id)])
            cntt = 0
            for word in words[str(msg.guild.id)]:
                if words[str(msg.guild.id)][word] == 'true':
                    cntt = cntt + 1
            if cntt == nb_words:
                for word in words[str(msg.guild.id)]:
                    words[str(msg.guild.id)][word] = 'false'
                await channel.send('cycle finished, resetting stats, starting cycle over')
                voice = get(client.voice_clients, guild=msg.guild)
                await voice.disconnect()
                scores = ''
                for player, points in scoreboard[str(msg.guild.id)].items():
                    scores = scores + f'<@{player}>: `{points}`\n'
                scores = '`Scoreboard:`\n' + scores

                await channel.send(scores)
                break
            await channel.send('Picking new word in 3 sec...')
            await asyncio.sleep(3)
        scoreboard[str(msg.guild.id)].clear()
        return

    if content.startswith('db$typingspeed') or content.startswith('db$typing'):
        # list_players = msg.mentions
        print(msg.author)
        print(msg.author.id)
        print(msg.mentions)
        print(len(msg.mentions))
        # msg.mentions = msg.mentions.append(msg.author)
        '''players_id = []
        for i in range(len(msg.mentions)):
            players_id.append(msg.mention[i].id)
        players_id.append(msg.author)'''
        # list_players.append(msg.author)
        quote, author = await pick_random_text(channel, msg)
        quote = quote.split('\n')
        quote = quote[0]
        # quote = 'my name is jeff'

        quote_words = quote.split()
        # command_ran_time = datetime.datetime.now()
        player_wpm = {}
        player_acc = {}
        for i in range(len(msg.mentions)):
            id = msg.mentions[0].id
            player_wpm[id] = None
            # player_wpm[list_players.id]['status'] = ''

        people = ''
        for person in player_wpm:
            people = people + f', <@{person}>'
        await channel.send(f'<@{msg.author.id}>, {people}\n{author}\n{quote}\n**`This timeouts in 5min`**')
        time_start = datetime.datetime.now()
        player_wpm[msg.author.id] = None
        everybody_done = ''
        while everybody_done != 'done':
            # print('ee ee ee')
            def check(author):
                def inner_check(message):
                    if message.author != author:
                        return False

                    try:
                        int(message.content)
                        return True
                    except ValueError:
                        return False
                return inner_check

            while True:
                message = await client.wait_for('message', check=check, timeout=300)
                if message.author.id in player_wpm:
                    # print(player_wpm)
                    if player_wpm[message.author.id] is None:
                        break
            # print('gotteeeem message')
            stop_time = datetime.datetime.now()
            total_time = (stop_time - time_start).total_seconds()
            wordin = message.content.split()
            correct_word_count = 0  # len(quote_words)
            '''for i in range(len(quote_words)):
                try:
                    mywordin = wordin[i]
                    myquote_words = quote_words[i]
                except:
                    break
                if mywordin == myquote_words:
                    correct_word_count = correct_word_count + 1
                else:
                    pass'''
            for word in quote_words:
                if word in wordin:
                    correct_word_count = correct_word_count + 1
            wpm = (correct_word_count * 60) / total_time
            accuracy = (correct_word_count / float(len(quote_words))) * 100
            await channel.send(f'<@{message.author.id}>\n'
                               f'Words Per Minute: **`{wpm}`WPM**\n'
                               f'Accuracy: **`{accuracy}` %**\n'
                               f'Total Time: **`{total_time}` sec**\n'
                               f'```Correctly typed words: {correct_word_count}\n'
                               f'Total word count: {len(quote_words)}```\n')
            # player_wpm[message.author.id]['status'] = 'done'
            player_wpm[message.author.id] = wpm
            player_acc[message.author.id] = accuracy
            # player_wpm[message.author.id]['accuracy'] = accuracy
            '''for player in player_wpm:
                if player_wpm[player] == None:
                    break
                print('written done')
                everybody_done = "done"'''
            donelist = []
            for player in player_wpm:
                if player_wpm[player] is not None:
                    donelist.append(player)
            if len(donelist) == len(player_wpm):
                break
        # stats = {'a': 1000, 'b': 3000, 'c': 100}
        # print(player_wpm)
        max_wpm = max(player_wpm.values())  # maximum value
        max_keys = [k for k, v in player_wpm.items() if v == max_wpm]  # getting all keys containing the `maximum`

        if len(max_keys) > 1:
            max_key_two = {}
            for winn in max_keys:
                accc = player_acc[winn]
                max_key_two[winn] = accc
            max_acc = max(max_key_two.values())  # maximum value
            winners = [k for k, v in max_key_two.items() if v == max_acc]  # getting all keys containing the `maximum`
            if len(winners) > 1:
                lethem = ''
                for person in winners:
                    lethem = f'{lethem} <@{person}>'
                await channel.send(f'WOW it\'s a tie! {lethem} had the same WPM AND ACCURACY!!')
            else:
                await channel.send(f'<@{winners}> is the winner since he had a better accuracy.')

        else:
            # print(max_wpm, max_keys)
            # winner = max(player_wpm.items(), key=operator.itemgetter(1))[0]
            if len(player_wpm) > 1:
                await channel.send(f'Winner is <@{max_keys[0]}>!')

    if content.startswith('db$englishvocab') or content.startswith('db$vocab'):
        await channel.send('working...')
        command = content.split()
        try:
            wordrange = command[1].split('-')
        except:
            await channel.send('`[ERROR]` - Please specify range of words (ex: 16-30)')
            return
        word_listt = []
        vocabfile = open('dictating_program/english_vocabs.txt', 'r')
        lines = vocabfile.readlines()
        vocabfile.close()

        try:
            strt = int(wordrange[0])
            end = int(wordrange[1])
            for i in range(len(lines)):
                # print(i)
                if strt <= i+1 <= end:
                    word_listt.append(lines[i].strip('\n'))
            await insert_word(msg, channel, word_listt)
        except:
            await channel.send('`[ERROR]` Invalid word range.')
            return

    if content.startswith('db$showvocab'):
        vocabfile = open('dictating_program/english_vocabs.txt', 'r')
        lines = vocabfile.readlines()
        vocabfile.close()
        message = ''
        for i in range(len(lines)):
            message = f'{message}`{i+1}.` {lines[i]}'
        await channel.send(f'English vocab list: \n{message}')

    if msg.content.startswith('db$getguilds'):
        if msg.author.id == 391692290382495746:
            for guild in client.guilds:
                await msg.channel.send(guild.name)

# client.loop.create_task(forward_console_logs())

client.run(TOKEN)

# -*- coding: utf-8 -*-
import json
from wordcloud import WordCloud,STOPWORDS,ImageColorGenerator
import pandas
import matplotlib
import matplotlib.pyplot as plt
import ftfy
from scipy.ndimage import gaussian_gradient_magnitude
import numpy as np
from PIL import Image
import unicodedata
json_raw = None
FILE_PATH = "./message_1.json"
remove_list = ["?","!",",",".",";",":","\"","+","-","_","(",")","{","}","<",">","[","]"]
TOP_N = 20
matplotlib.rc('font',family='sans-serif')
unprocessed_text = ""
with open(FILE_PATH,encoding='utf-8') as f:
    json_raw = json.load(f)


messages = json_raw["messages"]
participants = []
for j in json_raw["participants"]:
    participants.append(j["name"])#ftfy.fix_encoding(j["name"]))#we have to force names to ascii otherwise it breaks set...
texts = {}
# print(participants)
participant_reactions={}
for j in participants:
    texts[j]=""
    participant_reactions[j]={}


for message in messages:
    try:
        texts[message['sender_name']] += ftfy.fix_encoding(message["content"])
        for react in message["reactions"]:
            if react["reaction"] in participant_reactions[react["actor"]]:
                participant_reactions[react["actor"]][react["reaction"]] += 1
            else:
                participant_reactions[react["actor"]][react["reaction"]] = 1
    except KeyError:#seems to happen for photo messages only
        continue
        # print("Failed on message:")
        # print(message)
        # print("=====")


output_text = ""
for j in participants: #for now combine all the text into one string 
    for symbol in remove_list: #Remove all prohibited symbols
        texts[j] = texts[j].replace(symbol,"")
    output_text += " " + texts[j]

stop = set(STOPWORDS) #Add a few clutter words to the removal set
additional_stops = ["I'm","I'll","I","I've",'',"-","2","itâ\x80\x99s","Iâ\x80\x99m","thatâ\x80\x99s"]
for j in additional_stops:
    stop.add(j)

colour_image = np.array(Image.open("./mask.jpg"))
colour_image[colour_image.sum(axis=2)==0] = 255
edges = np.mean([gaussian_gradient_magnitude(colour_image[:, :, i] / 255., 2) for i in range(3)], axis=0)
colour_image[edges > .08] = 255

wc = WordCloud(max_words=2500,stopwords=stop,mask=colour_image).generate(output_text) #Make a wordcloud with the custom stoplist
wc.recolor(color_func = ImageColorGenerator(colour_image))
plt.axis("off")
plt.imshow(wc, interpolation="bilinear")
plt.title("WW35 Group Chat word cloud")
plt.savefig("./wordcloud.png",bbox_inches='tight')

#Further frequency plotting.
wordsets = {} #dictionary of people, each item containing a dictionary of word:frequency
for name in participants:
    wordsets[name] = {}
    for word in texts[name].split(" "):
        if word not in stop: #ignore words on the stoplist
            if word not in wordsets[name]:
                wordsets[name][word]=1
            else:
                wordsets[name][word]+=1
fig,ax= plt.subplots()
width=0.7

popular_words = set()
for name in participants:
    person_words,person_word_freqs = zip(* sorted(wordsets[name].items(),key=lambda kv: kv[1],reverse=True)[:TOP_N])
    # print(person_words)
    popular_words.update(person_words)
bottom_words = {}
for i in popular_words:
    bottom_words[i] = 0
for name in participants:
    person_words,person_word_freqs = zip(*filter(lambda kv:kv[0] in popular_words,wordsets[name].items()))
    bottom_arr = []
    for i in person_words:
        bottom_arr.append(bottom_words[i])
    ax.bar(person_words,person_word_freqs,width,label=ftfy.fix_encoding(name),bottom=bottom_arr)
    for i,f in zip(person_words,person_word_freqs):
        bottom_words[i]+=f
plt.xticks(rotation=90)
ax.legend()
plt.title("Top {0} words per speaker".format(TOP_N))
plt.gcf().set_size_inches(20,10)
plt.savefig("./top_{0}_words_per_speaker.png".format(TOP_N),bbox_inches='tight')

# per speaker plots as requested
for name in participants:
    plt.figure()
    person_words,person_word_freqs = zip(* sorted(wordsets[name].items(),key=lambda kv: kv[1],reverse=True)[:TOP_N])
    # print(person_words)
    plt.bar(person_words,person_word_freqs,width,label=name)
    plt.title("Top {0} words for {1}".format(TOP_N,ftfy.fix_encoding(name)))
    plt.xticks(rotation=90)
    plt.savefig("./{0}.png".format(name.replace(" ","_")),bbox_inches='tight')

fig,ax= plt.subplots()
width=0.7
WRAP_LENGTH=15
bottom_height = {}
for name in participants:
    react,freq = zip(*participant_reactions[name].items())
    
    fixed_reacts = []
    for i in react:
        # print(i)
        fixed_react= unicodedata.name(ftfy.fix_encoding(i))
        while np.max([len(segment) for segment in fixed_react.split("\n")]) > WRAP_LENGTH:
            segmented = fixed_react.split("\n")
            fixed_react = ''.join([j + '\n' for j in segmented[:-1]]) + segmented[-1][0:WRAP_LENGTH]+"\n"+segmented[-1][WRAP_LENGTH:]
        fixed_reacts.append(fixed_react)
    # print(name,freq)
    bottom_arr = []
    for r in fixed_reacts:
        if r in bottom_height:
            bottom_arr.append(bottom_height[r])
        else:
            bottom_arr.append(0)
    ax.bar(fixed_reacts,freq,width,label=ftfy.fix_encoding(name),bottom=bottom_arr)
    for r,f in zip(fixed_reacts,freq):
        if r not in bottom_height:
            bottom_height[r] = f
        else:
            bottom_height[r]+=f

    
# plt.xticks(rotation=45)
ax.legend()
plt.title("Reactions".format(TOP_N))
plt.gcf().set_size_inches(20,8)
plt.savefig("./reactions.png".format(TOP_N),bbox_inches='tight')

plt.show()
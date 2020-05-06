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
print(participants)
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

# wc = WordCloud(max_words=2500,stopwords=stop,mask=colour_image).generate(output_text) #Print a wordcloud with the custom stoplist
# wc.recolor(color_func = ImageColorGenerator(colour_image))
# plt.axis("off")
# plt.imshow(wc, interpolation="bilinear")
# plt.title("WW35 Group Chat word cloud")
# plt.savefig("./wordcloud.png",bbox_inches='tight')

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
    print(person_words)
    popular_words.update(person_words)
    ax.bar(person_words,person_word_freqs,width,label=ftfy.fix_encoding(name))
plt.xticks(rotation=90)
ax.legend()
plt.title("Top {0} words per speaker".format(TOP_N))
plt.gcf().set_size_inches(20,10)
plt.savefig("./top_{0}_words_per_speaker.png".format(TOP_N),bbox_inches='tight')

# per speaker plots as requested
for name in participants:
    plt.figure()
    person_words,person_word_freqs = zip(* sorted(wordsets[name].items(),key=lambda kv: kv[1],reverse=True)[:TOP_N])
    print(person_words)
    plt.bar(person_words,person_word_freqs,width,label=name)
    plt.title("Top {0} words for {1}".format(TOP_N,ftfy.fix_encoding(name)))
    plt.xticks(rotation=90)
    plt.savefig("./{0}.png".format(name.replace(" ","_")),bbox_inches='tight')

fig,ax= plt.subplots()
width=0.7
for name in participants:
    react,freq = zip(*participant_reactions[name].items())
    fixed_reacts = []
    for i in react:
    #     print(i)
        fixed_reacts = unicodedata.name(ftfy.fix_encoding(i))
    # print(react)
    ax.bar(react,freq,width,label=ftfy.fix_encoding(name))
# plt.xticks(rotation=90)
ax.legend()
plt.title("Reactions".format(TOP_N))
plt.gcf().set_size_inches(20,10)
plt.savefig("./reactions.png".format(TOP_N),bbox_inches='tight')

plt.show()
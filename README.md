# Plotting data from Facebook

As required under GDPR, Facebook lets you download all the data they hold on you. This could be more than you think.... In my case, so far I have only downloaded messages, with "low quality" media. This came to around 2GB. 

Data download is currently (May 2020) available from Settings->Your Facebook Information->Download Your Information. For ease of computational processing, I chose JSON output; an HTML option is given but I have not experimented with it yet. 

I encountered a few issues with parsing the unicode characters used correctly; there are various bodges to handle this which may get neatened up if I ever improve this script (or receive a PR...). One area which is still not dealt with entirely neatly is "Reacts", which use unicode characters and in this script are named using the Python module `unicodedata`. This was the only serious issue with parsing the file using the Python `json` module. 

## Plots produced
1. `wordcloud` is used to generate a word cloud of the data. This is currently generated using code along the lines of [this example](https://amueller.github.io/word_cloud/auto_examples/parrot.html). In my case, since the data analysed was from a college-related group chat, I chose a photograph of [Emmanuel College](www.emma.cam.ac.uk) as the mask. I tweaked the saturation and contrast in GIMP to allow the edge detection a better chance; with about 2500 words, the outline of the Chapel became relatively clear. You will need to adjust the word count depending on the complexity of your image; note that an increased word count comes at a cost of fitting time, and the 2500 word version takes maybe 20-30s to run on my machine. 

1. The top `TOP_N` most sent words from each author are collated into a single set; the number of times each author has sent a word in the set is then graphed in a stacked bar chart using `matplotlib`. TODO: improve the stacking algorithm. I skimmed the docs for `ax.bar` and misread it badly, thinking that I could get away with simply calling it repeatedly; in fact, one must specify the bottom for each bar plot. This is currently worked around rather messily, and a neater implementation is certainly possible using `numpy`. That said, it runs in almost no time, so it's not that high up the list...

1. The top `TOP_N` words from each author are plotted on a single figure per author. 

1. The reactions made by each 'actor' (in the Facebook JSON parlance) to all messages are collated and plotted on a single graph. Currently I print the names of the Unicode character as the x-axis label; this is a bit of a shortcoming and I think it should be possible to render the Unicode emoji properly using a suitable font--the names are not exactly snappy, for example "SMILING FACE WITH OPEN MOUTH AND TIGHTLY-CLOSED EYES"!




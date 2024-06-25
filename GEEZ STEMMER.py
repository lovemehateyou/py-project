import normalization as norm
import stop_word as stop
import stmmer as stem

word_dic = {}
PUNC = ["።","፤","።"] 
num = ["፪","፫","፬","፭","ዕፀ","፮","፯","፰","፱",""]
with open('fname.txt', 'r',encoding= "utf-8") as f:
    for line in f:
        words = line.lower().split(" ")
        for word in words:
            if word in num:
                words.remove(word)
            else:
                if word:
                    if word[-1] not in PUNC :
                        if word  in word_dic:
                            word_dic[word] += 1
                        else:
                            word_dic[word] = 1
                    else:
                        if word  in word_dic:
                            word_dic[word[:-1]] += 1
                        else:
                            word_dic[word[:-1]] = 1

sorted_dict_values = dict(sorted(word_dic.items(), key=lambda item: item[1],reverse= True)) 


normal =norm.convert_to_root(sorted_dict_values)
stoped = stop.remove_stop_words(normal)
stemmed = stem.geez_stemmer(stoped)
for key, value in stemmed.items():
    print(key,value)







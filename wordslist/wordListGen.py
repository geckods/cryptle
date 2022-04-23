import random

import wordfreq

def sortFunc(myTuple):
    return myTuple[1]

if __name__ == "__main__":

    with open("/usr/share/dict/words", "r") as f:
        all_words = [x.strip() for x in f.readlines()]

    raw_words_list = [x for x in all_words if len(x) == 5 and x.islower()]

    words_with_frequency = [(word, wordfreq.zipf_frequency(word,'en')) for word in raw_words_list]

    words_with_frequency.sort(key=sortFunc, reverse=True)

    words_with_non_zero_frequency = [x for x in words_with_frequency if x[1] > 0.0]

    mini_list_1 = [x[0].upper() for x in words_with_non_zero_frequency[:700]]

    list_1 = [x[0].upper() for x in words_with_non_zero_frequency[:1400]]
    list_2 = [x[0].upper() for x in words_with_non_zero_frequency[1400:2800]]
    list_3 = [x[0].upper() for x in words_with_non_zero_frequency[2800:4200]]
    list_4 = [x[0].upper() for x in words_with_non_zero_frequency[4200:]]

    random.seed(420)

    random.shuffle(list_1)
    random.shuffle(list_2)
    random.shuffle(list_3)
    random.shuffle(list_4)

    print(list_1)
    print(list_2)
    print(list_3)
    print(list_4)

    random.shuffle(mini_list_1)
    print(mini_list_1)

    # with open("list_1.txt", 'w') as f:
    #     for word in list_1:
    #         f.write(word)
    #         f.write("\n")
    #
    # with open("list_2.txt", 'w') as f:
    #     for word in list_2:
    #         f.write(word)
    #         f.write("\n")
    #
    # with open("list_3.txt", 'w') as f:
    #     for word in list_3:
    #         f.write(word)
    #         f.write("\n")
    #
    # with open("list_4.txt", 'w') as f:
    #     for word in list_4:
    #         f.write(word)
    #         f.write("\n")
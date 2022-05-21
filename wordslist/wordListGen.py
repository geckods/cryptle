import random
import wordfreq
import string

def sortFunc(myTuple):
    return myTuple[1]

if __name__ == "__main__":

    with open("/usr/share/dict/words", "r") as f:
        all_words = [x.strip() for x in f.readlines()]

    raw_words_list = [x for x in all_words if len(x) == 5 and x.islower() and all([y in string.ascii_lowercase for y in x])]

    words_with_frequency = [(word, wordfreq.zipf_frequency(word,'en')) for word in raw_words_list]

    words_with_frequency.sort(key=sortFunc, reverse=True)

    words_with_non_zero_frequency = [x for x in words_with_frequency if x[1] > 0.0]

    word_list = [x[0].upper() for x in words_with_non_zero_frequency]

    encoded_list_for_solidity = str(["bytes5(0x" + x.encode('utf-8').hex() + ")" for x in word_list] ).replace("'","")

    print(encoded_list_for_solidity)
    print(word_list)
    print(word_list[287])


    print(len(word_list))
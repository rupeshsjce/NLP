from math import log10, inf
import sys
import json

#
class Decoder():
    def __init__(self, model_file):  # STEP 1
        self.trans_emis, self.emis_inv = self.load_model(model_file)
        self.tags = list(self.trans_emis.keys())
        self.ow_tags = self.ow_tags(5)  # Set k open-world tags

    def load_model(self, model_file):  # called by __init__
        '''Load model from hmmmodel.txt
        model_file - path/to/hmmmodel.txt'''
        with open(model_file) as json_file:
            data = json.load(json_file)
            trans_emis = data['trans_emis']
            emis_inv = data['emis_inv']
        return trans_emis, emis_inv

    def ow_tags(self, k):  # called by __init__
        '''For all tags, infer tags with top k unique phrases as open-world, for unseen phrases.
        k - the number of desired open-world tags.'''
        tag_counts = []
        for tag in self.trans_emis.keys():
            if tag in ['$START', '$STOP']:
                continue
            count = self.trans_emis[tag]['count']
            #print(f'tag: {key} count: {count}')
            tag_counts.append([count, tag])
        t = sorted(tag_counts, key=lambda x: x[0])
        print("ow_tags : ", [count for count in t[-k:]])
        return [count[1] for count in t[-k:]]

    def decode(self, test_file):  # STEP 2:
        '''Load the test file, decode each sentence and output the sentence with the most likely tags
        using the hmm model.'''
        result = list()
        fd = open(test_file, 'r')
        count = 0

        while True:
            count += 1
            line = fd.readline().strip().split(' ')

            # if line is empty, end of file
            if line[0] == '':
                break

            line.append(' ')  # end state

            ### VITERBI ###
            # start :: first phrase
            t = 1
            phrase = line[0]
            prob_mat = {t: dict()}  # init prob_mat
            back_mat = {t: dict()}  # init back_mat
            print(prob_mat)
            print(back_mat)

            if phrase not in self.emis_inv:  # word completely unseen
                for tag1 in self.ow_tags:
                    a = log10(self.trans_emis["$START"]['next'][tag1]) - \
                        log10(self.trans_emis["$START"]['count'])
                    prob_mat[t][tag1] = a
                    back_mat[t][tag1] = '$START'
            else:  # word seen
                for tag1 in self.tags:
                    # word-tag pair unseen
                    if tag1 not in self.emis_inv[phrase]['tag_0']:
                        continue
                    else:  # word-tag pair seen
                        a = log10(
                            self.trans_emis["$START"]['next'][tag1]) - log10(self.trans_emis["$START"]['count'])
                        b = log10(
                            self.emis_inv[phrase]['tag_0'][tag1]) - log10(self.trans_emis[tag1]['count'])
                        prob_mat[t][tag1] = a + b
                        back_mat[t][tag1] = '$START'
            # end :: first phrase
            # start :: all subsequent phrases - recursion for remaining timestamps
            for t in range(1, len(line)):  # for each timestamp
                phrase = line[t]
                prob_mat[t+1] = dict()
                back_mat[t+1] = dict()

                if phrase not in self.emis_inv:  # word completely unseen
                    for tag1 in self.ow_tags:
                        max_prob_score = -inf
                        max_tag0 = None

                        for tag0 in prob_mat[t]:  # look at previous tags
                            prior = prob_mat[t][tag0]
                            a = log10(
                                self.trans_emis[tag0]['next'][tag1]) - log10(self.trans_emis[tag0]['count'])
                            prob_score = prior + a
                            if prob_score > max_prob_score:
                                max_prob_score = prob_score
                                max_tag0 = tag0

                        prob_mat[t+1][tag1] = max_prob_score
                        back_mat[t+1][tag1] = max_tag0

                else:  # word seen
                    for tag1 in self.tags:
                        # word-tag pair unseen
                        if tag1 not in self.emis_inv[phrase]['tag_0']:
                            continue
                        else:  # word-tag pair seen
                            max_prob_score = -inf
                            max_back_score = -inf
                            max_tag0 = None

                            for tag0 in prob_mat[t]:
                                prior = prob_mat[t][tag0]
                                a = log10(
                                    self.trans_emis[tag0]['next'][tag1]) - log10(self.trans_emis[tag0]['count'])
                                b = log10(
                                    self.emis_inv[phrase]['tag_0'][tag1]) - log10(self.trans_emis[tag1]['count'])

                                prob_score = prior + a + b
                                back_score = prior + a

                                if prob_score > max_prob_score:
                                    max_prob_score = prob_score
                                if back_score > max_back_score:
                                    max_back_score = back_score
                                    max_tag0 = tag0
                            prob_mat[t+1][tag1] = max_prob_score
                            back_mat[t+1][tag1] = max_tag0

                if phrase == ' ':  # timestamp of $STOP tag, non-phrase emitting
                    max_last_score = -inf
                    mlt = None
                    for tag0 in self.tags:
                        if tag0 in prob_mat[t]:
                            prior = prob_mat[t][tag0]
                            a = log10(self.trans_emis[tag0]['next']['$STOP'])
                            last_score = prior + a
                            if last_score > max_last_score:
                                max_last_score = last_score
                                mlt = tag0

                    prob_mat[t+1]['$STOP'] = max_last_score
                    back_mat[t+1]['$STOP'] = mlt

            # Follow all backpointers to create tag sequence
            state_seq = [mlt]
            for t in reversed(range(2, len(line))):
                mlt_next = back_mat[t][mlt]
                state_seq.insert(0, mlt_next)
                mlt = mlt_next
            line.pop()
            res = ' '.join([f'{phrase}/{tag}' for phrase,
                            tag in zip(line, state_seq)])
            result.append(res)
        return result

    def write_result(self, result):
        '''Write the result to outfile'''
        out_file = 'hmmoutput.txt'
        fd = open(out_file, "w")
        for line in result:
            # write line to output file
            fd.write(line)
            fd.write("\n")
        fd.close()


# PARAMETERS
base = 'hmm-training-data/'  # TODO: Remove hard-code
langs = ['it_isdt_', 'ja_gsd_']
file_types = ['dev_raw.txt', 'dev_tagged.txt', 'train_tagged.txt']
lang_files = {lang: [f'{lang}{file}' for file in file_types] for lang in langs}
model_file = 'hmmmodel.txt'

# DRIVER

# Pick one
#test_file = sys.argv[1]
test_file = base + lang_files['it_isdt_'][0]
# test_file = base + lang_files['ja_gsd_'][0]

decoder = Decoder(model_file)
result = decoder.decode(test_file)
print('Decoding complete. Writing... ')
decoder.write_result(result)

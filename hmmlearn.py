import json
import sys

#
def construct_model(train_doc):
    '''Build up the transition and emission matrix from the tagged training corpus.
    train_doc - a filepath to the training corpus.'''
    fd = open(train_doc, 'r')
    count = 0
    trans_emis_mat = dict()
    emis_mat_inv = dict()

    # while True and count < 1: #TODO: Hard-code, just look at first 2 lines
    run = 0
    while True:
        count += 1
        line = fd.readline().strip().split(' ')

        # if line is empty, end of file
        if line[0] == '':
            break

        line.insert(0, ' /$START')
        line.append(' /$STOP')
        # print(line)
        # print("*"*60)

        for idx, pair in enumerate(line): #
            # print(idx, pair)
            # get the next pair
            if idx < len(line)-1:
                next_pair = line[idx + 1]  # not last item
            else:
                next_pair = ' / '  # last item

            p_split = pair.split('/')
            # print("p_split :", p_split)

            tag_0 = p_split.pop()
            # print("tag_0 : ", tag_0)
            phrase = '/'.join(p_split)
            # print("phrase : ", phrase)
            tag_1 = next_pair.split('/')[-1]
            # print("tag_1 : ", tag_1)

            # ADD TO EMIS_MAT_INV
            if idx >= 1 and idx < len(line) - 1:  # Skip START and STOP tags
                if phrase not in emis_mat_inv:  # phrase not yet seen
                    emis_mat_inv[phrase] = {'count': 1, 'tag_0': {tag_0: 1}}
                else:  # phrase seen
                    emis_mat_inv[phrase]['count'] += 1
                    # tag not yet seen
                    if tag_0 not in emis_mat_inv[phrase]['tag_0']:
                        emis_mat_inv[phrase]['tag_0'][tag_0] = 1
                    else:  # tag already seen
                        emis_mat_inv[phrase]['tag_0'][tag_0] += 1

            # Add to the transition and emission matrixes
            if tag_0 not in trans_emis_mat:  # Tag not yet seen

                # NOT YET SEEN: Start and stop tags
                if phrase == ' ':  # START_TAG: First instance
                    trans_emis_mat[tag_0] = {
                        'count': 1, 'next': {tag_1: 1}, 'phrase': {}}
                    # print("trans_emis_mat START_TAG : ", trans_emis_mat)
                    if tag_1 == ' ':  # STOP_TAG: First instance
                        trans_emis_mat[tag_0] = {
                            'count': 1, 'next': {}, 'phrase': {}}
                        # print("trans_emis_mat STOP_TAG : ", trans_emis_mat)
                        continue
                    continue

                # AO_TAGS: First instance
                trans_emis_mat[tag_0] = {'count': 1, 'next': {
                    tag_1: 1, }, 'phrase': {phrase: 1}}

                # print("trans_emis_mat : ", trans_emis_mat)

            else:  # Tag already seen
                trans_emis_mat[tag_0]['count'] += 1

                # SEEN: Start and stop tags
                if phrase == ' ':
                    if tag_1 == ' ':
                        continue  # STOP_TAG: Don't add tag_1
                    # START_TAG: Add tag_1 to each tag_0
                    if tag_1 not in trans_emis_mat[tag_0]['next']:
                        trans_emis_mat[tag_0]['next'][tag_1] = 1
                    else:
                        trans_emis_mat[tag_0]['next'][tag_1] += 1
                    continue

                # AO_TAGS: Add tag_1 to each tag_0
                if tag_1 not in trans_emis_mat[tag_0]['next']:
                    trans_emis_mat[tag_0]['next'][tag_1] = 1
                else:
                    trans_emis_mat[tag_0]['next'][tag_1] += 1

                # AO_TAGS: Add phrase to each tag_0
                if phrase not in trans_emis_mat[tag_0]['phrase']:
                    trans_emis_mat[tag_0]['phrase'][phrase] = 1
                else:
                    trans_emis_mat[tag_0]['phrase'][phrase] += 1

                # print("trans_emis_mat else : ", trans_emis_mat)
        run = run + 1

    return trans_emis_mat, emis_mat_inv


def smooth(trans_emis_mat):
    '''For each tagkey in trans_emis_mat, if a childtag doesn't exist,
    add one and increase the parent tag's count'''
    tags = list(trans_emis_mat.keys())
    print(len(tags))
    for key in trans_emis_mat.keys():
        records_to_add = 0
        for tag in tags:
            if tag not in trans_emis_mat[key]['next']:
                trans_emis_mat[key]['next'][tag] = 1
                records_to_add += 1
        trans_emis_mat[key]['count'] += records_to_add


def write_model(trans_emis_mat, emis_mat_inv):
    '''Write the model to a json-style file'''
    output_file = 'hmmmodel.txt'
    model = {'trans_emis': trans_emis_mat, 'emis_inv': emis_mat_inv}
    data = json.dumps(model, ensure_ascii=False)
    fd = open(output_file, "w")
    fd.write(data)
    fd.close()


# PARAMETERS
base = 'hmm-training-data/'  # TODO: Remove hard-code
langs = ['it_isdt_', 'ja_gsd_']
file_types = ['dev_raw.txt', 'dev_tagged.txt', 'train_tagged.txt']
lang_files = {lang: [f'{lang}{file}' for file in file_types] for lang in langs}


# Pick one
#train_doc = sys.argv[1]
train_doc = base + lang_files['it_isdt_'][2]
#train_doc = base + lang_files['ja_gsd_'][1]

# DRIVER
trans_emis_mat, emis_mat_inv = construct_model(train_doc)
smooth(trans_emis_mat)
write_model(trans_emis_mat, emis_mat_inv)

class Word(object):
    def __init__(self, word_vector, features, f_types):

        word_indices = []
        self.dict = {'word': 'n/a', 'prev$-$word': 'n/a', 'next$-$word': '', 'pos': 'n/a', 'prev$-$pos': 'n/a', 'next$-$pos': '', 'capitalized': 'n/a', 'location': 'n/a', 'abbrivation': 'n/a'}

        if 'CAP' in f_types:
            self.dict['capitalized'] = 'no'

        if 'LOCATION' in f_types:
            self.dict['location'] = 'no'

        if 'ABBR' in f_types:
            self.dict['abbrivation'] = 'no'

        if type(word_vector) == int:
            return

        for word_feature in word_vector.split():
            tokens = (word_feature.split(':'))
            if len(tokens) == 2:
                word_indices.append(features[int(tokens[0])])

        for feature in word_indices:
            tokens = feature.rsplit('$-$', 1)
            if len(tokens) == 1:
                self.dict[tokens[0]] = 'yes'
            else:
                self.dict[tokens[0]] = tokens[1]


    def toString(self):

        word_con = self.dict['prev$-$word'] + ' ' + self.dict['next$-$word']
        if self.dict['prev$-$word'] == 'n/a':
            word_con = 'n/a'

        pos_con = self.dict['prev$-$pos'] + ' ' + self.dict['next$-$pos']
        if self.dict['prev$-$pos'] == 'n/a':
            pos_con = 'n/a'

        return 'WORD: %s\nWORDCON: %s\nPOS: %s\nPOSCON: %s\nABBR: %s\nCAP: %s\nLOCATION: %s\n' % (self.dict['word'], word_con, self.dict['pos'], pos_con, self.dict['abbrivation'], self.dict['capitalized'], self.dict['location'])

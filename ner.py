import sys
from Word import Word

label_ints = {'O': 0, 'B-PER': 1, 'I-PER': 2, 'B-LOC': 3, 'I-LOC': 4, 'B-ORG': 5, 'I-ORG': 6}

def readLocs(file_path):
    locations = set()
    for line in open(file_path):
        locations.add(line.rstrip())

    return locations

def readTrain(file_path, f_types, training=False):
    features = set()
    features.add('word$-$UNK')

    if 'WORDCON' in f_types:
        features.add('prev$-$word$-$UNK')
        features.add('next$-$word$-$UNK')
    if 'POS' in f_types:
        features.add('pos$-$UNKPOS')
    if 'POSCON' in f_types:
        features.add('prev$-$pos$-$UNKPOS')
        features.add('next$-$pos$-$UNKPOS')

    prev_line = 'x PHIPOS PHI'
    current_line = ''
    next_line = ''

    lines = open(file_path).readlines()
    for i in range(0, len(lines)):
        current_line = lines[i]
        if i + 1 > len(lines) - 1 or len(lines[i + 1].rstrip()) == 0:
            next_line = 'x OMEGAPOS OMEGA'
        else:
            next_line = lines[i + 1]
        if len(current_line.rstrip()) == 0:
            # Starting a new sentence
            prev_line = 'x PHIPOS PHI'
            continue

        if 'WORD' in f_types or training:
            features.add('word$-$' + current_line.split()[2])
        if 'POS' in f_types:
            features.add('pos$-$' + current_line.split()[1])
        if 'WORDCON' in f_types:
            features.add('prev$-$word$-$' + current_line.split()[2])
            features.add('next$-$word$-$' + current_line.split()[2])
            features.add('prev$-$word$-$' + prev_line.split()[2])
            features.add('next$-$word$-$' + next_line.split()[2])
        if 'POSCON' in f_types:
            features.add('prev$-$pos$-$' + prev_line.split()[1])
            features.add('next$-$pos$-$' + next_line.split()[1])

        prev_line = current_line

    if 'CAP' in f_types:
        features.add('capitalized')
    if 'ABBR' in f_types:
        features.add('abbrivation')
    if 'LOCATION' in f_types:
        features.add('location')

    return features

def buildFeatureString(label, true_features):
    feature_string = label
    true_features.sort()

    for true_feature in true_features:
        feature_string = '%s %s:1' % (feature_string, true_feature)

    return feature_string

def inPattern(word, pattern):
    for i in range(0, len(word)):
        if word[i] not in pattern:
            return False

    return True

def vectorizeWords(file_path, features, locations, f_types):
    word_vectors = []

    prev_line = 'x PHIPOS PHI'
    current_line = ''
    next_line = ''

    lines = open(file_path).readlines()
    for i in range(0, len(lines)):
        true_features = []
        current_line = lines[i]
        current_line_tokens = current_line.rstrip().split()

        if i + 1 > len(lines) - 1 or len(lines[i + 1].rstrip()) == 0:
            next_line = 'x OMEGAPOS OMEGA'
        else:
            next_line = lines[i + 1]
        if len(current_line.rstrip()) == 0:
            # Starting a new sentence
            prev_line = 'x PHIPOS PHI'
            continue

        label = label_ints[current_line_tokens[0]]
        prev_line_tokens = prev_line.rstrip().split()
        next_line_tokens = next_line.rstrip().split()
        word = current_line_tokens[2]


        if 'word$-$' + word in features:
            index = features.index('word$-$' + word)
            true_features.append(index)
        else:
            index = features.index('word$-$UNK')
            true_features.append(index)

        if 'pos$-$' + current_line_tokens[1] in features:
            index = features.index('pos$-$' + current_line_tokens[1])
            true_features.append(index)
        elif 'POS' in f_types:
            index = features.index('pos$-$UNKPOS')
            true_features.append(index)

        if 'prev$-$word$-$' + prev_line_tokens[2] in features:
            index = features.index('prev$-$word$-$' + prev_line_tokens[2])
            true_features.append(index)
        elif 'WORDCON' in f_types:
            index = features.index('prev$-$word$-$UNK')
            true_features.append(index)


        if 'next$-$word$-$' + next_line_tokens[2] in features:
            index = features.index('next$-$word$-$' + next_line_tokens[2])
            true_features.append(index)
        elif 'WORDCON' in f_types:
            index = features.index('next$-$word$-$UNK')
            true_features.append(index)

        if 'prev$-$pos$-$' + prev_line_tokens[1] in features:
            index = features.index('prev$-$pos$-$' + prev_line_tokens[1])
            true_features.append(index)
        elif 'POSCON' in f_types:
            index = features.index('prev$-$pos$-$UNKPOS')
            true_features.append(index)

        if 'next$-$pos$-$' + next_line_tokens[1] in features:
            index = features.index('next$-$pos$-$' + next_line_tokens[1])
            true_features.append(index)
        elif 'POSCON' in f_types:
            index = features.index('next$-$pos$-$UNKPOS')
            true_features.append(index)

        if 'capitalized' in features and word[0].isupper():
            true_features.append(features.index('capitalized'))

        if 'location' in features and word in locations:
            true_features.append(features.index('location'))

        pattern = '.ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        if 'abbrivation' in features and word[-1] == '.' and len(word) <= 4 and inPattern(word, pattern):
            true_features.append(features.index('abbrivation'))

        word_vectors.append(buildFeatureString(label, true_features))
        prev_line = current_line

    return word_vectors

def buildWords(word_vectors, features, f_types):
    words = []
    for word_vector in word_vectors:
        word = Word(word_vector, features, f_types)
        words.append(word)

    return words

def writeFile(file_name, items):
    file = open(file_name,'w')
    for item in items:
        file.write("%s\n" % item)
    file.close()

def main():
    args = sys.argv
    train_file = args[1]
    test_file = args[2]
    locs_file = args[3]

    f_types = []
    for i in range(4, len(args)):
        f_types.append(args[i])

    locations = readLocs(locs_file)
    features = list(readTrain(train_file, f_types, True))
    features.insert(0, 'dummyOffset')
    word_vectors = vectorizeWords(train_file, features, locations, f_types)
    words = buildWords(word_vectors, features, f_types)

    writeFile('train.txt.vector', word_vectors)
    writeFile('train.txt.readable', [word.toString() for word in words])

    # Test file
    word_vectors = vectorizeWords(test_file, features, locations, f_types)
    words = buildWords(word_vectors, features, f_types)

    writeFile('test.txt.vector', word_vectors)
    writeFile('test.txt.readable', [word.toString() for word in words])


main()

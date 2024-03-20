import re

stringescapes = {}

a = 'C1'
b = 'C2'
v = 'D7'
g = 'C7'
d = 'C4'
e = 'C5'
zh = 'D6'
z = 'DA'
i = 'C9'
i_ = 'CA'
k = 'CB'
l = 'CC'
m = 'CD'
n = 'CE'
o = 'CF'
p = 'D0'
r = 'D2'
s = 'D3'
t = 'D4'
u = 'D5'
f = 'C6'
kh = 'C8'
ts = 'C3'
ch = 'DE'
sh = 'DB'
shch = 'DD'
quote = 'DF'
y = 'D9'
apostrophe = 'D8'
e_ = 'DC'
iu = 'C0'
ia = 'D1'


def mark_regions(word):
    pV = len(word)
    p2 = len(word)

    i = 0
    while i < len(word):
        if word[i:i + 2] in [a, b, v, g, d, e, zh, z, i, i_, k, l, m, n, o, p, r, s, t, u, f, kh, ts, ch, sh, shch,
                             quote, y, apostrophe, e_, iu, ia]:
            pV = i
            i += 2
            while i < len(word):
                if word[i:i + 2] not in [a, b, v, g, d, e, zh, z, i, i_, k, l, m, n, o, p, r, s, t, u, f, kh, ts, ch,
                                         sh, shch, quote, y, apostrophe, e_, iu, ia]:
                    p2 = i
                    break
                i += 2
        i += 2

    return pV, p2


def perfective_gerund(word):
    endings = [
        v,
        v + sh + i,
        v + sh + i + s + quote,
        a + y + v,
        ia + y + v,
        i + v,
        i + v + sh + i,
        i + v + sh + i + s + quote,
        y + v,
        y + v + sh + i,
        y + v + sh + i + s + quote
    ]

    for ending in endings:
        if word.endswith(ending):
            return True

    return False


def adjective(word):
    endings = [
        e + e, i + e, y + e, o + e, i + m + i, y + m + i,
        e + e_, i + e_, y + i_, o + i_, e + m, i + m,
        y + m, o + m, e + g + o, o + g + o, e + m + u,
        o + m + u, i + kh, y + kh, u + iu, iu + iu, a + ia,
        ia + ia, o + iu, e + iu
    ]

    for ending in endings:
        if word.endswith(ending):
            return True

    return False


def adjectival(word):
    endings = [
        e + m,
        n + n,
        v + sh,
        iu + shch, shch,
        i + v + sh, y + v + sh,
        i + v + shch, y + v + shch,
    ]

    for ending in endings:
        if word.endswith(ending):
            return True

    return False


def reflexive(word):
    endings = [
        s + ia,
        s + quote
    ]

    for ending in endings:
        if word.endswith(ending):
            return True

    return False


def is_verb(word):
    verb_patterns = [
        l + a, n + a, e + t + e, i_ + t + e, l + i, i_,
        l, e + m, n, l + o, n + o, e + t, iu + t,
        n + y, t + quote, e + sh + quote,
        n + n + o,
        '(' + a + '|' + ia + ')' + ' delete',
        i + l + a, y + l + a, e + n + a, e + i_ + t + e,
        u + i_ + t + e, i + t, i + l + i, y + l + i, e + i_,
        u + i_, i + l, y + l, i + m, y + m, e + n,
        i + l + o, y + l + o, e + n + o, ia + t, u + e + t,
        u + iu + t, i + t, y + t, e + n + y, i + t + quote,
        y + t + quote, i + sh + quote, u + iu, iu,
        'delete'
    ]
    verb_regex = '|'.join(verb_patterns)
    return re.match(verb_regex, word)


def is_noun(word):
    noun_patterns = [
        a, e + v, o + v, i + e, apostrophe + e, e,
           i + ia + m + i, ia + m + i, a + m + i, e + i, i + i,
        i, i + e + i_, e + i_, o + i_, i + i_, i_,
           i + ia + m, ia + m, i + e + m, e + m, a + m, o + m,
        o, u, a + kh, i + ia + kh, ia + kh, y, quote,
           i + iu, apostrophe + iu, iu, i + ia, apostrophe + ia, ia,
        'delete'
    ]
    noun_regex = '|'.join(noun_patterns)
    return re.match(noun_regex, word)


def is_derivational(word):
    derivational_patterns = [
        o + s + t,
        o + s + t + apostrophe,
        'delete'
    ]
    derivational_regex = '|'.join(derivational_patterns)
    return re.match(derivational_regex, word)


def tidy_up(word):
    tidy_up_patterns = [
        e_ + sh,
        e_ + sh + e,  # superlative forms
        'delete',
        '[' + n + ']' + n + ' delete'
    ]
    tidy_up_regex = '|'.join(tidy_up_patterns)
    return re.sub(tidy_up_regex, '', word)


def stem(word):
    perfective_gerund = False
    adjectival = False
    verb = is_verb(word)
    noun = is_noun(word)

    if verb or noun:
        word = re.sub(i, '', word)

    if verb:
        word = is_derivational(word)
        word = tidy_up(word)

    return word

print(stem("генералы"))
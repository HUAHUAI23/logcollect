import regex as re

# s = '<44>2022-10-14 19:13:57,163 - root - WARNING - sss'
types = {
    'WORD': r'\w+',
    'TEMP': r'.+',
    # todo: extend me
}
# PATTERN="%{TEMP:temp} - root - %{WORD:level} - %{WORD:message}"


def compile(pat):
    return re.sub(
        r'%{(\w+):(\w+)}',
        lambda m: "(?P<" + m.group(2) + ">" + types[m.group(1)] + ")", pat)

def outputtt(patterCompiled,reprStr):
    """
    docstring
    """
    return re.search(patterCompiled, reprStr).groupdict()
# rr=compile(PATTERN)
# print(rr)
# print(re.search(rr, s).groupdict())

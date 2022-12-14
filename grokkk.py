import regex as re

types = {
    'WORD': r'\w+',
    'TEMP': r'.+',
    # todo: extend me
}


def compile(pat):
    return re.sub(
        r'%{(\w+):(\w+)}',
        lambda m: "(?P<" + m.group(2) + ">" + types[m.group(1)] + ")", pat)

def outputtt(patterCompiled,reprStr):
    """
    docstring
    """
    return re.search(patterCompiled, reprStr).groupdict()
# Test
# s = '<44>2022-10-14 19:13:57,163 - root - WARNING - sss'
# PATTERN="%{TEMP:temp} - root - %{WORD:level} - %{WORD:message}"
# rr=compile(PATTERN)
# print(rr)
# print(re.search(rr, s).groupdict())

#!/usr/bin/env python
# encoding:utf-8

"""
    iter utilities
    ~~~~~~~~~~~~~~

    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

def list_replace(iterable, src, dst):
    """
    Thanks to "EyDu":
        http://www.python-forum.de/viewtopic.php?f=1&t=34539 (de)
    
    >>> list_replace([1,2,3], (1,2), "X")
    ['X', 3]
    
    >>> list_replace([1,2,3,4], (2,3), 9)
    [1, 9, 4]
    
    >>> list_replace([1,2,3], (2,), "X")
    [1, 'X', 3]
    
    >>> list_replace([1,2,3,4,5], (2,3,4), "X")
    [1, 'X', 5]
    
    >>> list_replace([1,2,3,4,5], (4,5), "X")
    [1, 2, 3, 'X']
    
    >>> list_replace([1,2,3,4,5], (1,2), "X")
    ['X', 3, 4, 5]
    
    >>> list_replace([1,2,3,3,3,4,5], (3,3), "X")
    [1, 2, 'X', 3, 4, 5]
    
    >>> list_replace((58, 131, 73, 70), (58, 131), 131)
    [131, 73, 70]
    """
    result=[]
    iterable=list(iterable)
    
    try:
        dst=list(dst)
    except TypeError: # e.g.: int
        dst=[dst]
        
    src=list(src)
    src_len=len(src)
    index = 0
    while index < len(iterable):
        element = iterable[index:index+src_len]
#         print element, src
        if element == src:
            result += dst
            index += src_len
        else:
            result.append(iterable[index])
            index += 1
    return result


if __name__ == "__main__":
    import doctest
    print doctest.testmod()
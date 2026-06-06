def compute_lps(pattern):
    """Computes the Longest Prefix Suffix (LPS) array for KMP."""
    m = len(pattern)
    lps = [0] * m
    length = 0
    i = 1

    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps

def kmp_search(text, pattern):
    """Returns True if pattern is found in text using KMP Algorithm."""
    n = len(text)
    m = len(pattern)
    
    if m == 0: return False
    if m > n: return False

    lps = compute_lps(pattern)
    i = 0  # index for text
    j = 0  # index for pattern

    while i < n:
        if pattern[j] == text[i]:
            i += 1
            j += 1

        if j == m:
            return True # Match found
        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return False

def rabin_karp_search(text, pattern, prime=101):
    """Returns True if pattern is found in text using Rabin-Karp Algorithm."""
    n = len(text)
    m = len(pattern)
    if m == 0 or m > n: return False

    d = 256 # Number of characters in the input alphabet
    p_hash = 0 # Hash value for pattern
    t_hash = 0 # Hash value for text
    h = 1

    for i in range(m - 1):
        h = (h * d) % prime

    for i in range(m):
        p_hash = (d * p_hash + ord(pattern[i])) % prime
        t_hash = (d * t_hash + ord(text[i])) % prime

    for i in range(n - m + 1):
        if p_hash == t_hash:
            # Verify characters one by one
            match = True
            for j in range(m):
                if text[i + j] != pattern[j]:
                    match = False
                    break
            if match:
                return True

        if i < n - m:
            t_hash = (d * (t_hash - ord(text[i]) * h) + ord(text[i + m])) % prime
            if t_hash < 0:
                t_hash += prime
    return False
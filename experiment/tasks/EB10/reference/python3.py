class Solution:
    def stringIndices(self, wordsContainer: List[str], wordsQuery: List[str]) -> List[int]:
        
        trie = {}
        
        for i, word in enumerate(wordsContainer):
            size = len(word)
            
            t = trie
            for c in word[::-1]:
                if '#' in t:
                    if len(wordsContainer[t['#']]) > size:
                        t['#'] = i
                else:
                    t['#'] = i
                
                if c not in t:
                    t[c] = {}
                t = t[c]
                
            if '#' in t:
                if len(wordsContainer[t['#']]) > size:
                    t['#'] = i
            else:
                t['#'] = i
                
        res = []
        for i, word in enumerate(wordsQuery):
            
            t = trie
            for c in word[::-1]:
                if c not in t:
                    res.append(t['#'])
                    break
                t = t[c]
                
            if len(res) == i:
                res.append(t['#'])
        return res
#define X first
#define Y second

using Pii = pair<int, int>;

constexpr int MAX = 500010;
constexpr int INF = 0x3F3F3F3F;

struct Trie {
  struct Node {
    Pii v = std::make_pair(INF, INF);
    int nxt[26];

    Node() { std::memset(nxt, -1, sizeof(nxt)); }
  } q[MAX];

  int cnt = 1;

  void Clear() {
    std::fill(q, q + cnt, Node());
    cnt = 1;
  }

  void Insert(const char* s, int n, int idx) {
    int x = 0;
    Pii cur = std::make_pair(n, idx);
    for (int i = 0; i < n; ++i) {
      q[x].v = std::min(q[x].v, cur);
      int d = s[i] - 'a';
      if (q[x].nxt[d] == -1) {
        q[x].nxt[d] = cnt++;
      }
      x = q[x].nxt[d];
    }
    q[x].v = std::min(q[x].v, cur);
  }
  
  int Query(const char* s, int n) const {
    int x = 0;
    for (int i = 0; i < n; ++i) {
      int d = s[i] - 'a';
      if (q[x].nxt[d] == -1) {
        break;
      }
      x = q[x].nxt[d];
    }
    return q[x].v.Y;
  }
} trie;

class Solution {
public:
    vector<int> stringIndices(vector<string>& wordsContainer, vector<string>& wordsQuery) {
      const auto& a = wordsContainer;
      const auto& q = wordsQuery;
      int n = a.size(), m = q.size();
      trie.Clear();
      for (int i = 0; i < n; ++i) {
        std::string s = a[i];
        std::reverse(s.begin(), s.end());
        trie.Insert(s.c_str(), s.length(), i);
      }
      std::vector<int> ret(m);
      for (int i = 0; i < m; ++i) {
        std::string s = q[i];
        std::reverse(s.begin(), s.end());
        ret[i] = trie.Query(s.c_str(), s.length());
      }
      return ret;
    }
};
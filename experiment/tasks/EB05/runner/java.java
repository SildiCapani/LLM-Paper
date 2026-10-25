public class Main {
    private static int[] deserializeParent(String str) {
        String[] parts = str.split(",");
        int[] res = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            res[i] = Integer.parseInt(parts[i]);
        }
        return res;
    }
    
    private static String serializeOutput(int[] result) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < result.length; i++) {
            if (i > 0) sb.append(",");
            sb.append(result[i]);
        }
        return sb.toString();
    }
    
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine().trim();
        String[] split = line.split(" ", 2);
        int[] parent = deserializeParent(split[0]);
        String s = split[1];
        Solution sol = new Solution();
        int[] ans = sol.findSubtreeSizes(parent, s);
        System.out.println(serializeOutput(ans));
    }
}

==Code Submission==
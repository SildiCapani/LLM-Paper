public class Main {
    private static int[][] deserializeQueries(String qLine) {
        if(qLine.trim().isEmpty()) return new int[0][0];
        String[] parts = qLine.split(";");
        int[][] queries = new int[parts.length][4];
        for (int i = 0; i < parts.length; i++) {
            String[] nums = parts[i].split(",");
            for (int j = 0; j < 4; j++) {
                queries[i][j] = Integer.parseInt(nums[j].trim());
            }
        }
        return queries;
    }
    
    private static String serializeOutput(boolean[] result) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < result.length; i++){
            sb.append(result[i] ? "true" : "false");
            if (i < result.length - 1) sb.append(",");
        }
        return sb.toString();
    }
    
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String s = br.readLine().trim();
        String qLine = br.readLine().trim();
        int[][] queries = deserializeQueries(qLine);
        Solution sol = new Solution();
        boolean[] ans = sol.canMakePalindromeQueries(s, queries);
        System.out.println(serializeOutput(ans));
    }
}

==Code Submission==
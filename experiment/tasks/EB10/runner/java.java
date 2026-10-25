public class Main {
    private static String[] deserialize(String line) {
        return line.split(",");
    }
    
    private static String serializeOutput(int[] result) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < result.length; i++) {
            sb.append(result[i]);
            if(i < result.length - 1) sb.append(",");
        }
        return sb.toString();
    }
    
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String containerLine = br.readLine().trim();
        String queryLine = br.readLine().trim();
        String[] wordsContainer = deserialize(containerLine);
        String[] wordsQuery = deserialize(queryLine);
        Solution sol = new Solution();
        int[] ans = sol.stringIndices(wordsContainer, wordsQuery);
        System.out.println(serializeOutput(ans));
    }
}

==Code Submission==
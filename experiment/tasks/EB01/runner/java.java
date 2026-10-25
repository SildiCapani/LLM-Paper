public class Main {
    private static int[] deserializeInput(String input) {
        if (input.isEmpty())
            return new int[0];
        String[] tokens = input.split(",");
        int[] numbers = new int[tokens.length];
        for (int i = 0; i < tokens.length; i++){
            numbers[i] = Integer.parseInt(tokens[i].trim());
        }
        return numbers;
    }
    
    private static String serializeOutput(long result) {
        return Long.toString(result);
    }
    
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine().trim();
        int[] power = deserializeInput(line);
        Solution sol = new Solution();
        long ans = sol.maximumTotalDamage(power);
        System.out.println(serializeOutput(ans));
    }
}

==Code Submission==
public class Main {
    private static int[] deserializeInput(String input) {
        String[] parts = input.trim().split(",");
        int[] nums = new int[parts.length];
        for (int i = 0; i < parts.length; i++) {
            nums[i] = Integer.parseInt(parts[i]);
        }
        return nums;
    }
    
    private static String serializeOutput(long result) {
        return Long.toString(result);
    }

    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine().trim();
        int[] nums = deserializeInput(line);
        Solution sol = new Solution();
        long ans = sol.sumDigitDifferences(nums);
        System.out.println(serializeOutput(ans));
    }
}

==Code Submission==
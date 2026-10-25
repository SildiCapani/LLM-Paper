// Auto-injected: import java.util.*; import java.util.stream.*; etc.

// No helper data structures like ListNode needed for this problem.

public class Main {

    private static class ParsedInput {
        int[] coins;
        int k;

        ParsedInput(int[] coins, int k) {
            this.coins = coins;
            this.k = k;
        }
    }

    private static ParsedInput deserializeInput(String inputStr) {
        String[] parts = inputStr.trim().split(" ", 2);
        String coinsStr = parts[0];
        int k = Integer.parseInt(parts[1]);

        if (coinsStr.isEmpty()) {
            return new ParsedInput(new int[0], k);
        }
        
        String[] coinItems = coinsStr.split(",");
        int[] coinsArray = new int[coinItems.length];
        for (int i = 0; i < coinItems.length; i++) {
            coinsArray[i] = Integer.parseInt(coinItems[i]);
        }
        return new ParsedInput(coinsArray, k);
    }

    private static String serializeOutput(long result) {
        return String.valueOf(result);
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine();

        ParsedInput parsed = deserializeInput(line);
        
        Solution sol = new Solution();
        long ans = sol.findKthSmallest(parsed.coins, parsed.k);

        System.out.println(serializeOutput(ans));
    }
}

==Code Submission==
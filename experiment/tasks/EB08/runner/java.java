public class Main {
    public static void main(String[] args) throws Exception {
        // Our serialization format: "start,finish,limit,s"
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String line = br.readLine().trim();
        String[] parts = line.split(",", 4);
        long start = Long.parseLong(parts[0]);
        long finish = Long.parseLong(parts[1]);
        int limit = Integer.parseInt(parts[2]);
        String s = parts[3];
        
        Solution sol = new Solution();
        long ans = sol.numberOfPowerfulInt(start, finish, limit, s);
        System.out.println(ans);
    }
}

==Code Submission==
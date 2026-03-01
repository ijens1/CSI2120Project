// Project CSI2120/CSI2520
// Winter 2026
// Bolin Chen #StudentNumberHere
// Isaac Jensen-Large 300341826

public class StableMatching {
    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("Usage: java StableMatching <residents.csv> <programs.csv>");
            return;
        }

        try {
            GaleShapley engine = new GaleShapley(args[0], args[1]);
            
            engine.executeMatching();
            
            System.out.println("Final Matches:");
            for (Resident res : engine.residents.values()) {
                String matchName = "No Match";
                
                if (res.getMatchedProgram() != null) {
                    matchName = res.getMatchedProgram().getName();
                }
                
                System.out.println(res.getFirstname() + " " + res.getLastname() + " -> " + matchName);
            }

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
        }
    }
}
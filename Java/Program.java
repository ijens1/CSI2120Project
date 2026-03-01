// Project CSI2120/CSI2520
// Winter 2026
// Robert Laganiere, uottawa.ca
// Bolin Chen #StudentNumberHere
// Isaac Jensen-Large 300341826

import java.util.ArrayList;

public class Program {
    private String programID;
    private String name;
    private int quota;
    private int[] rol; 
    private ArrayList<Resident> matchedResidents = new ArrayList<>();

    public Program(String id, String n, int q) {
        programID = id;
        name = n;
        quota = q;
    }

    public void setROL(int[] rol) {
        this.rol = rol;
    }

    public String getName() { return name; }
    public String getProgramID() { return programID; }

    public boolean member(int residentID) {
        for (int id : rol) {
            if (id == residentID) return true;
        }
        return false;
    }

    public int rank(int residentID) {
        for (int i = 0; i < rol.length; i++) {
            if (rol[i] == residentID) return i;
        }
        return -1;
    }

    // Finds the "worst" person currently matched to this program [cite: 27]
    public Resident leastPreferred() {
        if (matchedResidents.isEmpty()) return null;
        Resident worst = matchedResidents.get(0);
        for (Resident r : matchedResidents) {
            if (rank(r.getResidentID()) > rank(worst.getResidentID())) {
                worst = r;
            }
        }
        return worst;
    }

    public void addResident(Resident newResident) {
        // If there's space, just add them [cite: 29]
        if (matchedResidents.size() < quota) {
            matchedResidents.add(newResident);
            newResident.setMatchedProgram(this);
        } else {
            // If full, see if new guy is better than the worst current guy [cite: 29]
            Resident worst = leastPreferred();
            if (rank(newResident.getResidentID()) < rank(worst.getResidentID())) {
                // Kick out the worst guy [cite: 30]
                worst.setMatchedProgram(null);
                matchedResidents.remove(worst);
                // Add the new guy
                matchedResidents.add(newResident);
                newResident.setMatchedProgram(this);
            }
        }
    }

    public String toString() {
       return "[" + programID + "]: " + name + " (Quota: " + quota + ")";
    }
}
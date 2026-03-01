// Project CSI2120/CSI2520
// Winter 2026
// Robert Laganiere, uottawa.ca
// Bolin Chen #StudentNumberHere
// Isaac Jensen-Large 300341826

public class Resident {
    
    private int residentID;          
    private String firstname;       
    private String lastname;         
    private String[] rol;            
    
    private Program matchedProgram;  
    private int matchedRank;          
    private int nextChoice = 0;

    public Resident(int id, String fname, String lname) {
        residentID = id;
        firstname = fname;
        lastname = lname;
        matchedProgram = null;       
        matchedRank = -1;             
    }

    public void setROL(String[] rol) {
        this.rol = rol;
    }

    // Getters 
    public int getResidentID() { 
        return residentID; }
    public String getFirstname() { 
        return firstname; }
    public String getLastname() { 
        return lastname; }
    public Program getMatchedProgram() { 
        return matchedProgram; }
    public void setMatchedProgram(Program p) { 
        matchedProgram = p; }

    public String getNextProgramID() {
        if (nextChoice < rol.length) {
            String target = rol[nextChoice];
            nextChoice++;
            return target;
        }
        return null;
    }
    public String toString() {
       return "[" + residentID + "]: " + firstname + " " + lastname + " (" + rol.length + ")";	  
    }
}
// Project CSI2120/CSI2520
// Winter 2026
// Robert Laganiere, uottawa.ca
// Bolin Chen #StudentNumberHere
// Isaac Jensen-Large 300341826

import java.io.*;
import java.util.HashMap;

public class GaleShapley {
    
    public HashMap<Integer, Resident> residents;
    public HashMap<String, Program> programs;

    public GaleShapley(String residentsFilename, String programsFilename) throws IOException { 
        readResidents(residentsFilename);
        readPrograms(programsFilename);
    }

    public void executeMatching() {
        boolean someoneChanged = true;
        
        while (someoneChanged) {
            someoneChanged = false; 
            
            for (Resident res : residents.values()) {
                if (res.getMatchedProgram() == null) {
                    String targetID = res.getNextProgramID();
                    
                    if (targetID != null) {
                        Program prog = programs.get(targetID);
                        
                        if (prog != null && prog.member(res.getResidentID())) {
                            prog.addResident(res);
                            someoneChanged = true; // We made a match, so we gotta check again
                        }
                    }
                }
            }
        }
    }

    public void readResidents(String residentsFilename) throws IOException {
        residents = new HashMap<Integer, Resident>();
        BufferedReader br = new BufferedReader(new FileReader(residentsFilename)); 
        String line = br.readLine(); // skip the header line

        while ((line = br.readLine()) != null && line.length() > 0) {
            // Using basic split like the starter code suggested
            String[] parts = line.split(",");
            int residentID = Integer.parseInt(parts[0]);
            String firstname = parts[1];
            String lastname = parts[2];

            Resident resident = new Resident(residentID, firstname, lastname);

            int start = line.indexOf("[");
            int end = line.indexOf("]");
            if (start != -1 && end != -1) {
                String plist = line.substring(start + 1, end);
                String[] rol = plist.split(",");
                resident.setROL(rol);
            }
            
            residents.put(residentID, resident);
        }
        br.close();
    }

    public void readPrograms(String programsFilename) throws IOException {
        programs = new HashMap<String, Program>();
        BufferedReader br = new BufferedReader(new FileReader(programsFilename)); 
        String line = br.readLine(); // skip header

        while ((line = br.readLine()) != null && line.length() > 0) {
            String[] parts = line.split(",");
            String programID = parts[0];
            String name = parts[1];
            int quota = Integer.parseInt(parts[2]);

            Program program = new Program(programID, name, quota);

            int start = line.indexOf("[");
            int end = line.indexOf("]");
            if (start != -1 && end != -1) {
                String rlist = line.substring(start + 1, end);
                String[] rol_string = rlist.split(",");
                int[] rol = new int[rol_string.length];
                
                for (int j = 0; j < rol_string.length; j++) {
                    rol[j] = Integer.parseInt(rol_string[j].trim());
                }
                program.setROL(rol);
            }
            
            programs.put(programID, program);
        }
        br.close();
    }
}
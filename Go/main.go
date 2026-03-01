package main

//Bo Lin Chen #300236550

import (
	"encoding/csv"
	"flag"
	"fmt"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"
)

// resident type
type Resident struct {
	residentID     int
	firstname      string
	lastname       string
	rol            []string
	matchedProgram string
	nextProposal   int
}

// program type
type Program struct {
	programID         string
	name              string
	nPositions        int
	rol               []int
	selectedResidents []int
	mu                sync.Mutex
}

func prefers(p *Program, r1 int, r2 int) bool {
	pos1 := 9999
	pos2 := 9999
	// loop to find rank
	for i := 0; i < len(p.rol); i++ {
		if p.rol[i] == r1 {
			pos1 = i
		}
		if p.rol[i] == r2 {
			pos2 = i
		}
	}

	if pos1 < pos2 {
		return true
	}
	return false
}

func evaluate(rid int, pid string, residents map[int]*Resident, programs map[string]*Program, wg *sync.WaitGroup) {

	prog := programs[pid]

	if prog == nil {
		return
	}

	prog.mu.Lock()
	defer prog.mu.Unlock()
	// adds if program has open spot
	if len(prog.selectedResidents) < prog.nPositions {
		prog.selectedResidents = append(prog.selectedResidents, rid)
		residents[rid].matchedProgram = pid
	} else {
		// finding the worst resident avaliable
		worstRes := prog.selectedResidents[0]
		worstIndex := 0

		for i := 0; i < len(prog.selectedResidents); i++ {
			if prefers(prog, worstRes, prog.selectedResidents[i]) {
				worstRes = prog.selectedResidents[i]
				worstIndex = i
			}
		}
		// checking if the new applicant is better than the worst one we just found
		if prefers(prog, rid, worstRes) == true {
			prog.selectedResidents[worstIndex] = rid
			residents[rid].matchedProgram = pid
			residents[worstRes].matchedProgram = ""

			if wg != nil {
				wg.Add(1)
				go offer(worstRes, residents, programs, wg)
			} else {
				offer(worstRes, residents, programs, nil)
			}
		} else {
			// rid is rejected outright — have them try their next choice
			if wg != nil {
				wg.Add(1)
				go offer(rid, residents, programs, wg)
			} else {
				offer(rid, residents, programs, nil)
			}
		}
	}
}

func offer(rid int, residents map[int]*Resident, programs map[string]*Program, wg *sync.WaitGroup) {
	if wg != nil {
		defer wg.Done()
	}

	res := residents[rid]

	if res.nextProposal < len(res.rol) {
		nextProg := res.rol[res.nextProposal]
		res.nextProposal = res.nextProposal + 1
		evaluate(rid, nextProg, residents, programs, wg)
	}
}

func loadResidents(filename string) map[int]*Resident {
	file, err := os.Open(filename)
	if err != nil {
		fmt.Println("Error opening file:", filename)
		return nil
	}
	defer file.Close()

	reader := csv.NewReader(file)
	reader.TrimLeadingSpace = true
	lines, _ := reader.ReadAll()
	resMap := make(map[int]*Resident)

	for i := 1; i < len(lines); i++ {
		line := lines[i]
		id, _ := strconv.Atoi(strings.TrimSpace(line[0]))

		rawRol := strings.Split(strings.Trim(line[3], "[]"), ",")
		var rol []string
		for _, s := range rawRol {
			s = strings.TrimSpace(s)
			if s != "" {
				rol = append(rol, s)
			}
		}

		resMap[id] = &Resident{
			residentID: id,
			firstname:  strings.TrimSpace(line[1]),
			lastname:   strings.TrimSpace(line[2]),
			rol:        rol,
		}
	}
	return resMap
}

func loadPrograms(filename string) map[string]*Program {
	file, err := os.Open(filename)
	if err != nil {
		fmt.Println("Error opening file:", filename)
		return nil
	}
	defer file.Close()

	reader := csv.NewReader(file)
	reader.TrimLeadingSpace = true
	lines, _ := reader.ReadAll()
	progMap := make(map[string]*Program)

	for i := 1; i < len(lines); i++ {
		line := lines[i]
		progID := strings.TrimSpace(line[0])
		nPos, _ := strconv.Atoi(strings.TrimSpace(line[2]))
		// split and clean up list
		rawRol := strings.Split(strings.Trim(line[3], "[]"), ",")
		var rol []int
		for _, s := range rawRol {
			s = strings.TrimSpace(s)
			if s != "" {
				val, _ := strconv.Atoi(s)
				rol = append(rol, val)
			}
		}

		progMap[progID] = &Program{
			programID:  progID,
			name:       strings.TrimSpace(line[1]),
			nPositions: nPos,
			rol:        rol,
		}
	}
	return progMap
}

func main() {
	concurrent := flag.Bool("concurrent", false, "run in concurrent mode")
	flag.Parse()

	// change file name to test different csv files
	resFile := "residentSmall.csv"
	progFile := "programSmall.csv"

	residents := loadResidents(resFile)
	programs := loadPrograms(progFile)

	if residents == nil || programs == nil {
		return
	}

	start := time.Now()
	var wg sync.WaitGroup
	for id := range residents {
		if *concurrent {
			wg.Add(1)
			go offer(id, residents, programs, &wg)
		} else {
			offer(id, residents, programs, nil)
		}
	}
	if *concurrent {
		wg.Wait()
	}
	end := time.Now()

	// print solution
	unmatchedCount := 0
	for _, r := range residents {
		if r.matchedProgram == "" {
			fmt.Printf("%s, %s, %d, XXX, NOT MATCHED\n", r.lastname, r.firstname, r.residentID)
			unmatchedCount++
		} else {
			p := programs[r.matchedProgram]
			fmt.Printf("%s, %s, %d, %s, %s\n", r.lastname, r.firstname, r.residentID, p.programID, p.name)
		}
	}

	availablePos := 0
	for _, p := range programs {
		availablePos += (p.nPositions - len(p.selectedResidents))
	}

	fmt.Printf("\nNumber of unmatched residents: %d\n", unmatchedCount)
	fmt.Printf("Number of positions available: %d\n", availablePos)
	fmt.Printf("Execution time: %s\n", end.Sub(start))
}

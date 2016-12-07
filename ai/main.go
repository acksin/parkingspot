package main

import (
	"bufio"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"
	"sync"
)

type fileWriter struct {
	f *os.File
	c chan stage2
}

type stage2 struct {
	split []string
	line  string
}

var (
	s1c chan string
	s2c chan stage2

	filec chan string

	s2file map[string]*fileWriter

	s = &sync.Mutex{}
)

func osName(o string) string {
	if o == "Linux/UNIX" {
		return "linux"
	}
	return "windows"
}

func (s *fileWriter) writeWorker() {
	for {
		v := <-s.c

		if _, err := s.f.WriteString(v.line + "\n"); err != nil {
			fmt.Println(err)
		}
	}
}

func stage1Worker() {
	for {
		v := <-s1c
		s := strings.Split(v, ",")

		if s[2] != "SUSE Linux" {
			fileName := filepath.Join("spot_prices_split", s[0], s[1], osName(s[2]), "spot_prices.csv")

			s2file[fileName].c <- stage2{s, v}
		}
	}
}

func stage1() {
	f, _ := os.Open("spot_prices.csv")

	i := 0
	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		i++
		if i%10000 == 0 {
			fmt.Println(i)
		}
		s1c <- scanner.Text() // Println will add back the final '\n'
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, "reading standard input:", err)
	}
}

func main() {
	s1c = make(chan string)
	s2c = make(chan stage2)
	filec = make(chan string)

	s2file = make(map[string]*fileWriter)

	b, _ := ioutil.ReadFile("azs.csv")
	b2, _ := ioutil.ReadFile("insts.csv")

	for _, az := range strings.Split(string(b), "\n") {
		for _, inst := range strings.Split(string(b2), "\n") {
			if az != "" && inst != "" {
				for _, o := range []string{"linux", "windows"} {
					fileName := filepath.Join("spot_prices_split", az, inst, o, "spot_prices.csv")

					os.MkdirAll(filepath.Dir(fileName), 0755)

					fmt.Println("Creating", fileName)

					f, err := os.OpenFile(fileName, os.O_APPEND|os.O_WRONLY|os.O_CREATE, 0666)
					if err != nil {
						fmt.Println(err)
					}

					s2file[fileName] = &fileWriter{f, make(chan stage2)}
					go s2file[fileName].writeWorker()
				}
			}
		}
	}

	for i := 0; i < 100; i++ {
		go stage1Worker()
	}

	stage1()
}

#!/usr/bin/python3

import csv, sys

if __name__ == "__main__":
    
    students = []
    with open(sys.argv[1], 'r') as fd:
        reader = csv.reader(fd)
        header = next(reader)
        for row in reader:
            if "151-001" in row[4] and row[0] != "Student, Test":
                first, last = row.strip().split(",")
                students.append(f"{first} {last}")
    
    with open("students.txt", 'w') as fd:
        fd.write("\n".join(students))

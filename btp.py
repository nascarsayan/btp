import csv
from collections import defaultdict
import datetime
from prettytable import PrettyTable
import requests
from sys import argv

#max_per_prof = 4

def download_file(rn):
    response = requests.get("https://docs.google.com/spreadsheets/d/12uKBLCAfI0McgkQnULzJEg8WtEifNbDx4E5-7QI22iY/gviz/tq?tqx=out:csv&sheet=1")
    assert response.status_code == 200, 'Wrong status code'
    #print response.content
    dat = response.content
    if len(rn) > 0 :
        dat = dat.split(rn)
        dat = dat[0]
    with open("Choices.csv", "wb") as f:
        f.write(dat)
    print "File written successfully"

def listFromcsv(filename):

    i = 0 # dr number - 1
    count = 0
    bad_count = 0 # people who haven't filled yet
    bad_threshold = 107 # ignoring for now

    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[1] == "NAME":
                continue

            if (row[3] == "" and row[4] == ""):
                bad_count += 1

            # upto 5 bad entries accepted
            if bad_count == bad_threshold:
                break

            count += 1

    print "Overview of allocation based on", count, "students who have filled their choices"

    #count = 123 # total number of students to be alloted
    lister = [[] for i in range(count)] # gives list for each student who has filled priorities

    i = 0
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[1] == "NAME":
                continue
            if i == count:
                break
            j = 3
            lister[i].append(row[1])
            if row[j] == '':
                lister[i].append("")
            #print row[1],len(row)
            while 1:
                if j == 23:       # upto 20 choices
                    break
                if row[j] == '': # last choice
                    if row[j+1] == '':
                        break
                    else:
                        j+=1
                        continue
                if row[j][0] == '/': # comments ignored
                    break
                if row[j][0] == ' ': # because there exist dumbf#cks
                    break
                row[j] = row[j].strip() # row[j] is j-1 th preference of ith student
                lister[i].append(row[j])
                # print row[j] # j-1 th choice
                j += 1
            i += 1

    # print lister
    return lister


def dicttFromcsv(filename):

    with open(filename, mode='rb') as infile:
        reader = csv.reader(infile)
        d = defaultdict(list)
        prof = dict()
        for row in reader:
            if row[1] == "Code" or row[1] == "":
                continue

            if(row[7]==""):
                d[row[1]].append(1)
            else:
                d[row[1]].append(int(row[7]))
            d[row[1]].append(row[8])
            d[row[1]].append(0)
            d[row[1]].append(row[3])
            prof[row[3]] = 0    # new restriction :
                                # each prof can have 4 students with CG > 7
            #d[row[1]]=list(int(row[7]),row[8],0)
            # row 1 is code , 7 is capacity , 8 is type of student
            # 0 is the filled value to be used later

    # print "Profs"
    # print prof
    return d, prof


def showRemaining(projects, profs):
    """
        See left courses capacity filled and total
    """
    # pros = PrettyTable(['Code', 'Capacity', 'Filled', 'Prof filled', 'Prof available'])
    pros = PrettyTable(['Code', 'Capacity', 'Filled'])
    rem = 0
    profav = 0
    for each in sorted(projects.keys()):
        pros.add_row([each, projects[each][0],projects[each][2]])
        if projects[each][0] != projects[each][2]:    # capacity not full
            # profFilled = profs[projects[each][3]]
            # if profFilled == max_per_prof:
            #     pros.add_row([each, projects[each][0], projects[each][2], profFilled, "X NO"])
            # else:
                # pros.add_row([each, projects[each][0], projects[each][2], profFilled, "  Yes"])
                # profav += 1
            rem += (projects[each][0]-projects[each][2])

    print "\nOverview of remaining projects : "
    print pros
    print rem, "projects remain"
    # print profav, "projects remain with available professors"


def allot(projects, people, profs, details):
    """
        Print DR# wise project alloted
        details matlab print small details for allocation
        profs has the count for prof . At max 4 per prof for CG > 7
    """

    statsTable = PrettyTable(['Name', 'Tentative'])
    for student in people: # student has name and all choices of him/her
        if details == "1":
            print "\n", student[0], "\t\t",
            print student
        for i in range(1, len(student)):
            #print student[i]

            # student[i] is i-1 th priority

            if student[i] == "" and len(student)<=2 :    
                statsTable.add_row([student[0], "Fill choices"])
                break
            elif student[i] == "":
                continue

            elif student[i] not in projects:
                # statsTable.add_row([student[0],"Invalid choice"+str(i)])
                print "Invalid choice ", student[i], "for", student[0]
                continue

            thisProject = projects[student[i]]
            # again , trusting people fill proper codes

            if thisProject[2] == thisProject[0]: # capacity full

                # remove below for debugging
                if details == "1":
                    print student[i], "full\t",
                if i == len(student)-1:
                    if details == "1":
                            print "Tumse na ho payega"
                    statsTable.add_row([student[0], "Out of choices"])
                continue # look for next

            # # new constraint : at max max_per_prof people under that prof
            # if profs[thisProject[3]] == max_per_prof:
            #     # remove below for debugging
            #     if details == "1":
            #         print student[i], "unavailable since prof already has 4 students\t",
            #     if i == len(student)-1:
            #         if details == "1":
            #             print "Out of choices"
            #         statsTable.add_row([student[0], "Out of choices(prof filled)"])
            #     continue # look for next

            # if here , it means student gets it
            if details == "1":
                print student[i], "alloted"
            statsTable.add_row([student[0], student[i]])
            projects[student[i]][2] += 1 # update filled positions
            profs[projects[student[i]][3]] += 1 # number of students under that prof
            break

    # tabulated results are printed
    print statsTable



def main():
    """
        Get shit done.
    """
    print "Downloading..."
    rn = ""
    if len(argv) > 1:
		# roll number below you is supplied, show btp alloc of all above you
        rn = '"%s"' % argv[1]
    download_file(rn)
    print "The file has been downloaded"

    now = datetime.datetime.now()
    print "Script started on "+now.strftime("%A %d %B %Y %I:%M:%S %p %Z")
    #deprecated for the time being change 0 to 1 for detailed view
    details = ""

    #details = raw_input("Print allocation details ?\n 1 for yes , any other char for no : ")
    projects, profs = dicttFromcsv("Projects.csv")

    #assumed that Choices.csv is sorted by DR#
    # ignoring constraints like Any, BTech , Dual , CG > 8.5 for now
    # Expecting people not to be arseholes , like a dual guy taking btech specific
    people = listFromcsv("Choices.csv")

    #print len(people)
    allot(projects, people, profs, details)

    #remainder = raw_input("Show remaining options ?\n 1 for yes , any other char for no : ")
    #if remainder=="1":
    showRemaining(projects, profs)
    now = datetime.datetime.now()
    print "Script ended on "+now.strftime("%A %d %B %Y %I:%M:%S %p %Z")
    

if __name__ == "__main__":
    main()

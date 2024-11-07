# RateMyProfessor "Scraper"
A class that sends get requests to RateMyProfessors.com to make CSV files of RateMyProfessor information at a school. 

# How to use:

#### First, call the constructor with the RateMyProfessor school ID of a school of your choice. This ID can be found in the RMP link when you navigate to your school

```
uncc = RMPSchool(1253)  # example for UNC Charlotte, which has School ID of 1253
```

#### Then, use the object you just created and call RMPSchool.dump_to_csv()

```
uncc.dump_to_csv() 
```
![Screenshot 2024-11-06 232337](https://github.com/user-attachments/assets/0b426af5-6ca4-4179-8cb9-b0d62badf1bf)


#### After the code executes, which should take a while for large schools, you should have two new CSV files saved in your directory called:

```
<YourSchoolName>Profs.csv
<YourSchoolName>Reviews.csv
```

### <YourSchoolName>Profs.csv:
![image](https://github.com/user-attachments/assets/98466601-981a-4fd2-aff6-075893df2ed1)

### <YourSchoolName>Reviews.csv: 
![image](https://github.com/user-attachments/assets/56acb366-065d-4781-8842-17d22f3d0d2b)


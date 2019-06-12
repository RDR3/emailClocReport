# emailClocReport
___

#### Scan a specified repo using cloc-1.64.exe and email the results as a .csv file.

emailClocReport.py clones a repository of your specification to your local machine. It downloads cloc v1.64 to the working directory and scans the repo clone. The results of the scan are sent to an email address you specify as a .csv file. At the end you have the option to remove the repo clone directory and the cloc file from the working directory.

##### Requirements

To use emailClocReport, you will need the following:

  - Python v. 3.7.3 installed
  - **Note:** Python and pip must be on the local machine's PATH
  - Gmail account & password to use as the sender 
  - **Note:** Destination address does not have to be gmail
  - Git v2.21.0.windows.1
  - **Note:** It is recommended to install emailClocReport to a directory that does not require admin rights. If you install to a directory that requires admin rights, you will need to open Bash, Powershell, or Windows command prompt as an admin.
 

##### Usage
- emailClocReport works with Bash, Powershell, and Windows command prompt
- The console output is a bit verbose with several user inputs and options
- cloc is downloaded from: <https://sourceforge.net/projects/cloc/files/latest/download>
- **Note:** Following the link above will begin a cloc download


##### Output
- An email is sent to the receiving address with the subject "Repo <repo> scanned by cloc"
- The body will read "This email has the cloc scan of Git repo <repo> attached as clocReport.csv"
- The .csv file will conform to the following format:

Files | Language | Blank | Comment | Code | http://clocsourceforge.net v 1.64 T=___s (___files/s, ___lines/s)
:---:|:---:|:---:|:---:|:---:|:---
Number of files per language | Programming language | Number of blank lines | Number of lines that are comments | Number of lines of actual code | This column only has data in the header, it specifies the cloc source and speed. T = elapsed time and <files per second, lines per second>



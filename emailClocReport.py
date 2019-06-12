import getpass, re, smtplib, ssl, email, subprocess, shutil, os, time, datetime
import stat, mimetypes, urllib.request, sys, multiprocessing, errno

from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from shutil import copy
from multiprocessing import Process

# Global variables:
# Current working directory, used for cloc download and git clone 
p = os.getcwd()

# Functions:
# Directory overwritewrite (to reuse this script on same repo, if directory was not deleted)
def redo_with_write(redo_func, p, err):
    os.chmod(p, stat.S_IWRITE)
    redo_func(p)

# clocDownload checks for and downloads cloc
# clocDownload runs as a thread then joins main after completion
def clocDownload(p):
    # Inform the user
    print("This python script scans a Git repo using cloc v1.64 and sends the results " +  
    "to a specified email address as a .csv file. \n" + "You will need git installed on your " +
    "machine, your gmail credentials, and the destination email address. \n" +
    "This script will download cloc v1.64.exe to this directory, unless it already exists.")
    # Check for cloc in cwd
    print ("The current working directory is %s" % p)
    clocExistsPath = p + "/cloc-1.64.exe"
    if os.path.exists(clocExistsPath):
        print("cloc is installed in the cwd")
    if not os.path.exists(clocExistsPath):
        print("cloc is downloading to the cwd")
        clocDownloadUrl = "https://sourceforge.net/projects/cloc/files/latest/download"
        f = urllib.request.urlopen(clocDownloadUrl)
        file = f.read()
        f.close
        f2 = open('cloc-1.64.exe', 'wb')
        f2.write(file)
        f2.close

# Scan Git clone using cloc
def useCloc(directory):
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S')
    clocResultsReturned = subprocess.call(["cloc-1.64.exe", directory, "--csv", "--report-file=clocReport.csv"])
    print("Cloc started")

# Error handling for shutil.rmtree removing git clone directory at end of run
def handleError(func, path, exc_info):
    # Uncomment the line below if you want to print the error info
    #print(exc_info)
    # Check file access permissions
    if not os.access(path, os.W_OK):
       # Change the permision of file
       os.chmod(path, stat.S_IWUSR)
       # call the calling function again
       func(path)

# Delete cloc
def removeCloc(filename):
    try:
        os.remove(filename)
    except OSError as e:
        # errno.ENOENT = no such file or directory
        if e.errno != errno.ENOENT:
            # raise exception if a different error occurred
            raise

# Remove the cloned Git repo directory
def removeCloneDir(directory):
    try:  
        shutil.rmtree(directory, ignore_errors=True)
        shutil.rmtree(directory, onerror=handleError)
        shutil.rmtree(directory, ignore_errors=True)
    except OSError:  
        print ("Working on " + directory)

def main():
    # Enter the repo url to be scanned 
    repo = input("Please enter the path/to/repository to be scanned: https://")
    url = "https://" + repo

    # Port for SSL
    port = 465

    # Email address and password to send from
    gmail = input("Please type in your Gmail account to send from and press enter: ")
    password = getpass.getpass("Please type your Gmail password and press enter: ")

    # Email address to send to
    try:
        email2 = input("Please enter the email address to send the cloc results to: ")
        if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email2):
            raise ValueError("That is not a valid email address!")
    except ValueError as ve:
        print(ve)

    # Create destination directory for git clone  
    directory = p + "\\" + repo.replace("/", "\\")
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        shutil.rmtree(directory, onerror=redo_with_write)
        os.makedirs(directory)
    print("Directory ", directory, " created")
    
    # Clone Git repo to local machine
    clonedDirectory = subprocess.call(["git", "clone", url, directory])
    time.sleep(2)
    print("Git cloned")

    # Call useCloc once cloc is downloaded
    useCloc(directory)

    # Send an email from your gmail account to the destination email
    subject = "Repo " + repo + " scanned by cloc"
    body = "This email has the cloc scan of Git repo " + repo + " attached as clocReport.csv"

    message = MIMEMultipart()
    message["From"] = gmail
    message["To"] = email2
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    fileToSend = "clocReport.csv"

    ctype, encoding = mimetypes.guess_type(fileToSend)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)

    if maintype == "text":
        fp = open(fileToSend)
        attachment = MIMEText(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "image":
        fp = open(fileToSend, "rb")
        attachment = MIMEImage(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "audio":
        fp = open(fileToSend, "rb")
        attachment = MIMEAudio(fp.read(), _subtype=subtype)
        fp.close()
    else:
        fp = open(fileToSend, "rb")
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
    message.attach(attachment)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(gmail, password)
        server.sendmail(gmail, email2, message.as_string())
        server.quit()
    print("Email sent to " + email2)

    # Remove cloned directory
    removeCloneDirectory = input("Would you like to remove " + directory + " ?\n" +
    "Enter 1 for yes: \n" + "Enter 0 for no: ")
    try:
        valu = int(removeCloneDirectory)
    except ValueError:
        print("That was not an integer, exiting program.")
        sys.exit()
    if valu == 1:
        removeCloneDir(directory)
        d = repo.replace("/", "\\")
        data = d.split("\\")
        s = "\\"
        x = len(data)
        for i in range(x, 0, -1):
            t = s.join(data)
            y = p + "\\" + t
            if os.path.exists(y):
                try:  
                     removeCloneDir(y)
                except OSError:  
                    print ("Deletion of the directory %s failed" % directory)
            del data[-1]  
        print ("Successfully deleted the directory %s" % directory)
    elif valu == 0:
        print("Directory saved")
    else:
        print("That is not 1 or 0, exiting program.")
        sys.exit()

    # Remove cloc
    deleteClocFile = input("Would you like to remove cloc-1.64.exe ?\n" + "Enter 1 for yes: \n" + "Enter 0 for no: ")
    try:
        val = int(deleteClocFile)
    except ValueError:
        print("That was not an integer, exiting program")
        sys.exit()
    if val == 1:
        # Call function removeCloc for error handling
        removeCloc("cloc-1.64.exe")
        print("cloc removed!")
    elif val == 0:
        print("cloc-1.64.exe saved")
    else:
        print("That is not 1 or 0, exiting program.")
        sys.exit()

if __name__ == '__main__':
    pro = Process(target=clocDownload(p), args=(p,))
    pro.start()
    pro.join()
    main()
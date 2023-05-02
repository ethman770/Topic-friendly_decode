# * * * * * * * Dependencies * * * * * * * 
import pyperclip, re, os

# * * * * * * * Global Variables * * * * * * * 
raw_bt = ""
clean_bt = ""
topic_bt = ""
topic_adv_bt = ""
dsig_bt = ""
bt_source = ""
clipboard = ""

# * * * * * * * Functions * * * * * * * 
def identifyBTsource():
    global raw_bt, bt_source, clipboard, topic_adv_bt

    # Get raw decode from user's clipboard
    clipboard = pyperclip.paste()
    
    raw_bt = clipboard

    # Divide the clipboard into lines
    clipboard = clipboard.split(os.linesep)

    # Regex patterns
    linaPattern = re.compile("\|   0x[\da-f]+ : ")
    gnosisPattern = re.compile("\|   .*")
    gdbPattern = re.compile("#0 .*")
    smartDecoderPattern = re.compile("\s*1\. .*")

    if linaPattern.match(clipboard[0]):
        bt_source = "lina"
    elif gnosisPattern.match(clipboard[0]):
        bt_source = "Gnosis"
    elif gdbPattern.match(clipboard[0]):
        bt_source = "GDB"
    elif smartDecoderPattern.match(clipboard[0]):
        bt_source = "SmartDecoder"
    else:
        print("Backtrace format not recognized")
        exit()

def processBT(bt_source):
    global clean_bt, topic_bt, dsig_bt, topic_adv_bt

    #print(bt_source)
    #print(clipboard[0])

    # Choose the patterns based on the backtrace type
    if bt_source == "GDB":
        frameNumPattern = re.compile("#[\d]+\s+")
        memAddressPattern = re.compile("0x[\da-f]+ in ")
        postFuncPattern = re.compile("\s[\[\(].*")

    elif bt_source == "Gnosis":
        frameNumPattern = re.compile("\|\s+")
        memAddressPattern = re.compile("None\s|[\da-f]+\s")
        postFuncPattern = re.compile("\s")

    elif bt_source == "lina":
        frameNumPattern = re.compile("") #No frame numbers
        memAddressPattern = re.compile("\|   0x[\da-f]+ : ")
        postFuncPattern = re.compile("[+\d]* at .*")

    else: # Will be SmartDecoder
        frameNumPattern = re.compile("^\s*\d+\.\s")
        memAddressPattern = re.compile("0x[\da-f]+\s")
        postFuncPattern = re.compile("\s\-.*")

    # Start off the advanced search
    topic_adv_bt = "OR("
    
    function_count = 0

    for line in clipboard:
        function_count = function_count + 1
        function = re.sub(frameNumPattern,"",line)
        function = re.sub(memAddressPattern,"",function)
        function = re.sub(postFuncPattern,"",function)

        clean_bt = clean_bt + function + "\n"

        # Still needs underscores escaped
        topic_bt = topic_bt + '"' + function + '" '

        topic_adv_bt = topic_adv_bt + '"' + function + '", '

        dsig_bt = dsig_bt + function + ".+?"

    # Escape the underscores
    topic_bt = topic_bt.replace("_","\_")
    topic_adv_bt = topic_adv_bt.replace("_","\_")
    
    # Complete advanced search query with minimum that looks for n-1 functions
    topic_adv_bt = topic_adv_bt + "min=" + str(int(function_count/2)) + ")"


def presentBT():
    print("Raw input")
    print(raw_bt)
    print("\nFunction Names")
    print(clean_bt)
    print("Old Topic formats")
    print(topic_bt)
    print("\n")
    print(topic_adv_bt)
    print("\nGnosis")
    print(dsig_bt[:-3])     # "[:-3]" is printed to avoid printing ".+?" at the end
    pyperclip.copy(topic_bt)

# * * * * * * * Steps * * * * * * * 

def main():
    # Identify which source the BT came from: Gnosis, SmartDecoder, or GDB
    identifyBTsource()

	# Get the bt from the user and clean it up
    processBT(bt_source)
    
    # Place the Topic-friendly decode in the clipboard, print it, the raw BT, and the clean BT in the command prompt
    presentBT()

if __name__ == '__main__':
	main()
#! /usr/bin/python

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
import os
import sys
from sets import Set


__author__ = "Vishesh"
__date__ = "$22 Feb, 2015 5:11:09 PM$"

#if __name__ == "__main__":
#   print "Hello World";


TYPE_PHRASE = 0
TYPE_POS = 1
TYPE_LEAF = 2
LEAF = 1


STANFORD_PARSER_EXEC="/home/dsluser/Desktop/Natural_Language_Processing/stanford-parser-full-2015-01-30/lexparser.sh"
INPUT_FILE='/home/dsluser/Desktop/Natural_Language_Processing/stanford-parser-full-2015-01-30/input'
STANFORD_PARSER_INPUT_SENTENCE_FILE = '/home/dsluser/Desktop/Natural_Language_Processing/stanford-parser-full-2015-01-30/stanford_parser_input'
STANFORD_PARSER_OUTPUT_FILE='/home/dsluser/Desktop/Natural_Language_Processing/stanford-parser-full-2015-01-30/stanford_parser_output'
SEARCH_TERM = "manap"

IGNORE_KEYWORDS_SET = Set(["", ";", ",","``", "''", "a", "an", "am", "and", "are",
                                    "be", "being", "by", "do", "has", "here",
                                    "i", "in", "is", "it", "its", 
                                    "may", "my", "not", "of", "our", 
                                    "say", "see", "so", "such",
                                    "that","the", "there","these", "this", "to",
                                    "we", "with", "what", "will",
                                    "you", "your"])


prev_leaf = None
first_leaf = None

class TreeNode:
    def __init__(self):    
        self.indent = -1 #Used to determine parent-child relationship, since children have higher indent than parent in the text output from the parser
        self.should_print = -1 # Not used, to be used later
        self.in_keyword_path = 0 #Placeholder for future plans
        self.parent = None #Parent pointer in the parse tree
        self.children = [] #Children list of this node
        self.type = 0 
        self.name = "" #Denotes keyword itself or the phrase name
        self.left = None #These 2 are to interconnect leaf entries
        self.right = None
        
    def print_raw_node(self):
        print self.indent
        print self.should_print
        print self.in_keyword_path
        print self.parent
        print self.children
        print self.type
        print self.name
    
    def print_children(self):
        for child in self.children:
            #child.print_children()
            child.print_raw_node()
        
    def insert_phrase_node(self, name, indent):
        #if more indented means it is the child of the previous element
        if (self.indent < indent):
            new_node = TreeNode()
            new_node.type = TYPE_PHRASE
            new_node.name = name    
            new_node.parent = self
            new_node.indent = indent
            self.children.append(new_node)
            #print "Parent:", self.name, "Child:", name 
            return new_node
        else:
            return self.parent.insert_phrase_node(name, indent)
        
            
    def insert_POS_node(self, name, indent):
        #if more indented means it is the child of the previous element
        if (self.indent < indent):
            new_node = TreeNode()
            new_node.type = TYPE_POS
            new_node.name = name    
            new_node.parent = self
            self.children.append(new_node)
            #print "Parent:", self.name, "Child:", name 
            return new_node
        else:
            return self.parent.insert_POS_node(name, indent)
        
    def insert_leaf_node(self, name):
        #if more indented means it is the child of the previous element
        global prev_leaf
        global first_leaf
        new_node = TreeNode()
        new_node.type = TYPE_LEAF
        new_node.name = name    
        new_node.parent = self
        #print "Parent:", self.name, "Child:", name 
        self.children.append(new_node)
        
        new_node.left = prev_leaf
        if(prev_leaf == None):
            first_leaf = new_node
        else:
            prev_leaf.right = new_node
        prev_leaf = new_node
        return new_node
        
def remove_closing_braces(name):
    while name[-1] == ')':
        name = name[:-1]
    return name

def remove_beginning_extraneous_characters(sentence):
    while (sentence != "" and (sentence[0] == ' ' or sentence[0] == '\n' or sentence[0] == '\t')):
        sentence = sentence[1:]
    return sentence

'''
Reads the raw text file and identifies the sentence in which the phrase features.
Dumps this sentence to a separate file so that the stanford parser can parse it
and dump its output for further processing
'''
def identify_keyword_sentence_in_file(search_string, FILE):
    print "Keyword: ",search_string
    f = open(FILE,"r")
    fout = open(STANFORD_PARSER_INPUT_SENTENCE_FILE,"w")
    for line in f:
        print line
        mySentences = line.split('.')
        for sentence in mySentences:
            if (sentence.lower().find(search_string.lower()) > -1):
                fout.write(sentence)
                print "Keyword sentence found"
                fout.close()
                return
    
    print "Keyword sentence not found"
    

'''
Constructs a tree by parsing the indented output dump from stanford_PCFG_parser.
Also keeps track of where it found the search_string that was passed as argument 
to this function
and returns a pointer to that node for future use.
'''
def make_tree(INPUT_FILE):    
    x=TreeNode()
    ROOT=x
    x.name = "ROOT"
    global prev_leaf 
    global first_leaf
    prev_leaf = None
    first_leaf = None
    
    f = open(INPUT_FILE,"r") 
       
    myList = []

    for line in f:
        myList.append(line)
    
    #for line in myList:
        #print line

    for line in myList:
        line_indent =  (len(line) - len(line.lstrip()) )
        line = line.lstrip()
        if (len(line) < 1 or (line[0] != '(')):
            continue
        #print line

        word_list = line.split()
        while(len(word_list) > 0):
            keyword = word_list[0][1:] #get first word without open bracket

            #Vishesh: Not necessary that the beginning of each line is a phrase
            if (len(word_list) < 2):
                #CASE (NP
                x = x.insert_phrase_node(keyword, line_indent)
                word_list = word_list[1:]
                
            elif(word_list[1][0] == '('):
                #CASE (NP (POS leaf)
                x = x.insert_phrase_node(keyword, line_indent)
                line_indent = line_indent + len(word_list[0])
                word_list = word_list[1:]
            ###Vishesh TODO: check for more than 2 leaf nodes at the same level
            else:
                #CASE (POS leaf)
                '''Note: shouldn't update x itself, otherwise the next child of 
                parent phrase of this POS will get messed up'''
                POS_node = x.insert_POS_node(keyword, line_indent)
                keyword = remove_closing_braces(word_list[1])
                leaf_node = POS_node.insert_leaf_node(keyword)
                line_indent = line_indent + len(word_list[0]) + len(word_list[1])
                word_list = word_list[2:]



    return (ROOT)

'''
Prints all the leaves of the tree rooted at the root to the file pointed by FILE_HANDLE
'''
def populate_leaves_list(root, leaves_list):
    if (root.type == TYPE_LEAF):
        if (root.name not in [",", ";"]):
            leaves_list = leaves_list + " "
        leaves_list = leaves_list + root.name
        
    else:
        for child in root.children:
            leaves_list = populate_leaves_list(child, leaves_list)
    return leaves_list
            
def print_all_leaves():
    global first_leaf
    node = first_leaf
    while node != None:
        print node.name
        node = node.right
        
def print_all_nodes(root):
    print root.name,"[",
    if (root.type != TYPE_LEAF):
        for child in root.children:
            print_all_nodes(child)
    print "]"
        
    
        
def find_keyword_node(search_string):
    global first_leaf
    #Convert both strings to lower case before checking
    node = first_leaf
    while node != None:
        if (node.name.lower().find(search_string.lower()) > -1 ):
            print "keyword found"
            return node
        node = node.right
    return None
    

'''
Finds my nearest ancestor that is EITHER NP or VP
'''
def find_VP_or_NP_ancestor(keyword_node):
    #We have to go to phrase node. Hence jump 2 parents
    current_node = keyword_node.parent.parent;
    while(current_node != None):
        #Is my ancestor a VP or NP node itself
        if current_node.name == "NP" or current_node == "VP" :
            return current_node
        #Does my ancestor have either VP or NP as one of the children
        else:
            for child in current_node.children:
                if child.name == "NP" or child.name == "VP":
                    return current_node
        current_node = current_node.parent
    return None

'''
Finds the nearest ancestor that has BOTH NP and VP as children
'''
def find_VP_and_NP_ancestor(keyword_node):
    #We have to go to phrase node. Hence jump 2 parents
    current_node = keyword_node.parent.parent;
    while(current_node != None):
        found_NP = 0;
        found_VP = 0;
        for child in current_node.children:
            if child.name == "NP":
                found_NP = 1
                node_NP = child
            elif child.name == "VP":
                found_VP = 1
                node_VP = child
        if (found_NP == 1 and found_VP == 1):
            #print current_node.name
            return current_node
        current_node = current_node.parent
    return None
    
'''
Dummy funtion for testing various outputs
'''
def trigger_headline_for_each_word_in_sentence(search_string, FILE, fout):
    #OUTPUT_FILE=sys.stdout
    f = open(FILE,"r")
    #fout = open(OUTPUT_FILE,"w", 1)
    
    fout.write("***********************************************\n")
    fout.write("SENTENCE|KEYWORD|NP_OR_VP_TITLE|NP_AND_VP_TITLE\n")
    fout.write("***********************************************\n")
    
    for line in f:
        mySentences = line.split('.')
        for sentence in mySentences:
            sentence = remove_beginning_extraneous_characters(sentence)
            f_stanford_input = open(STANFORD_PARSER_INPUT_SENTENCE_FILE,"w")
            f_stanford_input.write(sentence)
            f_stanford_input.close()
            os.system(STANFORD_PARSER_EXEC+" "+STANFORD_PARSER_INPUT_SENTENCE_FILE+"  > "+STANFORD_PARSER_OUTPUT_FILE)             
            ROOT = make_tree(STANFORD_PARSER_OUTPUT_FILE)
            global first_leaf
            node = first_leaf
            while node != None:
                word = node.name
                keyword_node = node

                if word.lower() in IGNORE_KEYWORDS_SET:
                    node = node.right
                    continue
                fout.write(sentence)
                #print_all_leaves()
                fout.write("|")
                fout.write(word)
                fout.write("|")
                    
                if (keyword_node != None):
                    #find ancestor having both NP and VP at the same level
                    ancestor = find_VP_or_NP_ancestor(keyword_node)
                    leaves_list = ""
                    if (ancestor == None):
                        # "No suitable ancestor found!"
                        leaves_list = populate_leaves_list(ROOT, leaves_list)
                    else:
                        leaves_list = populate_leaves_list(ancestor, leaves_list)
                    fout.write(remove_beginning_extraneous_characters(leaves_list))    
                    fout.write("|")
                    ancestor = find_VP_and_NP_ancestor(keyword_node)
                    leaves_list = ""
                    if (ancestor == None):
                        # "No suitable ancestor found!"
                        leaves_list = populate_leaves_list(ROOT, leaves_list)
                    else:
                        leaves_list = populate_leaves_list(ancestor, leaves_list)
                    
                    fout.write(remove_beginning_extraneous_characters(leaves_list))    
                    
                
                    
                else:
                    fout.write("Keyword Not Found. Should never reach here since the keyword featured in a sentence")
                fout.write("\n")
                
                node = node.right
#populate_leaves_list(ROOT)
                
                
    
trigger_headline_for_each_word_in_sentence(SEARCH_TERM, INPUT_FILE, sys.stdout)    

'''
identify_keyword_sentence_in_file(SEARCH_TERM, INPUT_FILE)

os.system(STANFORD_PARSER_EXEC+" "+STANFORD_PARSER_INPUT_SENTENCE_FILE+"  > "+STANFORD_PARSER_OUTPUT_FILE)             

ROOT = make_tree(STANFORD_PARSER_OUTPUT_FILE)

#print_all_leaves()

keyword_node = find_keyword_node(SEARCH_TERM)

if (keyword_node != None):
    #print keyword_node.name
    ancestor = find_VP_and_NP_ancestor(keyword_node)
    populate_leaves_list(ancestor)
else:
    print "Keyword Not Found. Should never reach here since the keyword featured in a sentence."
#populate_leaves_list(ROOT)
'''

'''Closing comments 26Feb : Have to also feature an N-gram phrase's common ancestor. 
For that, I can print the path from root till each keyword node, then find the first 
node where even one of them diverges. This can be passed as a list to the make_tree
func and the return value from the func can also be a list which in turn is passed to find_VP_and_NP_ancestor'''

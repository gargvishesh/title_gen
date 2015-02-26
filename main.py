#! /usr/bin/python

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
import os
__author__ = "dsluser"
__date__ = "$22 Feb, 2015 5:11:09 PM$"

#if __name__ == "__main__":
#   print "Hello World";
TYPE_PHRASE = 0
TYPE_POS = 1
TYPE_LEAF = 2
LEAF = 1
STANFORD_PARSER_EXEC="/home/dsluser/Desktop/Natural_Language_Processing/stanford-parser-full-2015-01-30/lexparser.sh"
INPUT_FILE='/home/dsluser/Desktop/Natural_Language_Processing/stanford-parser-full-2015-01-30/input'
STANFORD_PARSER_INPUT_FILE = '/home/dsluser/Desktop/Natural_Language_Processing/stanford-parser-full-2015-01-30/stanford_parser_input'
STANFORD_PARSER_OUTPUT_FILE='/home/dsluser/Desktop/Natural_Language_Processing/stanford-parser-full-2015-01-30/stanford_parser_output'
SEARCH_TERM = "manap"


class TreeNode:
    def __init__(self):    
        self.indent = -1
        self.should_print = -1
        self.in_keyword_path = 0
        self.parent = -1
        self.children = []
        self.type = 0
        self.name = ""
    
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
        
            
    def insert_POS_node(self, name):
        #if more indented means it is the child of the previous element
        #print "leaf_call"
        new_node = TreeNode()
        new_node.type = TYPE_POS
        new_node.name = name    
        new_node.parent = self
        self.children.append(new_node)
        #print "Parent:", self.name, "Child:", name 
        return new_node
    
    def insert_leaf_node(self, name):
        #if more indented means it is the child of the previous element
        #print "leaf_call"
        new_node = TreeNode()
        new_node.type = TYPE_LEAF
        new_node.name = name    
        new_node.parent = self
        #print "Parent:", self.name, "Child:", name 
        self.children.append(new_node)
        return new_node
        
def remove_closing_braces(name):
    while name[-1] == ')':
        name = name[:-1]
    return name


'''
Reads the raw text file and identifies the sentence in which the phrase features.
Dumps this sentence to a separate file so that the stanford parser can parse it
and dump its output for further processing
'''
def identify_keyword_sentence(search_string):
    print "Keyword: ",search_string
    f = open(INPUT_FILE,"r")
    fout = open(STANFORD_PARSER_INPUT_FILE,"w")
    for line in f:
        print line
        mySentences = line.split('.')
        for sentence in mySentences:
            if (sentence.lower().find(search_string.lower()) > -1):
                fout.write(sentence)
                print "Keyword sentence found"
                return
    
    print "Keyword sentence not found"
    

'''
Constructs a tree by parsing the indented output dump from stanford_PCFG_parser.
Also keeps track of where it found the search_string that was passed as argument 
to this function
and returns a pointer to that node for future use.
'''
def make_tree(search_string):    
    x=TreeNode()
    ROOT=x
    search_string_found = 0
    return_keyword_node = None
    f = open(STANFORD_PARSER_OUTPUT_FILE,"r") 
       
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
            keyword = word_list[0][1:] #get the phrase of the line

            #Vishesh: Not necessary that the beginning of each line is a phrase
            if (len(word_list) < 2):
                x = x.insert_phrase_node(keyword, line_indent)
                word_list = word_list[1:]
            elif(word_list[1][0] == '('):
                x = x.insert_phrase_node(keyword, line_indent)
                word_list = word_list[1:]
            ###Vishesh TODO: check for more than 2 leaf nodes at the same level
            else:
                '''Note: shouldn't update x itself, otherwise the next child of 
                parent phrase of this POS will get messed up'''
                POS_node = x.insert_POS_node(keyword)
                keyword = remove_closing_braces(word_list[1][:-1])
                leaf_node = POS_node.insert_leaf_node(keyword)
                #Convert both strings to lower case before checking
                if (search_string_found == 0 and keyword.lower().find(search_string.lower()) > -1 ):
                    search_string_found = 1
                    return_keyword_node = leaf_node
                word_list = word_list[2:]



    return (ROOT, return_keyword_node)

'''
Prints all the leaves of the tree rooted at the root pointed to by the argument
'''
def print_tree(root):
    if (root.type == TYPE_LEAF):
        print root.name
    else:
        for child in root.children:
            print_tree(child)

def find_ancestor(keyword_node):
    #We have to go to phrase node. Hence jump 2 parents
    current_node = keyword_node.parent.parent;
    while(keyword_node != None):
        found_NP = 0;
        found_VP = 0;
        for child in current_node.children:
            if child.name == "NP":
                found_NP = 1
                node_NP = child
                break
        for child in current_node.children:
            if child.name == "VP":
                found_VP = 1
                node_VP = child
                break
        if (found_NP == 1 and found_VP == 1):
            #print current_node.name
            return current_node
        current_node = current_node.parent
    
    
identify_keyword_sentence(SEARCH_TERM)
os.system(STANFORD_PARSER_EXEC+" "+STANFORD_PARSER_INPUT_FILE+"  > "+STANFORD_PARSER_OUTPUT_FILE)             

(ROOT, keyword_node) = make_tree(SEARCH_TERM)
if (keyword_node != None):
    #print keyword_node.name
    ancestor = find_ancestor(keyword_node)
    print_tree(ancestor)
else:
    print "Keyword Not Found. Should never reach here since found keyword sentence."
#print_tree(ROOT)

'''Closing comments 26Feb : Have to also feature an N-gram phrase's common ancestor. 
For that, I can print the path from root till each keyword node, then find the first 
node where even one of them diverges. This can be passed as a list to the make_tree
func and the return value from the func can also be a list which in turn is passed to find_ancestor'''

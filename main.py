#! /usr/bin/python

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "dsluser"
__date__ = "$22 Feb, 2015 5:11:09 PM$"

#if __name__ == "__main__":
#   print "Hello World";
TYPE_PHRASE = 0
TYPE_POS = 1
TYPE_LEAF = 2
LEAF = 1
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
            print "Parent:", self.name, "Child:", name 
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
        print "Parent:", self.name, "Child:", name 
        return new_node
    
    def insert_leaf_node(self, name):
        #if more indented means it is the child of the previous element
        #print "leaf_call"
        new_node = TreeNode()
        new_node.type = TYPE_LEAF
        new_node.name = name    
        new_node.parent = self
        print "Parent:", self.name, "Child:", name 
        self.children.append(new_node)
        
            
def leafify(name):
    while name[-1] == ')':
        name = name[:-1]
    return name


        
def make_tree():    
    x=TreeNode()
    f = open("/home/dsluser/tmp","r") #opens file with name of "test.txt"
    myList = []

    for line in f:
        myList.append(line)

    for line in myList:
        print line

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
                POS_node.insert_leaf_node(leafify(word_list[1][:-1]))
                word_list = word_list[2:]



    print"=====End of Orig====="

make_tree()

###Vishesh: Closing comment - :: is a leaf without a phrase in the same line. This is creating a problem
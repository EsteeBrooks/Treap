import pytest
import random


# A Treap is a combination between a Binary Search Tree and a Heap. 
# It is partially a BST (Binary Search Tree) in that its keys are ordered 
# so that any key k is in-order. This means the key of the k's left child < k's key 
# and k's key < the key of k's right child.
# It is partially a Heap because the priorties of each node are in heap-order, 
# meaning any prioty is > its two children's priorities. 
# This means the tree's root will be the highest priorty node and the rest of 
# the tree is a BST.

# This treap can only use strings as its keys 

# This code utalizes code from Professor Alan Broder's Data Structures classes 
# in Stern College. Also the structure of this code is based on the artical titled 
# "Randomized Search Trees" by Raimund Seidel and Cecilia R. Aragon 
# (Artical can be found here: http://faculty.washington.edu/aragon/pubs/rst96.pdf)

#Invidual class for each node in the treap:
class Node(object):
    def __init__(self, k):
        self.key = k
        self.leftChild = self.rightChild = None 
        # proirities are not explicitly stored as they are the hash value of 
        # the keys and can be easily accessed by rehashing the key's value

    def __str__(self):
        return "{" + str(self.key) + "}" 
    
class Treap(object):
    def __init__(self):
        self.__root = None
        self.__nElems = 0 
        # setup a list of random 7-bit values to be used by BitHash. 7-bit is 
        # the suggested amount based on the artical above:
        self.__bits = [random.getrandbits(7) for i in range (7*1024)] 
    
    # Returns the number of nodes in the tree:
    def __len__(self): return self.__nElems
    
    # Returns the priority value of a node, based on node's key
    def bitHash(self, key, h = 0):
        for c in key: 
            h  = (((h << 1) | (h >> 63)) ^ self.__bits[ord(c)]) 
            h &= 0xffffffffffffffff
        return h
    
    # Insert a new node method:
    def insert(self, k):
        # remember nElems to see if it changed due to insert
        temp = self.__nElems
        self.__root = self.__insert(self.__root, k)
        # if the insert failed (due to duplicate key), 
        # then nElems will not have changed. 
        return temp != self.__nElems    

    def __insert(self, cur, k):
        # Recursively try to insert into tree at cur using key and BST rules.
        # Before returning back to the top, rotate up based on the Heap rules
        # using the priority values.
        # Returns a reference to cur, which is the orginal cur or a new node if 
        # cur was None. 
               
        # Empty tree, so just insert the node. No rotations needed. 
        if not cur:
            self.__nElems += 1
            return Node(k)
        
        # Insert k in the left or right branch as appropriate:
    
        if k < cur.key: 
            cur.leftChild  = self.__insert(cur.leftChild, k)
            
            #Rotate right if cur has a higher priority that k
            if self.bitHash(cur.leftChild.key) > self.bitHash(cur.key):
                # Rotatate right:
                tmp = cur.leftChild
                cur.leftChild = tmp.rightChild
                tmp.rightChild = cur
                cur = tmp
            
        elif k > cur.key:            
            cur.rightChild = self.__insert(cur.rightChild, k)
            
            #Rotate left if cur has a higher priority that k
            if self.bitHash(cur.rightChild.key) > self.bitHash(cur.key):
                # Rotatate left:
                tmp = cur.rightChild
                cur.rightChild = tmp.leftChild
                tmp.leftChild = cur
                cur = tmp

        # at this point, k was inserted into the correct branch,
        # or it wasn't inserted since the key k was already there
        return cur

        
    # This method finds the Node associated with a key. As well, it finds the 
    # Node of the key's parent, which will be used in the delete method:
    def find(self, k, forDelete=False): 
        # start at the root
        current = self.__root  
        
        # If this find is for the delete method, create a node to keep track of 
        # parent of cur and a varible to keep track of if the node is from a 
        # left or right pointer: 
        if forDelete == True:
            parent = None 
            leftOrRight = None 
            
        # while we haven't found the key
        while current and k != current.key:
            
            # If forDelete is True, save the parent of the next node
            if forDelete == True: parent = current
            
            # Decide if you should go left or right down the tree: 
            if k < current.key: 
                
                # If forDelete is True, update leftOrRight:
                if forDelete == True: forleftOrRight = "left"
                
                # Update current node:
                current = current.leftChild
            
            # The key must be to right of current:
            else:
                # If forDelete is True, update leftOrRight:
                if forDelete == True: leftOrRight = "right"
                
                 # Update current node:
                current = current.rightChild
        
        # If this search is for the delete method, if we found a node matching 
        # the search key, return current, parent, and leftOrRight. Otherwise,
        # return None, None, None for the delete method to work:
        if forDelete == True:
            if current: return current, parent, leftOrRight
            else: return None, None, None
        
        # If this is a normal search, return current if its not None. Otherwise,
        # return error message:
        if current: return current.key, self.bitHash(current.key)
        else: return "Key not Found"        
           
    def delete(self, k):
        # Find cur and the information about cur that is needed to delete:
        cur, parent, leftOrRight = self.find(k, True)
        
        # If cur is None, the tree is empty and key is not in tree:
        if not cur: return "Key not Found"
        
        # Loop until we get cur to be leaf:
        while cur.rightChild or cur.leftChild:
            
            # If cur has a left AND right child, see which has higher priority.
            # If left has higher priority or there is no right child, switch 
            # the node to be deleted with the left child. 
            if (cur.leftChild and cur.rightChild and \
               self.bitHash(cur.leftChild.key) > self.bitHash(cur.rightChild.key)) \
               or (not cur.rightChild):

                tmp = cur.leftChild
                cur.leftChild = tmp.rightChild
                tmp.rightChild = cur
                
                # Point the parent of cur to tmp, making sure to use the correct
                # leftChild or rightChild pointer:
                self.replaceTmpsParent(parent, leftOrRight, tmp)
                
                # Update the leftOrRight varible to be "right" and the parent
                # varible to tmp so the next rotation will be have correct infomation:
                leftOrRight = "right" 
                parent = tmp
                    
            # If right has higher priority or there is no left child, switch 
            # the node to be deleted with the right child. 
            elif (cur.leftChild and cur.rightChild and \
               self.bitHash(cur.leftChild.key) < self.bitHash(cur.rightChild.key)) \
               or (not cur.leftChild):
                
                tmp = cur.rightChild
                cur.rightChild = tmp.leftChild
                tmp.leftChild = cur
                
                # Point the parent of cur to tmp, making sure to use the correct
                # leftChild or rightChild pointer:
                self.replaceTmpsParent(parent, leftOrRight, tmp)
                
                # Update the leftOrRight varible to be "left" and the parent
                # varible to tmp so the next rotation will be have correct infomation:
                leftOrRight = "left"
                parent = tmp 
                          
        # set parent's child that points to cur to None to delete cur:
        if leftOrRight == "left":
            parent.leftChild = None          
        if leftOrRight == "right":
            parent.rightChild = None 
            
        # Decrement total amount of nodes 
        self.__nElems -= 1   
        
    # A method in the delete method. Used to point the correct pointer of the parent 
    # varible to tmp after a rotation:
    def replaceTmpsParent(self, parent, leftOrRight, tmp):
        # Find out which pointer to use for the parent to point to tmp.
        # If leftOrRight is left, use leftChild of parent to point to tmp:
        if leftOrRight == "left" and parent:
            parent.leftChild = tmp
            
        # If leftOrRight is right, so use rightChild of parent to point to
        # tmp:
        elif leftOrRight == "right" and parent:
            parent.rightChild = tmp
            
        # Otherwise parent, and now tmp, must be a root node:
        else:
            self.__root = tmp
    
    # Method used to print the tree:    
    def printTree(self):
        self.pTree(self.__root, "ROOT:  ", "")
        print()
        
    # Method used by printTree method to print out the tree recursively:  
    def pTree(self, n, kind, indent):
        print("\n" + indent + kind, end="")
        if n: 
            # For printing purposes, hash the piority so the code can be 
            # verified to work: 
            print(n, self.bitHash(n.key), end="")
            if n.leftChild:
                self.pTree(n.leftChild,  "LEFT:   ",  indent + "    ")
            if n.rightChild:
                self.pTree(n.rightChild, "RIGHT:  ", indent + "    ")  
    
    # Method used to check if the tree is in BST order according to its keys:   
    def BSTOrder(self, cur="Start"):
        if cur == "Start": cur = self.__root
        if cur:
            self.BSTOrder(cur.leftChild)
            self.BSTOrder(cur.rightChild)
            if cur.rightChild and cur.rightChild.key < cur.key: return False
            if cur.leftChild and cur.leftChild.key > cur.key: return False
        return True 
    
    # Method used to check if the tree is in heap order according to its priorties:
    def heapOrder(self, cur="Start"):
        if cur == "Start": cur = self.__root        
        if cur:
            self.heapOrder(cur.leftChild)
            self.heapOrder(cur.rightChild)
            if cur.rightChild and self.bitHash(cur.rightChild.key) > self.bitHash(cur.key): return False
            if cur.leftChild and self.bitHash(cur.leftChild.key) > self.bitHash(cur.key): return False
        return True 
                
            

#def __main():
    #theTree = Treap()
    
    #theTree.insert("V")
    #theTree.insert("G")
    #theTree.insert("Z")
    #theTree.insert("Harold")
    #theTree.insert("James")
    #theTree.insert("David")
    #theTree.printTree()
    #print(theTree.find("James"))
    #theTree.delete("James")
    #theTree.printTree()
 
#if __name__ == '__main__':
    #__main()

#Function to be used in the pytests that creates a randomly filled treap:
def initTreapRandom():
    t = Treap()
    
    NUMPTS = 800  # the number of points to insert into the Treap 
    
    for c in range(NUMPTS): 
        # Choose a random number:
        x = random.random()
        
        # Set h to to the value of that random number in a string: 
        h = str(x)
        
        # Insert the priorty of x to the heap:
        t.insert(h)
    return t

#Pytests:

#Make sure a search on an empty AVL returns "Key not Found":
def test_searchEmpty():
    t = Treap()
    ans = t.find("")
    assert ans == "Key not Found" 
    
#Make sure a tree with one Node has a len of 1:
def test_sizeOne():
    t = Treap()
    t.insert("EARL")
    assert len(t) == 1 
    
#Make sure a tree with 800 random inserts has a len of 800:
def test_len800():
    t = initTreapRandom()
    assert len(t) == 800  

#Make sure tree with one element deletes correctly
def test_sizeOneDelete():
    t = Treap()
    t.insert("EARL")
    t.delete("EARL")
    assert len(t) == 0
  
#Make sure all keys are in heap order after inserting a bunch
def test_insertBunchHeap():
    t = initTreapRandom()
    assert t.heapOrder()
    
#Make sure all keys are in BST order after inserting a bunch
def test_insertBunchBST():
    t = initTreapRandom()
    assert t.BSTOrder()

#Make sure all keys are in heap and BST order after inserting and deleting a bunch a bunch
def test_insertDeleteBunchHeap():
    t = initTreapRandom()
    for c in range(20): 
        # Choose a random number:
        x = random.random()
        
        # Set h to to the value of that random number in a string: 
        h = str(x)
        
        # Insert the priorty of x to the heap:
        t.delete(h)
    assert t.heapOrder()
    assert t.BSTOrder()

pytest.main(["-v", "-s", "test_treap.py"])
   
 
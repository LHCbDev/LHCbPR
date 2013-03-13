#!/usr/bin/env python

import sys
import re

#
# Parser for the TimingAuditor logfile or ROOT dump
#
################################################################################
class TimingTree:
    """ Class responsible for parsing the TimingAuditor log from the
    Gaudi run  log files """
    def __init__(self, root_name, node_data, node_childs, node_entries, node_ids):
        self.finalnodes = []
        self.generateTree(root_name, self.finalnodes, None, node_data, node_childs, node_entries, node_ids, 0)
        self.root = self.finalnodes[0]
        
        self.root.rankChildren()
    
    def generateTree(self, node_name, finalnodes, lastparent, node_data, node_childs, node_entries, node_ids, level):     
      current_node = Node(node_ids[node_name], node_name, node_data[node_name], node_entries[node_name], level, lastparent)
      finalnodes.append(current_node)
      
      level +=1
      if node_name in node_childs:
          lastparent = current_node
          for child in node_childs[node_name]:
              self.generateTree(child, finalnodes, lastparent, node_data, node_childs, node_entries, node_ids, level)
      else:
          return

    def getRoot(self):
        """ returns the root of the tree """
        return self.root

    def getHierarchicalJSON(self):
        return "[" + self.root.getJSON() + "]"

    def getFlatJSON(self):
        ct = 1
        json="["
        for c in self.root.getAllChildren():
            if ct > 1:
                json += ",\n"
            json += c.getJSON(False)
            ct += 1
        json += "]"
        return json 
    
    def getFullCSV(self):
        ct = 1
        
        csv="code,name,rank,mrank,childrenTotal,perTotal,perLevel,avgtime,total,entries,parentCode \n"
        for c in self.root.getAllChildren():
            if ct > 1:
                csv += "\n"
            csv += c.getCSV()
            ct += 1
        return csv 
    
    def getjqGrid(self):
        grid = {}
        
        rows = []
        for c in self.root.getAllChildren():
            rows.append(c.getjqGridCell())
        
        grid['rows'] = rows
        return grid
    
    def getActualTimeTree(self):
        singleLevelData = []
        perTotalDict = {}
        
        singleLevelData.append([ "Algname", "Parent", "ActualTime"])
        for c in self.root.getAllChildren():
            #perTotal List is just a list like : [ 'EVENT_LOOP' , '100%' ]
            treeData, perTotalList = c.getActualTimeData(self.root.name)
            singleLevelData.append(treeData)
            perTotalDict[perTotalList[0]] = perTotalList[1]
            
        return ( singleLevelData, perTotalDict )
    
    def findByName(self, name):
        return self.root.findByName(name)

    def getTopN(self, n):
        """ Get the top N ranked algorithms"""
        return sorted(self.root.getAllChildren(), key=Node.getRank)[:n]

    def getAllSorted(self):
        """ Get the top N ranked algorithms"""
        return sorted(self.root.getAllChildren(), key=Node.getRank)


#
# Class representing the Nodes in the Algorithm tree
#
################################################################################
class Node:
    """ Representation of an algorithm or sequence """

    @classmethod
    def getActualTimeUsed(cls, o):
        return o.actualTimeUsed()


    @classmethod
    def getRank(cls, o):
        return o.rank


    def __init__(self, id, name, value, entries, level, parent=None):
        """ Constructor """
        self.id = id
        self.name = name
        self.rank = 0
        self.value = float(value)
        self.entries = entries
        self.total = self.value * self.entries
        self.children = []
        self.parent = parent
        self.level = level
        self.eventTotal = None
        if parent != None:
            parent.children.append(self)
    
    def getParentName(self):
        if not self.parent:
            return None
        
        return self.parent.name
    
    def getParentID(self):
        if not self.parent:
            return None
        
        return self.parent.id
    
    def findByName(self, name):
        """ Find an algorithm in the subtree related to the Node  """
        if self.name == name:
            return self

        for c in self.children:
            tmp = c.findByName(name)
            if tmp != None:
                return tmp
        return None


    def actualTimeUsed(self):
        """ returns the CPU time actually used in the sequence,
        excluding time used by the children """
        actualTime = self.total - self.getSumChildrenTime()
        if actualTime < 0:
            return 0
        else:
            return actualTime 

    def getAllChildren(self):
        """ Navigate the tree to rturn all the children"""
        cdren = []
        cdren.append(self)
        for c in self.children:
            cdren += c.getAllChildren()
        return cdren

    def getMinChildrenRank(self):
        """ Get the lowest rank in all the children """
        m = self.rank
	for c in self.children:
            if c.getMinChildrenRank() < m:
                 m = c.getMinChildrenRank()
        return m
    

    def getSumChildrenTime(self):
        """ Get the sum of CPU time spent by the children """
        tmptotal = 0.0
        for c in self.children:
            tmptotal += c.total
        return tmptotal
            
    def perLevel(self):
        """ Percentage of time spent in this algo/seq over the
        time used by the parent """
        if self.parent != None:
            if self.parent.total == 0:
                return 0.0
            return round((self.total * 100.0)/self.parent.total,2)        
        else:
            return 100.0

    def getEventTotal(self):
        """ Get the total time spent in the EVENT LOOP """
        if self.eventTotal != None:
            return self.eventTotal

        if self.parent is None:
            self.eventTotal = self.total
            return self.eventTotal
        else:
            self.eventTotal = self.parent.getEventTotal()
            return self.eventTotal

    def perTotal(self):
        """ percentage time spent in this algorithm vs the TOTAL time"""
        return round(self.total * 100.0 / self.getEventTotal(),2)

    def getfullname(self):
        """ Returns the complete path flatened joined by '-' """
        if self.parent != None:
            return self.parent.getfullname() + "-" + self.name
        else:
            return self.name

    def getJSON(self, hierarchical=True):
        """ Returns teh JSON representation of thios node """
        cjson = ""

        if hierarchical and len(self.children) > 0:
            cjson = ', "children":[%s]' % self._childrenjson()

        tmpl = '{"code":%d, "name":"%s", "rank":%d, "mrank":%d, "childrenTotal":%.2f, "perTotal":%.2f, "perLevel":%.2f, "avgtime":%.2f, "total":%.2f, "entries":%d '
        vals =  [ self.id, self.name, self.rank, self.getMinChildrenRank(), self.getSumChildrenTime(), self.perTotal(), 
                  self.perLevel(), self.value, self.total, self.entries ]
        if self.parent != None:
            tmpl += ', "_parentCode":%d %s}'
            vals.append(self.parent.id)
            vals.append(cjson)
        else:
            tmpl += ' %s}'
            vals.append( cjson)

        return tmpl % tuple(vals)

    
    def getCSV(self, hierarchical=True):
        """ Returns CSV representation of this node """

        tmpl = '%d,%s,%d,%d,%.2f,%.2f,%.2f,%.2f,%.2f,%d'
        vals =  [ self.id, self.name, self.rank, self.getMinChildrenRank(), self.getSumChildrenTime(), self.perTotal(), 
                  self.perLevel(), self.value, self.total, self.entries ]
        if self.parent != None:
            tmpl += ',%d'
            vals.append(self.parent.id)

        return tmpl % tuple(vals)
    
    def getActualTimeData(self, customParent=None):
        """ Returns CSV representation of this node """

        if not customParent:
            parentName = self.getParentName()
        else:
            parentName = customParent
        
        if self.name == customParent:
            parentName = None
        
        #return the actualTreeMap data and also a list with the name and the perTotal,
        #this will be used to display a tooltip in the analyse template showing the persetange of the time
        return ( [ self.name, parentName, self.actualTimeUsed() ], [ self.name, str(self.perTotal())+'%' ] )
    
    def doesNotHaveChildren(self):
        if self.children:
            return False
        
        return True
    
    def getjqGridCell(self):
        return { 'id' : str(self.id), 'cell' : [ str(self.id), self.name, self.value , self.rank, self.entries,
                                                self.perTotal(), self.perLevel(), self.getSumChildrenTime(),
                                                self.level, self.getParentID(), self.doesNotHaveChildren(), 
                                                self.doesNotHaveChildren() ] }
    
    def _childrenjson(self):
        """ Util function to return the JSON reprentation of the children of the node """
        ct = 1
        json=""
        for c in self.children:
            if ct > 1:
                json += ",\n"
            json += c.getJSON()
            ct += 1
        return json

    def rankChildren(self):
        """ Actually sort of the children of this node and set their rank.
        This MUST be called on the tree before using teh rank value"""
        l = sorted(self.getAllChildren(), key=Node.getActualTimeUsed, reverse=True)
        for i, n in enumerate(l):
            n.rank = i + 1
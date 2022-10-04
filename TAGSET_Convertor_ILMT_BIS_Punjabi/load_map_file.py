import xml.dom.minidom
from sys import argv


def LoadMapFile(mapFile):  
    '''Loads the specified "mapFile" into the memory as a data-structure for better run-time access'''
    mapData = xml.dom.minidom.parse(mapFile)
    mapSet = {}
    for scheme in mapData.childNodes: 
        for rule in scheme.childNodes:
            if rule.childNodes != ():
                sourceTag = ""
                destinationTag = []
                expression = []
                for tag in rule.childNodes:
                    if tag.nodeType == tag.ELEMENT_NODE: 
                        if tag.localName == "sourcetag":    
                            sourceTag = tag.childNodes[0].nodeValue
                        if tag.localName == "destinationtag":
                            destinationTag.append(tag.childNodes[0].nodeValue)
                        if tag.localName == "expression":
                            expression.append(tag.childNodes[0].nodeValue)
                if expression != []:
                    mapSet[sourceTag] = expression
                else: 
                    mapSet[sourceTag] = destinationTag
    return mapSet


if __name__ == '__main__':
    mapFile = argv[1]
    mapSet = LoadMapFile(mapFile)
    print(mapSet)

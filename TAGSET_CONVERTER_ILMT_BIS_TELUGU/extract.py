#!/usr/bin/python
##########################################################################
#			 							#
#	LANGUAGE TECHNOLOGY AND REASEARCH CENTRE , IIIT-HYDERABAD		#
#										#
##########################################################################

from __future__ import division
import string
import re
import sys
import os
import xml.dom.minidom


class Converter():

    def __init__(self):
        self.wordQueue = []
        self.maxQueueLength = 5
        for word in range(0, self.maxQueueLength):
            self.wordQueue.append("NULL")

    def ProcessDocument(self, document, mapDict, outputDoc, wordDict):
        '''Document Processor - To iterate lines and send them for Analysis , also counts Sentences in the file'''

        sentenceTotal = 0
        sentencePattern = "<Sentence"
        lineNumber = 0
        for line in document:
            lineNumber += 1
            if sentencePattern in line:
                sentenceTotal += 1
                output = line
            else:
                output = self.SentenceAnalyser(line, mapDict, wordDict)
            outputDoc.write(output)
        return sentenceTotal

    def SentenceAnalyser(self, sentence, mapDict, wordDict):
        '''Extracts the fields and maps the respective target tag according to mapFile'''
        output = sentence
        stripSentence = sentence.strip()
        if len(stripSentence) == 0:
            output = "\n"
        else:
            if stripSentence[0] == "<":
                output = sentence
            else:
                splitSentence = stripSentence.split('\t')
                if len(splitSentence) != 0 and splitSentence[0] != "))":
                    if len(splitSentence) > 1 and splitSentence[1] != "((" and len(splitSentence) > 2 and splitSentence[2] in mapDict.keys():
                        # For one-to-one mapping
                        if len(mapDict[splitSentence[2]]) == 1:
                            if mapDict[splitSentence[2]][0][0] == "{":
                                splitSentence[2] = self.ExpressionRecognizer(
                                    splitSentence[2], mapDict[splitSentence[2]][0])
                            else:
                                splitSentence[2] = mapDict[splitSentence[2]][0]
                        else:
                            splitSentence[2] = self.GetTag(
                                splitSentence[1], mapDict[splitSentence[2]], wordDict)  # For one-to-many mapping
                        self.wordQueue.pop(0)
                        self.wordQueue.append(splitSentence[2])
                    output = self.OutputFormatter(splitSentence)
        return output

    def GetTag(self, word, tagList, wordDict):
        '''Resolves many-to-one mapping through word-list'''

        outTag = tagList[0]
        for tag in tagList:
            for dictWord in wordDict[tag]:
                if word == dictWord:
                    outTag = tag
                    return outTag
        return outTag

    def OutputFormatter(self, splitSentence):
        '''Formats the sentence back into it's original form'''
        if len(splitSentence) > 2:
            output = splitSentence[
                0] + "\t" + splitSentence[1] + "\t" + splitSentence[2] + "\t"
        else:
            output = '\t'.join([splitSentence[x]
                                for x in range(0, min(2, len(splitSentence)-1))])
        for iterator in range(3, len(splitSentence)-1):
            output += splitSentence[iterator] + " "
        if len(splitSentence) > 3:
            output += splitSentence[len(splitSentence)-1]
        output += '\n'
        return output

    def LoadMapFile(self, mapFile):
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
                                destinationTag.append(
                                    tag.childNodes[0].nodeValue)
                            if tag.localName == "expression":
                                expression.append(tag.childNodes[0].nodeValue)
                    if expression != []:
                        mapSet[sourceTag] = expression
                    else:
                        mapSet[sourceTag] = destinationTag
        return mapSet

    def LoadWordlist(self, filePath):
        '''Loads the words from the Word Lists into the memory as a data-structure for better run-time access'''

        targetFiles = os.listdir(filePath)
        wordDict = {}
        for fileName in targetFiles:
            if '.' in fileName:
                fileName = fileName[: fileName.rfind('.')]
            wordList = []
            listFile = open(
                filePath + fileName, encoding="utf-8", mode="r")
            for word in listFile:
                if word != "":
                    wordList.append(word.strip())
            wordDict[fileName] = wordList
            listFile.close()
        return wordDict

    def FileHandler(self, args):
        '''Handles the files involved in the process'''

        testList = os.listdir(args.inputPath)
        if not os.path.isdir(args.outputPath):
            os.mkdir(args.outputPath)
        mapFileName = args.mapFile							# Name of the Map file.
        mapDict = self.LoadMapFile(mapFileName)
        wordListPath = args.listPath
        wordListDict = self.LoadWordlist(wordListPath)
        for fileName in testList:
            name = args.inputPath + fileName
            # Name of the destination file , after conversion.
            newName = args.outputPath + fileName + ".new"
            sourceFile = open(name, encoding="utf-8", mode="r")
            targetFile = open(newName, encoding="utf-8", mode="w")
            sentences = self.ProcessDocument(
                sourceFile, mapDict, targetFile, wordListDict)
            print(name, newName, "converted")
            print("Total Sentences : ", sentences, "\n")
            sourceFile.close()
            targetFile.close()

    def ExpressionRecognizer(self, sourceTag, expression):
        '''
        For RDP, if the last tag is a symbol (mostly hyphen),
        RDP is resolved to the second last tag,
        otherwise it gets resolved to the last tag.
        '''
        expression = expression[1: -1]
        bothSides = expression.split("=>")
        leftSide = bothSides[0]
        rightSide = bothSides[1]
        leftSideSplit = leftSide.split("-")
        rightSideSplit = rightSide.split("-")
        resolvedTag = ''
        for tagIter in range(0, len(leftSideSplit)):
            tagName = leftSideSplit[tagIter]
            if tagName == str("(" + sourceTag + ")"):
                positionSourceTag = tagIter
        for index in range(positionSourceTag - 1, -1, -1): 
            tagPosition = int(rightSideSplit[index][1:])
            if self.wordQueue[self.maxQueueLength - tagPosition] in ['RD_SYM', 'RD_PUNC']:
                 continue
            else:
                resolvedTag = self.wordQueue[self.maxQueueLength - tagPosition]
                break
        return resolvedTag


def main():
    '''Main code that initializes the sequence'''

    try:
        from argumentParser import ExtractArgumentParser, checkArgs
    except ImportError:
        print("Cannot locate either argumentParser.py or in-built python argparse module. Make sure all the files are in the same folder.")
        exit()

    parserInstance = ExtractArgumentParser()
    args = parserInstance.parser.parse_args()
    checkArgs(args.__dict__)
    converterInstance = Converter()
    converterInstance.FileHandler(args)


if __name__ == "__main__":
    main()

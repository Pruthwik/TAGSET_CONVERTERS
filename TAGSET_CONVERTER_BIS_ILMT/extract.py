#!/usr/bin/python
#################################################################################
#			 							#	
#	LANGUAGE TECHNOLOGY AND REASEARCH CENTRE , IIIT-HYDERABAD		#		
#										#	
#################################################################################

from __future__ import division
import string
import re
import sys
import os
import xml.dom.minidom


class Converter():
	
	def __init__(self):
		self.wordQueue=[] 
		self.maxQueueLength = 5
		for word in range(0, self.maxQueueLength):
			self.wordQueue.append("NULL")

	def ProcessDocument(self, document, mapDict, outputDoc):								

		'''Document Processor - To iterate lines and send them for Analysis , also counts Sentences in the file'''

		sentenceTotal = 0
		sentencePattern="<Sentence"
		lineNumber = 0
		for line in document:
			lineNumber += 1
			if sentencePattern in line:
				sentenceTotal += 1
				output = line
			else:
				output = self.SentenceAnalyser(line, mapDict)				
			outputDoc.write(output)
		return sentenceTotal 

	def SentenceAnalyser(self, sentence, mapDict):
		
		'''Extracts the fields and maps the respective target tag according to mapFile'''
		output = sentence
		stripSentence = sentence.strip()
		if len(stripSentence) == 0:										
			output = "\n"
		else:
			if stripSentence[0] == "<":
				output = sentence
			else: 
				splitSentence = stripSentence.split()
				if len(splitSentence) != 0 and splitSentence[0] != "))":
					if len(splitSentence) > 1 and splitSentence[1]!="((" and len(splitSentence) > 2:
						search_word = splitSentence[2]
						keys = list(mapDict.keys())
						for i in range(len(keys)):
							if search_word in keys[i]:
								splitSentence[2] = mapDict[keys[i]]							
					output = self.OutputFormatter(splitSentence)
		return output

	def OutputFormatter(self, splitSentence):

		'''Formats the sentence back into it's original form'''
		if len(splitSentence) > 2: 
			output = splitSentence[0] + "\t" + splitSentence[1] + "\t" + splitSentence[2] + "\t" 
		else: 
			output = '\t'.join([splitSentence[x] for x in range(0, min(2, len(splitSentence) - 1))])
		for iterator in range(3, len(splitSentence) - 1): 
			output += splitSentence[iterator] + " "	
		if len(splitSentence) > 3: 
			output += splitSentence[len(splitSentence) - 1]
		output += '\n'
		return output

	def LoadMapFile(self, mapFile):	

		'''Loads the specified "mapFile" into the memory as a data-structure for better run-time access'''

		mapData = xml.dom.minidom.parse(mapFile)
		mapSet = {}
		for scheme in mapData.childNodes: 
			for rule in scheme.childNodes:
				if rule.childNodes!=():
					sourceTag = []
					destinationTag = ""
					for tag in rule.childNodes:
						if tag.nodeType == tag.ELEMENT_NODE: 
							if tag.localName == "sourcetag":
								sourceTag.append(tag.childNodes[0].nodeValue)	
							if tag.localName == "destinationtag":
								destinationTag = tag.childNodes[0].nodeValue
					mapSet[tuple(sourceTag)] = destinationTag
		return mapSet

	def FileHandler(self, args):

		'''Handles the files involved in the process'''

		testList = os.listdir(args.inputPath)
		if os.path.isdir(args.outputPath) == False: 
			os.mkdir(args.outputPath)
		mapFileName = args.mapFile							# Name of the Map file.
		mapDict = self.LoadMapFile(mapFileName)
		for fileName in testList:
			print(fileName)
			name = args.inputPath + fileName
			newName = args.outputPath + fileName + ".new"						# Name of the destination file , after conversion.
			sourceFile = open(name, encoding="utf-8",mode="r")
			targetFile = open(newName, encoding="utf-8",mode="w")
			sentences = self.ProcessDocument(sourceFile, mapDict, targetFile)
			print(name , newName, "converted" )
			print("Total Sentences: " , sentences , "\n")
			sourceFile.close()
			targetFile.close()


def main():
	'''
	Pass arguments and call functions here.
	'''
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


if __name__=="__main__": 
	main()

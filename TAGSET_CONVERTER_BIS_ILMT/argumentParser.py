#!/usr/bin/python
#################################################################################
#       		                                                         #       
#       LANGUAGE TECHNOLOGY AND REASEARCH CENTRE , IIIT-HYDERABAD               #               
#                                                                               #       
#################################################################################

import argparse

class ScriptArgumentParser():
        def __init__(self):
                self.parser=argparse.ArgumentParser()
                self.parser.add_argument("-i" , dest="inputPath", default="./dataset/new_files/")
                self.parser.add_argument("-g" , dest="goldPath" , default="./dataset/gold/")

class ExtractArgumentParser() :
	def __init__(self) :
		self.parser = argparse.ArgumentParser(description="Convert Tag files", prog="CONVERTER")
		self.parser.add_argument("-i", dest="inputPath"  )
		self.parser.add_argument("-o", dest="outputPath")
		self.parser.add_argument("-m", dest="mapFile", default="./map.xml")
def checkArgs(args) :
	for each in args: 
		if args[each][-1] != "/" and each != "mapFile":
			args[each] = args[each] + ("/")
	return args

#!/usr/bin/python2.7.6
# packages
import json
import os
import requests
# import urllib
from pprint import pprint
from openpyxl import Workbook #2.2.3
from openpyxl import load_workbook
import re
# import csv
# from collections import defaultdict
from HTMLParser import HTMLParser
import vcf
import gzip
import itertools
from collections import OrderedDict


rsid='' #rs16947 rs1801158 rs4244285 rs4986893 rs5030862 #raw_input('rsid please:')
geneSymbolName=''
''' To remove HTML tags from the Recommendation texts
'''
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)
def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def getGeneSymbolName(rsid):
	''' Converts RsID to geneSymbolName through myvariant.info in iterations at 3 different annotation resources
	'''
	geneNameFromMyVariant = ''
	myvariantRsidRequest = requests.get('http://myvariant.info/v1/query?q='+rsid)
	if myvariantRsidRequest.status_code == requests.codes.ok:
		# print '\nstatus_code ok!:',myvariantRsidRequest.headers['content-type']
		if bool(re.search('[r][s]\d+',rsid)):
			print 'http://myvariant.info/v1/query?q='+rsid
			commit_data = myvariantRsidRequest.json()
			print 'This is the hgvs id from myvariant.info:' ,commit_data['hits'][0]['_id']
			print 'Searching for Genename...'
			try:
				geneNameFromMyVariant=commit_data['hits'][0]['dbsnp']['gene']['symbol']
			except KeyError:
				pass
				# print """KeyError: Key not found in ['hits'][0]['dbsnp']['gene']['symbol']"""
			except TypeError, e:
				print """TypeError: Multiple genes found in ['hits'][0]['dbsnp']['gene']['symbol']""",e
			else:
				print 'Genename found! This is the gene from myvariant.info:' ,commit_data['hits'][0]['dbsnp']['gene']['symbol']
			if geneNameFromMyVariant!='':
				return geneNameFromMyVariant
			try:
				geneNameFromMyVariant=commit_data['hits'][0]['snpeff']['ann'][0]['gene_name']
			except KeyError:
				pass
				# print """KeyError: Key not found in ['hits'][0]['snpeff']['ann'][0]['gene_name']"""
			else:
				print 'Genename found! This is the gene from myvariant.info:' ,commit_data['hits'][0]['snpeff']['ann'][0]['gene_name']
			if geneNameFromMyVariant!='':
				return geneNameFromMyVariant
			try:
				geneNameFromMyVariant=commit_data['hits'][0]['dbnsfp']['genename']
			except KeyError:
				pass
				# print """KeyError: Key not found in ['hits'][0]['dbnsfp']['genename']"""
			else:
				print 'Genename found! This is the gene from myvariant.info:' ,commit_data['hits'][0]['dbnsfp']['genename']
			if geneNameFromMyVariant!='':
				return geneNameFromMyVariant
			try:
				geneNameFromMyVariant=commit_data['hits'][0]['wellderly']['gene']
			except KeyError:
				pass
				# print """KeyError: Key not found in ['hits'][0]['dbnsfp']['genename']"""
			else:
				print 'Genename found! This is the gene from myvariant.info:' ,commit_data['hits'][0]['wellderly']['gene']
			if geneNameFromMyVariant!='':
				return geneNameFromMyVariant
			else:
				'genename not found on myvariant.info'
		else:
			'rsid malformed: ',rsid
	else:
		print '\nstatus_code at myvariant.info not ok!:',myvariantRsidRequest.headers['content-type']
def getHaplotypesFromTranslationtable(rsid):
	for translationTablePerGene in os.listdir('/Users/admin/Dropbox/Privat/00_Masterthesis/pharmGkb_resources/'):
		if translationTablePerGene.endswith('.xlsx') and not translationTablePerGene.startswith('~'): #and translationTablePerGene.startswith(geneSymbolName):
			haplottypeListTemp=[]
			translationTablePerGeneWorkbook = load_workbook('/Users/admin/Dropbox/Privat/00_Masterthesis/pharmGkb_resources/'+translationTablePerGene,read_only=True)
			worksheetTranslationTablePerGene = translationTablePerGeneWorkbook.active
			# print 'Dimensions of the worksheet:',worksheetTranslationTablePerGene.dimensions
			coordinatesOfRsid = ''
			for row in worksheetTranslationTablePerGene.rows:
			    for cell in row:
			    	if isinstance(cell.value,unicode): #dont parse datetime objects
				        if str(cell.value.encode('utf8','ignore')).strip()==rsid: #encoding due to unicode characters, str(unicode) gives unicodeencdoerror
				        	coordinatesOfRsid = cell.coordinate
				        	# print 'coordinates of',str(cell.value).strip(),':',coordinatesOfRsid
			letterOfRsIdCell = ''
			if coordinatesOfRsid!='':
				letterOfRsIdCell = re.search('[A-Z]{1,2}', coordinatesOfRsid).group() #gives the letter of the coordinate
				rowCount = worksheetTranslationTablePerGene.get_highest_row()
				# print 'Haplotypes where the allele is present in:'
				if not letterOfRsIdCell=='':
					for i in range (1,rowCount+1):
						try:
							if worksheetTranslationTablePerGene[letterOfRsIdCell+str(i)].value: #take only non-empty cells
								if bool(re.search('\*\d',str(worksheetTranslationTablePerGene['B'+str(i)].value))): # pattern is star plus a digit then stop because we only want the basic star allels. We search in the B column because it contains the star alleles
									# print geneSymbolName,worksheetTranslationTablePerGene['B'+str(i)].value,'(Alele: ',worksheetTranslationTablePerGene['D'+str(i)].value,')'
									haplottypeListTemp.append(worksheetTranslationTablePerGene['B'+str(i)].value)

						except IndexError, e:
							print e
						except:
							pass
				print 'star alleles list:',haplottypeListTemp
				return haplottypeListTemp
			else:
				# print 'rs id not found in excel file'
				pass

def getBasicStarAlleles(haplottypeListComplete):
	starAllelesListTwoBasicTemp=[]
	if haplottypeListComplete is not None:
		# for starAllele in haplottypeListComplete:
		# 	if bool(re.search('\*[0-9]+$',starAllele)): #only search for * and a number
		# 		starAllelesListTwoBasicTemp.append(starAllele)
		for x in itertools.combinations(haplottypeListComplete,2):
			starAllelesListTwoBasicTemp.append(x)
		# print starAllelesListTwoBasicTemp
		return starAllelesListTwoBasicTemp
	else:
		print 'no haplotypes found'



def printDosingGuidelineFromJsonFile(jsonFileName, starAllelesListTwoBasic):
	'''  takes a json file and searches for the two given star alleles and tries to print all found dosing guidelines
	'''
	# print jsonFileName
	with open('/Users/admin/Dropbox/Privat/00_Masterthesis/pharmGkb_resources/dosingGuidelines.json/'+jsonFileName) as data_file:
		parsedJsonFile = json.loads(data_file.read())
	guidesPresentBool = False
	if 'guides' in parsedJsonFile:
		jsonSnp = OrderedDict()
		for annsLoop in parsedJsonFile['guides'][0]['anns']:
			if 'location' in annsLoop:
				for diplotypeLoop in annsLoop['location']['diplotypes']:
					# if (diplotypeLoop['allele1']=='*1' and diplotypeLoop['allele2']=='*2'):
					# print diplotypeLoop['allele1'],starAllelesListTwoBasic[0],diplotypeLoop['allele1'],starAllelesListTwoBasic[1]
					if (diplotypeLoop['allele1']==starAllelesListTwoBasic[0] and diplotypeLoop['allele2']==starAllelesListTwoBasic[1]):
						guidesPresentBool = True
						# print '\njson file name:',jsonFileName
						if annsLoop['groups'][0]['term'].startswith('Phen'): #Phenotype is supposed to be the first line (see PharmGKB.org website) and if that is the case then BEFORE printing the Phenotype first print information about the DRUG and the Gene name
							print '\nDosing Guideline for:',parsedJsonFile['relatedDrugs'][0]['name'],'and gene name from the guideline json file:',parsedJsonFile['relatedGenes'][0]['symbol'],'and the exact gene name:',parsedJsonFile['relatedGenes'][0]['name'][0:10],'... and diplotype',diplotypeLoop['allele1'],'/',diplotypeLoop['allele2']
						levelOfEvidence=''
						if annsLoop['groups'][0]['term']=='Recommendations':
							levelOfEvidence = '  (Level of Evidence: '+annsLoop['strength']['term']+')'
						print strip_tags(annsLoop['groups'][0]['term']+levelOfEvidence+'  : '+annsLoop['textHtml'][0:60])#[0:30],'...'
						jsonSnp[annsLoop['groups'][0]['term']] = strip_tags(annsLoop['textHtml'][0:60])
			else:
				print 'no diplotypes at all in json file! but there are some guides in the json file!'
				# print 'star alleles not present in json filename, probably there is no evidence'
		if bool(jsonSnp):
			print json.dumps(jsonSnp, indent=4)
	else:
		pass
	return guidesPresentBool

def printDosingGuideline(starAllelesListTwoBasic,geneSymbolName):
	guidesPresentBool = False
	if len(starAllelesListTwoBasic)>=2:
		geneSymbolIterator=cpicIterator=jsonIterator=searchThroughJsonfile=0
		# print 'Searching for Dosing Guidelines for star alleles:',starAllelesListTwoBasic[0],starAllelesListTwoBasic[1]
		for dosingGuidelinesJsonFile in os.listdir('/Users/admin/Dropbox/Privat/00_Masterthesis/pharmGkb_resources/dosingGuidelines.json/'):
			if dosingGuidelinesJsonFile.endswith('.json'):
				if 'CPIC' in dosingGuidelinesJsonFile:
					if geneSymbolName in dosingGuidelinesJsonFile:
						guidesPresentBool = printDosingGuidelineFromJsonFile(dosingGuidelinesJsonFile, starAllelesListTwoBasic)
						searchThroughJsonfile=+1
					else:
						geneSymbolIterator+=1
				else:
					cpicIterator+=1
			else:
				jsonIterator+=1
		# print 'searched through '+str(searchThroughJsonfile)+' files, did NOT searched through '+str(jsonIterator)+' files that were NOT json, '+str(cpicIterator)+' were NOT from cpic and '+str(geneSymbolIterator)+' had the WRONG gene.'
	else:
		print 'not enough basic star alleles means no PGx evidence for this variant.'
	return guidesPresentBool

# haplottypeListComplete = getHaplotypesFromTranslationtable(rsid)
# starAllelesListTwoBasic = getBasicStarAlleles(haplottypeListComplete)
# geneSymbolName = getGeneSymbolName(rsid)
# printDosingGuideline(starAllelesListTwoBasic,geneSymbolName)

def printDosingGuidelineFromRsid(rsid):
	geneSymbolNameT = getGeneSymbolName(rsid)
	haplottypeListCompleteT = getHaplotypesFromTranslationtable(rsid)
	starAllelesListTwoBasicCombinationsT = getBasicStarAlleles(haplottypeListCompleteT)
	print 'Searching for Dosing Guidelines for all ',len(starAllelesListTwoBasicCombinationsT), 'star allele combinations.'
	guidesPresentBool = False
	for combination in starAllelesListTwoBasicCombinationsT:
		guidesPresentBool = printDosingGuideline(combination,geneSymbolNameT)
	if guidesPresentBool == False:
		print 'No dosing guidelines found'

# def printDosingGuidelineFromRsid(rsid):
# 	geneSymbolNameT = getGeneSymbolName(rsid)
# 	haplottypeListCompleteT = getHaplotypesFromTranslationtable(rsid)
# 	starAllelesListTwoBasicT = getBasicStarAlleles(haplottypeListCompleteT)
# 	printDosingGuideline(starAllelesListTwoBasicT,geneSymbolNameT)

# Check current working directory.
#print ('Current working directory is:  %s' % os.getcwd())
#print ('Changing directory')
#os.chdir('C:\\Users\\MJ\\Dropbox\\Privat\\00_Masterthesis\\python')
#print ('Current working directory is:  %s' % os.getcwd(),'\n')
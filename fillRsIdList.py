import os
from openpyxl import Workbook #2.2.3
from openpyxl import load_workbook
rsidList=[]
def getHaplotypesFromTranslationtable(translationTablePerGene):
		translationTablePerGeneWorkbook = load_workbook('/Users/admin/Dropbox/Privat/00_Masterthesis/pharmGkb_resources/'+translationTablePerGene,read_only=True)
		worksheetTranslationTablePerGene = translationTablePerGeneWorkbook.active
		for row in worksheetTranslationTablePerGene.rows:
		    for cell in row:
		    	if isinstance(cell.value,unicode): #dont parse datetime objects
			        if str(cell.value.encode('utf8','ignore')).strip().startswith('rs'): #encoding due to unicode characters, str(unicode) gives unicodeencdoerror
			        	rsidList.append(str(cell.value.encode('utf8','ignore')).strip())
		
#CYP2C19_06_11_2015.xlsx #DPYD_11_20_13.xlsx #G6PD_Variants_May_28_2014.xlsx #TPMT_01_27_2015.xlsx #UGT1A1_07_02_15_nomenclatureDB.xlsx
for translationTablePerGene in os.listdir('/Users/admin/Dropbox/Privat/00_Masterthesis/pharmGkb_resources/'):
	if translationTablePerGene.endswith('.xlsx') and not translationTablePerGene.startswith('~'): #and translationTablePerGene.startswith(geneSymbolName):
		getHaplotypesFromTranslationtable(translationTablePerGene)

with open('/Users/admin/Dropbox/Privat/00_Masterthesis/pharmGkb_resources/rsidlist.txt', 'w') as f:
	for rsid in rsidList:
		print rsid
		f.write("%s\n" % rsid)
print 'number of rs#s found: ',len(rsidList)

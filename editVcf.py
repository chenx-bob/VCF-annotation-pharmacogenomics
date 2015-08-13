import readCpic
import os
import gzip
import vcf

rsidlist = [line.strip() for line in open('/Users/admin/Dropbox/Privat/00_Masterthesis/pharmGkb_resources/rsidlist.txt', 'r')]
print 'Reading rsid list...',rsidlist[0:4],'... Found ',len(rsidlist),' rsids.'

# ftp://ftp-trace.ncbi.nih.gov/1000genomes/ftp/pilot_data/release/2010_07/trio/snps/
vcfFilePath = '/Users/admin/Documents/VCF_files/PG0001217-BLD.genome.vcf.gz'
# https://github.com/jamescasbon/PyVCF
vcf_reader = vcf.Reader(open(vcfFilePath, 'r'))
vcf_reader.infos['DRUGREC'] = vcf.parser._Info('DRUGREC', '.', 'String', 'Influences response of mentioned drugs.')
vcf_writer = vcf.Writer(open('/Users/admin/Documents/sample.vcf', 'w'), vcf_reader)
for record in vcf_reader:
	# print record.ID
	if record.ID in rsidlist:
		print '\nPGx variant found: '+record.ID+', Position='+str(record.POS)+', Chrom='+str(record.CHROM)+', REF='+record.REF+', ALT=',record.ALT[:]#,', INFO=',record.INFO
		record.INFO['DRUGREC'] = 'BadDrug!!'
		readCpic.printDosingGuidelineFromRsid(record.ID)
	vcf_writer.write_record(record)

f_in = open('/Users/admin/Documents/sample.vcf', 'rb')
f_out = gzip.open('/Users/admin/Documents/sample1.vcf.gz', 'wb')
f_out.writelines(f_in)
f_out.close()
f_in.close()
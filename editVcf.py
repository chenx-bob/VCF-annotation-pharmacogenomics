import readCpic
import os
import gzip
import vcf # https://github.com/jamescasbon/PyVCF


rsidlist = [line.strip() for line in open('rsidlist.txt', 'r')]
print 'Reading rsid list...',rsidlist[0:4],'... Found ',len(rsidlist),' rsids.'

vcfFilePath = '/Users/admin/Documents/VCF_files/sample.vcf'
vcf_reader = vcf.Reader(open(vcfFilePath, 'r'))
vcf_reader.infos['DRUGREC'] = vcf.parser._Info('DRUGREC', '.', 'String', 'Influences response of mentioned drugs.')
vcf_writer = vcf.Writer(open('/Users/admin/Documents/sample.vcf', 'w'), vcf_reader)
for record in vcf_reader:
	# print record.ID
	if record.ID in rsidlist:
		print '\nPGx variant found: '+record.ID+', Position='+str(record.POS)+', Chrom='+str(record.CHROM)+', REF='+record.REF+', ALT=',record.ALT[:]
		record.INFO['DRUG'] = readCpic.getPGxDrugFromRsid(record.ID)
		readCpic.printDosingGuidelineFromRsid(record.ID)
	vcf_writer.write_record(record)

f_in = open('/Users/admin/Documents/sample.vcf', 'rb')
f_out = gzip.open('/Users/admin/Documents/sample1.vcf.gz', 'wb')
f_out.writelines(f_in)
f_out.close()
f_in.close()

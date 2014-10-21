import vcf
import json
import yaml
from pymongo import MongoClient
import hashlib
from bson.json_util import dumps
import bson
import pymongo
import os
import sys

client = MongoClient('localhost', 27018)
db = client.variantDatabase

sampleCollection = db.samples
sampleCollection.ensure_index([('unique_sample', pymongo.ASCENDING), ('unique', True)])
commonPosts = db.variantCommon
commonPosts.ensure_index([('md5_key', pymongo.ASCENDING), ('unique', True)])
familyInfo = db.familyInfo
familyInfo.ensure_index([('family', pymongo.ASCENDING),
                         ('institute', pymongo.ASCENDING), ('unique', True)])

def runFamily(sFamily, sInstitute, fDate):
    sRes = familyInfo.find_one({'$and':
                                    [{'family': {'$eq':sFamily},
                                      'instance':{'$eq':sInstitute}}
                                     ]})
    if sRes == None or fDate >= sRes['yaml_time_stamp']: # For testing only, should be '>='
        return True
    else:
        return False

def countVariants(saSpecific):
    iCountPos = 0
    for family in saSpecific.keys():
        for entry in saSpecific[family]['samples']:
            if entry['GT'] != None and entry['GT'] != '0/0' and entry['GT'] != './.':
                iCountPos += 1
    return iCountPos

def md5It(sChr, sPos, sRef, sAlt):
    m = hashlib.md5()
    sAlt = sAlt.replace('[', '')
    sAlt = sAlt.replace(']', '')
    m.update(str(sChr) + ' ' + str(sPos) + ' ' + str(sRef) + ' ' + str(sAlt))
    md5key = m.hexdigest()
    return str(md5key)

def addMd5ToCompound(saCompounds):
    saReturn = []
    lError = False
    for sCompound in saCompounds:
        try:
            (sChr, sStart, sRef, sAltsScore) = sCompound.split('_')
        except:
            lError = True
            break
        (sAlt, sScore) = sAltsScore.split('>')

        md5key = md5It(sChr, sStart, sRef, sAlt)
        sRes = sScore + '_' + md5key
        saReturn.append(sRes)
    return lError, saReturn

def loadVariants(sVcf, sInstitute, sFamily, iSampleCount):
    try:
        sBuffer = open(sVcf, 'rU').read()
    except Exception as e:
        print "Failed to load file: " + sVcf
        print str(e)
        return False

    print "Loading variants from: " + sVcf
    sBuffer = sBuffer.replace('.refGene', '_refGene')
    sBuffer = sBuffer.replace('.ensGene', '_ensGene')
    fVcf = open(r'tmp.vcf', 'w')
    fVcf.write(sBuffer)
    fVcf.close()
    sBuffer = ""

    vcf_reader = vcf.Reader(open('tmp.vcf', 'r'))
    iCount = 0
    iCompoundErrors = 0
    for record in vcf_reader:
        md5key = md5It(str(record.CHROM), str(record.POS), str(record.REF), str(record.ALT))
        sMd5key = {'md5_key':md5key}
        tt = {}
        tt['common'] = json.loads(json.dumps(record.INFO))
        tt['derived'] = {}
        try:
            saGeneAnnotation = []
            for ga in record.INFO['GeneticRegionAnnotation']:
                saGeneAnnotation.append(ga.split(':')[1])
            tt['derived']['gene_annotation'] = saGeneAnnotation
        except Exception as e:
            print str(e)

        try:
            saFunctionalAnnotation = []
            for fa in record.INFO['MostSevereConsequence']:
                saFunctionalAnnotation.append(fa.split(':')[1])
            tt['derived']['functional_annotation'] = saFunctionalAnnotation
        except Exception as e:
            print str(e)
        try:
            sGeneticModels = record.INFO['GeneticModels']
        except:
            sGeneticModels = ""
        try:
            sCompounds = record.INFO['Compounds']
        except Exception as e:
            sCompounds = ""
        if sCompounds != "":
            (lError, sCompounds) = addMd5ToCompound(sCompounds)
            if lError:
                iCompoundErrors += 1
            del tt['common']['Compounds']

        tt['CHROM'] = record.CHROM
        tt['POS'] = record.POS
        tt['REF'] = record.REF
        tt['ALT'] = str(record.ALT)

        sNewEntry = sInstitute + '_' + sFamily
        samples = []
        for sample in record.samples:
            sData = []
            try:
                sDP = sample.data.DP
            except:
                sDP = ""
            s = {'sample':sample.sample,
                 'GT':sample.data.GT,
                 'DP':sDP,
                 'AD':sample.data.AD,
                 'GQ':sample.data.GQ,
                 'PL':sample.data.PL}
            samples.append(s)
        tt['md5_key'] = md5key
        
        try:
            # Move the Clinical_db_gene_annotation (IEM, EP) into specificVariant
            sClinical_db_gene_annotation = record.INFO['Clinical_db_gene_annotation']
            del tt['common']['Clinical_db_gene_annotation']
        except:
            sClinical_db_gene_annotation = ""

        specificVariant= {'GeneticModels':sGeneticModels,
                          'QUAL':record.QUAL,
                          'FILTER':record.FILTER,
                          'family':sFamily,
                          'institute':sInstitute,
                          'compounds':sCompounds,
                          'RankScore':record.INFO['RankScore'],
                          'samples':samples,
                          'Clinical_db_gene_annotation':sClinical_db_gene_annotation}
        del tt['common']['RankScore']
        saRes = commonPosts.find_one({'md5_key':md5key}, {'sample_specific':1, 'derived':1})
        
        if saRes == None or saRes['sample_specific'] == None:
            saSpecific = {sNewEntry:specificVariant}
        else:
            saSpecific = saRes['sample_specific']
            saSpecific[sNewEntry] = specificVariant
        iCountVariant = countVariants(saSpecific)
        tt['derived']['variant_count'] = iCountVariant
        tt['sample_specific'] = saSpecific
        commonPosts.update(sMd5key, tt, upsert=True)
        iCount += 1
        if iCount % 1000 == 0:
            if iCount % 50000 == 0:
                sys.stdout.write('|')
            elif iCount % 10000 == 0:
                sys.stdout.write('+')
            elif iCount % 5000 == 0:
                sys.stdout.write('-')
            else:
                sys.stdout.write('.')
            sys.stdout.flush()
    if iCompoundErrors > 0:
        print " Compound errors: " + str(iCompoundErrors)
    commonPosts.ensure_index([('specific.' + sNewEntry + '.RankScore', pymongo.DESCENDING)])
    return True

def updateClinDbGeneAnnotation(sInstitute, sFamily):
    sInstanceFamily = 'specific.' + sInstitute + '_' + sFamily
    saClinDbGeneAnnotation = commonPosts.distinct(sInstanceFamily + '.Clinical_db_gene_annotation')
    saGenticModels = commonPosts.distinct(sInstanceFamily + '.GeneticModels')

    saRes = familyInfo.find_one({'$and':
                                     [{'family': {'$eq':sFamily},
                                       'instance':{'$eq':sInstitute}}
                                      ]})
    saFunctionalAnnotation = commonPosts.find({"$and":[
                {sInstanceFamily + '.family':{"$eq":sFamily}},
                {sInstanceFamily + '.institute':{"$eq":sInstitute}}]}).distinct('derived.functional_annotation')

    saGeneAnnotation = commonPosts.find({"$and":[
                {sInstanceFamily + '.family':{"$eq":sFamily}},
                {sInstanceFamily + '.institute':{"$eq":sInstitute}}]}).distinct('derived.gene_annotation')

    saRes['gene_annotation'] = saGeneAnnotation
    saRes['functional_annotation'] = saFunctionalAnnotation
    saRes['genetic_models'] = saGenticModels
    saRes['clin_db_gene_annotation'] = saClinDbGeneAnnotation
    dFamilyFilter = {'family':sFamily, 'instance':sInstitute}
    familyInfo.update(dFamilyFilter, saRes)

def loadFile(sQcSampleFile, sConfigFile):
    configStream = open(sConfigFile, 'r')
    sa = yaml.load(configStream)
    for k, v in sa.iteritems():
        if type(v) == dict:
            break

    saSamples = v.keys()
    print ""
    print ""
    print "Processing: " + sQcSampleFile
    qcStream = open(sQcSampleFile, 'r')
    sa = yaml.load(qcStream)
    for k, v in sa.iteritems():
        sFamily = str(k)
        sInstitute = v[k]['instanceTag']
        saBams = []
        for sample in saSamples:
            saBams.append(v[sample]['MostCompleteBAM']['Path'])
            sUniqueSample = sInstitute + '_' + sFamily + '_' + sample
            dSample = {'unique_sample':sUniqueSample}
            dSampleData = {'unique_sample':sUniqueSample,
                           'instance':sInstitute,
                           'family':sFamily,
                           'sample':sample}
            sampleCollection.update(dSample, dSampleData, upsert=True)

        fDate = os.path.getmtime(sQcSampleFile)
        if (not runFamily(sFamily, sInstitute, fDate)) and (v[k]['AnalysisRunStatus'] != 'finished'):
            return
        try:
            sEthical = 'notApproved'
            sEthical = v[k]['researchEthicalApproval']
        except Exception as e:
            pass

        dFamilyFilter = {'family':sFamily, 'instance':sInstitute}
        dFamilyData = {'family':sFamily,
                       'instance':sInstitute,
                       'yaml_time_stamp':fDate,
                       'clin_db_gene_annotation':[],
                       'samples':saSamples,
                       'bam_files':saBams,
                       'ethical_approved':sEthical,
                       'qc_yaml_file':json.dumps(sa)}
        familyInfo.update(dFamilyFilter, dFamilyData, upsert=True)

        sRes = familyInfo.find_one({'$and':
                                        [{'family': {'$eq':sFamily},
                                          'instance':{'$eq':sInstitute}}
                                         ]})
        sClinicalVariants = str(v[k]['program']['RankVariants']['Clinical']['Path'])
        sResearchVariants = str(v[k]['program']['RankVariants']['Research']['Path'])

    iSampleCount = sampleCollection.find().count()
    lLoadResult = loadVariants(sClinicalVariants, sInstitute, sFamily, iSampleCount)
    if lLoadResult != True:
        print "Failed to load family " + sFamily
        return
    if sEthical != 'notApproved':
        print " Clinical variants loaded, loading research"
        loadVariants(sResearchVariants, sInstitute, sFamily, iSampleCount)
    else:
        print " Clinical variants loaded"
    updateClinDbGeneAnnotation(sInstitute, sFamily)

def isYaml(root, saFiles):
    fDate = None
    sSampleFile = None
    sConfigFile = None
    for sElement in saFiles:
        if sElement.endswith('~') or sElement.endswith('.bak') or \
                sElement.endswith('.uppmax') or sElement.endswith('.orig'):
            pass
        elif sElement.endswith('_qc_sampleInfo.yaml'):
            sSampleFile = root + '/' + sElement
            fDate = os.path.getmtime(sSampleFile)
        elif sElement.endswith('_config.yaml'):
            sConfigFile = root + '/' + sElement
            fDate = os.path.getmtime(sConfigFile)
    return (sSampleFile, sConfigFile)

def scanDir(sDirs):
    print "Scanning " + sDirs + " for input files"
    saFamsToAdd = []
    saFailedFamilies = []
    for root, dir, files in os.walk(sDirs):
        fSampleTime = None
        saSample = [s for s in files if "qc_sampleInfo.yaml" in s]
        saConfig = [s for s in files if "config.yaml" in s]
        try:
            saFiles = [saSample[0], saConfig[0]]
        except:
            continue
        (sSampleFile, sConfigFile) = isYaml(root, saFiles)
        if sSampleFile != None and sConfigFile != None:
            loadFile(sSampleFile, sConfigFile)

scanDir("/mnt/hds/proj/cust003/develop/exomes")
print ""

#loadFile("2_qc_sampleInfo.yaml", "2_config.yaml")
#stream = open("99_qc_sampleInfo.yaml", 'r')
#json.dumps(yaml.load(stream), indent=4)

"""
# Create an index for RankScore for every new family added
db.variantCommon.ensureIndex({'specific.CMMS_1.RankScore':-1})

# Creating a full text index for all documents:
db.variantCommon.ensureIndex(  { "$**": "text" },
                           { name: "TextIndex" } )

# Full text search:
db.variantCommon.find({$text: { $search: "NM_001168216" }})

# Find all distinct values for the Genetic_model model tag
db.variantCommon.distinct('Genetic_model')

db.variantCommon.find({'specific.CMMS_1.compounds':{$ne:""}})

db.variantCommon.find({ $and:[
{ 'specific.CMMS_1.Clinical_db_gene_annotation': { $eq: 'MIT'}},
{'specific.CMMS_1.GeneticModels': { $eq: 'AR_comp'}}]}).sort({'specific.CMMS_1.RankScore':-1})

db.variantCommon.find({'common.HGNC_symbol':{$eq:'MUC4'}})

# Clinical filter:
db.variantCommon.find({$and:[
    {$or:[{'common.1000GMAF':{$lt:0.001}},
          {'common.1000GMAF':{$eq:null}}]},
    {$or:[{"derived.functional_annotation": 'frameshift_variant'},
          {"derived.functional_annotation": 'splice_region_variant'},
          {"derived.functional_annotation": 'stop_lost'},
          {"derived.functional_annotation": 'stop_gained'}
        ]},
    {$or:[{"derived.gene_annotation": 'exonic'},
        {"derived.gene_annotation": 'splicing'}]},
          {'specific.CMMS_124.Clinical_db_gene_annotation': { $ne: 'IEM'}}
    ]},
    {'common':1,
     'sample_specific':1,
     'derived':1}).sort({'specific.CMMS_124.RankScore':-1})

# Query for compound popup:
db.variantCommon.find({'md5_key':{$in:["86db84a7a6aeabcf53a7408488bede6f",
    "196142d47dc2eb7885afc914792a496b"]}},
        {'specific.CMMS_1.samples':1, 'derived.gene_annotation':1, 'common.GeneticRegionAnnotation':1})

"""

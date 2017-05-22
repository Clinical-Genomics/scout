import re

def HGNC_chromosome_arm_notation(cytoband):
    """Determines if the varriant is on the p or q arm, and returns the derivatives
               
    Args:
        cytoband(str)
    Returns
        HGNC_cytoband(list)
    """

    A=""
    B=""
    #determine if A is on the P arm or Q arm
    if "p" in cytoband:
        A="pter"
        B="qter"
    elif "q" in cytoband:
        A="qter"
        B="pter"

    #decide if the centromere belongs ot A or B
    if "p11" in cytoband:
        A += "_cen"
    elif "q11" in cytoband:
        A="cen_"+A
    else:
        if "p" in cytoband: 
            B = "cen_"+B
        else:
            B+= "_cen"
    
    return( [A,B] )

def get_iscn(variant_obj):
    """Returns ISCN coordinates
    
    according to:http://varnomen.hgvs.org/bg-material/consultation/svd-wg004/

    Args:
        variant_obj(dict)

    Returns:
        iscn_coordinates(str)
    """

    start=variant_obj["position"]
    end=variant_obj["end"]
    chromosome=variant_obj["chromosome"]
    variant_type=variant_obj["sub_category"]
    posB = None
    #cytoband of the start/end coordinate
    cytoband_start=variant_obj['cytoband']["start"]
    cytoband_end=variant_obj['cytoband']["end"]
    #reference genome
    reference=variant_obj['reference']


    #If the variant is an interchromosomal translocation, the second chromosome and position is given on the folowing format
    # ]chr1:1231231[, if this is the case, then extract the chromosome and position. beware that : is used for <DUP:TANDEM> etc
    if ":" in variant_obj["alt"] and not ">" in variant_obj["alt"]:
        B=re.split("[],[]",variant_obj["alt"]);
        for string in B:
            if string.count(":"):
                lst=string.split(":");
                chromosomeB=lst[0]
                posB=lst[1]

    iscn_coordinates=""
    #del, dup, and inv are printed in a similar fashion
    if variant_type == "del" or variant_type == "inv" or variant_type == "dup":
        chromosome=chromosome.replace("chr","")
        iscn_coordinates="seq[{}] {}({})({}{})".format(reference,chromosome,variant_type,cytoband_start,cytoband_end)
        iscn_coordinates+="\nchr{}:g.{}_{}{}".format(chromosome,start,end,variant_type)

    #print interchromosomal translocation
    elif not chromosome == chromosomeB and posB:
        chromosome=chromosome.replace("chr","")
        chromosomeB=chromosomeB.replace("chr","")

        ter_A=HGNC_chromosome_arm_notation(cytoband_start)
        ter_B=HGNC_chromosome_arm_notation(cytoband_end)

        iscn_coordinates =  "seq[{}] t({};{})({};{})\n".format(reference,chromosome,chromosomeB,cytoband_start,cytoband_end)
        iscn_coordinates += "g.[{}:{}_{}::{}:{}_{}]\n".format(chromosome,ter_A[0],start,chromosomeB,posB,ter_B[0])
        iscn_coordinates += "g.[{}:{}_{}::{}:{}_{}]".format(chromosomeB,posB,ter_B[1],chromosome,ter_A[1],start)
    
    return(iscn_coordinates)

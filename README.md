# HALOH-LTE
This a simplified version of HALOH Toolkit, a haplotype-aware and cost-effective LOH calling solution that leverages Python and CLC Genomics Workbench. 

This tool was developed with the assumption that the experiments to obtain the LOH tracts were in a hybrid heterozygous diploid strain background SK1 and S288c. To summarize this methodology, first, we created a complete list of heterozygous single nucleotide polymorphisms (HetSNPs) in the parent strain. We validated this list by mapping reads from the fully heterozygous parent diploid to one of the haploid parents (S288c, reference genome). We then derived a list of variants shared by the two sets and removed variants present at repetitive regions of the genome to arrive at a high-confidence HetSNP list. This enabled us to generate a custom variant tract in CLC. Subsequently, we mapped WGS reads from the known LOH clones above to the reference, creating a variant list for each LOH clone. These mapping variants were interrogated against the high-confidence HetSNP variant tract. CLC provided allelic identity and frequency outputs at all HetSNP positions, which were used in a custom Python code to make haplotype-aware phased genotyping calls. 

This page will summarize how to navigate CLC Genomic Workbench and HALOH LTE User Interface to generate haplotype-aware LOH tracts. 

# USAGE
## Step 1: Running CLC Genomic Workbench Workflow called "Evaluation LOH Clone Variant"

![workflow snapshot](https://github.com/JoyLove0/LOH_Caller/assets/108104001/ba0c8a88-781f-4789-baf7-7d2ed7c3039c)

-Open CLC Genomic Workbench 
-Import Illumina
-Add Files
-Next and Save to designated folder
-Finish
-Find "Evaluation LOH Clone Variant" Workflow and Click Run
-Select Reads and transfer
-Finish

## Step 2: Running HALOH LTE User Interface

# Inputs for HALOH LTE User Interface

| Inputs            | Descriptions   |
| ----------------  | -------------- |
| wd                | This is the working directory. This will contain your input VCF/CSV Files. |
| clone_tables_list | This is the name of the txt file containing the list of clone table names. If you used the lines above this will be "Clone_Variant_Tables.txt". |
| coverage_minimum  | This must be a number with no quotesYou get to set the minimum coverage needed to reliable call region in your LOH tracks heterozygous or homozygous. If a position falls underneath this coverage, it will be marked "No Call Due to Low Coverage". Suggest to start with 25 and make this number higher to make this input more strict. | 

# Helpful Manual and Links for CLC Genomic Workbench 
The tools used in "Evaluating LOH Clone Variants" are Map Reads to Reference, Identify Known Mutations from Mapping, and Export as VCF.

For more information on each these tools, see below:

| Program       | Manuals and/or Useful Links   |
| ------------- | ------------- |
| All Manuals | https://resources.qiagenbioinformatics.com/manuals/clcgenomicsworkbench/current/index.php?manual=Introduction_CLC_Genomics_Workbench.html |
| Map Reads to Reference | https://resources.qiagenbioinformatics.com/manuals/clcgenomicsworkbench/900/index.php?manual=Map_Reads_Reference.html |
| Export in VCF | https://resources.qiagenbioinformatics.com/manuals/clcgenomicsworkbench/current/index.php?manual=Export_in_VCF_format.html |
| Identify Known Mutations from Mapping | https://resources.qiagenbioinformatics.com/manuals/clcgenomicsworkbench/950/index.php?manual=Identify_Known_Mutations_from_Sample_Mappings.html |


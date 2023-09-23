

# test code
x <- c('534')
eg <- bitr(x, fromType = 'ENTREZID', toType = c('SYMBOL','ENSEMBLPROT'), OrgDb='org.Hs.eg.db')
eg

y <- c('ENSP00000406389', 'ENSP0000534')
hh <- bitr(y, fromType = 'ENSEMBLPROT', toType = c('SYMBOL','ENTREZID'), OrgDb='org.Hs.eg.db')
hh

# real code
dataPath <- '/data/1011/ZYH/mgkg/database/STITCH/filter_human_pc.tsv'
data <- read.table(dataPath, header=T, sep='\t')
nrow(data)
library(tidyr)
library(dplyr)
data <- separate(data, protein, c(NA, 'ENSP'))
data <- data[, 1:2]
protein <- data[, 2]

# biomaRt
library('biomaRt')
listMarts()
mart <- useMart('ensembl')
dataset <- listDatasets(mart)
myDataset <- useDataset('hsapiens_gene_ensembl', mart=mart)
filterList <- listFilters(myDataset)
attribList <- listAttributes(myDataset)
entrezID <- getBM(attributes=c('ensembl_peptide_id', 'entrezgene_id'), filters=c('ensembl_peptide_id'),
                  values=protein, mart=myDataset)
entrezID.1 <- unique(entrezID)
nrow(entrezID)
nrow(entrezID.1)
nrow(entrezID[!duplicated(entrezID),])
names(entrezID.1)[1] <- 'ENSP'
names(entrezID.1)[2] <- 'entrez_id'
new_data <- merge(data, entrezID.1)
new_data <- new_data[, c('chemical', 'ENSP', 'entrez_id')]
nrow(new_data)
nrow(unique(new_data))
new_data <- new_data[, -2]
entrez <- rep('ENTREZ:', nrow(new_data))
new_data <- cbind(new_data, entrez)
new_data <- new_data[, c('chemical', 'entrez', 'entrez_id')]
new_data <- unite(new_data, 'entrez_id', 'entrez', 'entrez_id', sep='', remove=T)
nrow(unique(new_data))
write.table(new_data, '/data/1011/ZYH/mgkg/database/STITCH/cg_relation.csv',
            row.names=F, col.names=F, sep='\t', quote=F)

# clusterProfiler
# fast but not complete
library(clusterProfiler)
library("org.Hs.eg.db")
keytypes(org.Hs.eg.db)
entrezID.2 <- bitr(protein, fromType = 'ENSEMBLPROT', toType = c('ENTREZID'), OrgDb='org.Hs.eg.db')
nrow(entrezID.2)




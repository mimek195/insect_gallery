

class Entry:
    print("test")


class TaxonomicRank:
    def __init__(self, rank, rank_name, super_taxon=None, taxon_list=[]):
        taxon_rank = rank
        taxon_rank_name = rank_name
        taxon_super_taxon = super_taxon
        taxon_lower_list = taxon_list


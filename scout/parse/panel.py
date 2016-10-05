
def get_gene_panel(panel_info):
    """Parse the panel info and return a gene panel
        
        Args:
            panel_info(dict)
    
        Returns:
            gene_panel(dict)
    """
    
    gene_panel = {}
    
    gene_panel['path'] = panel_info.get('file')
    gene_panel['type'] = panel_info.get('type', 'clinical')
    gene_panel['date'] = panel_info.get('date')
    gene_panel['version'] = float(panel_info.get('version', '0'))
    gene_panel['id'] = panel_info.get('name')
    gene_panel['display_name'] = panel_info.get('full_name', panel_id)
    
    return gene_panel
    
    
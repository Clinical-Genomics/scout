from scout.models import GenePanel
    
def build_panel(panel_info, institute):
    """Build a mongoengine GenePanel
    
        Args:
            panel_info(dict): A dictionary with panel information
            institute(str)
    
        Returns:
            panel_obj(GenePanel)
    
    
    """

    panel_obj = GenePanel(
        institute=institute,
        panel_name = panel_info['id'],
        version = panel_info['version'],
        date = panel_info['date'],
    )
    panel_obj.display_name = panel_info['display_name']
    
    panel_obj.genes = panel_info['genes']
    
    return panel_obj

    
    
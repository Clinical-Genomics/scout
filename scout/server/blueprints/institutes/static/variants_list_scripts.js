$(document).ready(function() {
  $('#variants_table').DataTable( {
      paging: false,
			searching: true,
			layout: {
				topStart: 'buttons',
				topEnd: {
            search: {
                placeholder: 'Search'
            }
        }
			},
      buttons: [
          'copyHtml5',
          'excelHtml5',
      ]
  } );

  $('[data-toggle="tooltip"]').tooltip();
} );

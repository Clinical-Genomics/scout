$(document).ready(function() {
  $('#variants_table').DataTable( {
      paging: false,
      dom: 'Bfrtip',
      buttons: [
          'copyHtml5',
          'excelHtml5',
      ]
  } );

  $('[data-toggle="tooltip"]').tooltip();
} );

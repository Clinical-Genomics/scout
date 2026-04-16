$(document).ready(function() {
  $('#variants_table').DataTable({
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
          {
              text: 'Managed Variants infile',
              className: 'btn btn-primary',
              action: function () {
              		$(window).off('beforeunload');
                  window.location.href = exportAsManagedUrl;
              }
          }
      ]
  });

  $('[data-toggle="tooltip"]').tooltip();
});

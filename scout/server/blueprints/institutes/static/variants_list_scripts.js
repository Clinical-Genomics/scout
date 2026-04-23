$(document).ready(function() {
  const buttons = [
      'copyHtml5',
      'excelHtml5'
  ];

  if (isAdmin) {
      buttons.push({
          text: 'Managed Variants infile',
          className: 'btn btn-primary',
          action: function () {
              $(globalThis).off('beforeunload');
              globalThis.location.href = exportAsManagedUrl;
          }
      });
  }

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
      buttons: buttons
  });

  $('[data-toggle="tooltip"]').tooltip();
});

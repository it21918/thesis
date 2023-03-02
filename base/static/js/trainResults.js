$(document).ready(function() {
    $('#train-results-table').DataTable({
      "order": [[0, "asc"]],  // default sort by Step in ascending order
      "columnDefs": [
        { "targets": [2], "orderable": false },  // disable sorting on Validation IOU column
        { "targets": [1, 2], "searchable": true },  // enable filtering on Train Loss and Validation IOU columns
      ],
      "displayLength": 10,  // show 10 rows per page
      "lengthMenu": [10, 25, 50, 100],  // allow user to select number of rows per page
      "dom": '<"top"f>rt<"bottom"lp><"clear">',  // move search box to top
    });
  });

  $(document).ready(function() {
    $('#image-table').DataTable({
      paging: true,
      lengthMenu:[2,10,20,50,100],
      searching: false,
      ordering: false
    });
  });

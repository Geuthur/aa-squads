document.addEventListener('DOMContentLoaded', function () {
    // Initialize DataTable
    var Groups = $('#groups').DataTable({
        ajax: {
            url: '/squads/api/groups/0/',
            dataSrc: function (data) {
                return data;
            },
        },
        processing: true,
        columns: [
            {data: 'user'},
            {data: 'group'},
            {data: 'application'},
            {data: 'skills'},
            {data: 'group_id'},
        ],
        columnDefs: [
            {
                targets: 4,
                sortable: false,
                render: function (data, type, row) {
                    return '<button data-link="/approve/' + row.group_id + '/" class="btn btn-success btn-sm" title="Approve"><i class="fa-solid fa-check"></i></button> <button data-link="/decline/' + row.group_id + '/" class="btn btn-warning btn-sm" title="Decline"><i class="fa-solid fa-ban"></i></button>';
                },
            }
        ]
    });
});

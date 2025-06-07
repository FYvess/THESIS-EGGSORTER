// sidebar
const sidebarToggle = document.querySelector(".toggle-sidebar-btn");

sidebarToggle.addEventListener("click", () => {
  document.body.classList.toggle("toggle-sidebar");
});
 let minDate, maxDate;
 
// Custom filtering function which will search data in column four between two values
DataTable.ext.search.push(function (settings, data, dataIndex) {
    let min = minDate.val();
    let max = maxDate.val();
    let date = new Date(data[1]);
 
    if (
        (min === null && max === null) ||
        (min === null && date <= max) ||
        (min <= date && max === null) ||
        (min <= date && date <= max)
    ) {
        return true;
    }
    return false;
});
 
// Create date inputs
minDate = new DateTime('#min', {
    format: 'MMMM Do YYYY'
});
maxDate = new DateTime('#max', {
    format: 'MMMM Do YYYY'
});
 
// DataTables initialisation
let table = new DataTable('#datatable');
 
// Refilter the table
document.querySelectorAll('#min, #max').forEach((el) => {
    el.addEventListener('change', () => table.draw());
});
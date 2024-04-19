// function addSubject() {
//     var subjectContainer = document.querySelector('.subject-container');
//     var subjectCount = parseInt(document.getElementById('subject_count').value);

//     // Create a new subject div
//     var newSubject = document.createElement('div');
//     newSubject.className = 'subject';

//     // Update subject count
//     subjectCount += 1;
//     document.getElementById('subject_count').value = subjectCount;

//     // Add HTML for new subject with dynamically generated semester options
//     newSubject.innerHTML = `
//         <label for="subject_${subjectCount}">Subject ${subjectCount}:</label>
//         <input type="text" name="subject_${subjectCount}_name" placeholder="Enter subject">
//         <input type="number" name="subject_${subjectCount}_cia" placeholder="Enter CIA Marks">
//         <input type="number" name="subject_${subjectCount}_midsem" placeholder="Enter Midsem Marks">
//         <select name="subject_${subjectCount}_semester">
//             ${generateSemesterOptions()}
//         </select>
//     `;

//     // Append the new subject div
//     subjectContainer.appendChild(newSubject);

//     // Function to dynamically generate semester options
//     function generateSemesterOptions() {
//         var options = '';
//         for (var i = 1; i <= 6; i++) {
//             options += `<option value="Semester ${i}">Semester ${i}</option>`;
//         }
//         return options;
//     }
// }

function addSubject() {
    var subjectContainer = document.querySelector('.subject-container');
    var subjectCount = parseInt(document.getElementById('subject_count').value);

    // Create a new subject div
    var newSubject = document.createElement('div');
    newSubject.className = 'subject';

    // Update subject count
    subjectCount += 1;
    document.getElementById('subject_count').value = subjectCount;

    // Add HTML for new subject with dynamically generated semester options and delete button
    newSubject.innerHTML = `
            <label for="subject_${subjectCount}">Subject ${subjectCount}:</label>
            <input type="text" name="subject_${subjectCount}_name" placeholder="Enter subject">
            <input type="number" name="subject_${subjectCount}_cia" placeholder="Enter CIA Marks">
            <input type="number" name="subject_${subjectCount}_midsem" placeholder="Enter Midsem Marks">
            <select name="subject_${subjectCount}_semester">
                ${generateSemesterOptions()}
            </select>
            <button type="button" class="delete-button" onclick="deleteSubject(this)">Delete</button>
        `;

    // Append the new subject div
    subjectContainer.appendChild(newSubject);

    // Function to dynamically generate semester options
    function generateSemesterOptions() {
        var options = '';
        for (var i = 1; i <= 6; i++) {
            options += `<option value="Semester ${i}">Semester ${i}</option>`;
        }
        return options;
    }
}

// Function to delete the subject entry
function deleteSubject(button) {
    var subjectDiv = button.parentElement;
    subjectDiv.remove();
}

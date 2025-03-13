// Add this to static/js/script.js

document.addEventListener("DOMContentLoaded", function () {
  // Debug subject dropdowns
  const subjectDropdowns = document.querySelectorAll('select[name="subject"]');
  if (subjectDropdowns.length > 0) {
    console.log("Subject dropdowns found:", subjectDropdowns.length);

    subjectDropdowns.forEach((dropdown) => {
      console.log("Options count:", dropdown.options.length);

      // Add event listener to log selection
      dropdown.addEventListener("change", function () {
        console.log("Selected subject ID:", this.value);
        console.log(
          "Selected subject text:",
          this.options[this.selectedIndex].text
        );
      });
    });
  }

  // Ensure Bootstrap JS is properly initialized for dropdowns
  var dropdownElementList = [].slice.call(
    document.querySelectorAll(".dropdown-toggle")
  );
  var dropdownList = dropdownElementList.map(function (dropdownToggleEl) {
    return new bootstrap.Dropdown(dropdownToggleEl);
  });
});
